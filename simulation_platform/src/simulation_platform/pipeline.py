"""ONE pipeline, three independently-executable stages. See
`new direction.txt` §1-3: `run_full_pipeline()` is a thin wrapper calling
`execute_stage_1/2/3` in sequence -- it has no logic of its own, so the
individual-stage CLI commands and the `run` command can never drift apart.

All three stages are pointed at the SAME `project_dir` for one
`project_id` (via `Workspace`, see `workspace.py`) -- the "ONE PROJECT, ONE
WORKSPACE" requirement (§5) is met here, by resolver wiring, not by
renaming any stage's own subfolder.

Human-in-the-loop (§14): every stage's graph already raises a real
LangGraph `interrupt()` when it needs the user (Stage 1 for high-impact
ambiguities, Stage 2/3 for a validation/compile failure that exhausted
auto-repair). `on_interrupt(payload) -> answer` is the ONE shared
interaction hook every stage calls through -- the CLI supplies a real
interactive implementation (`cli.py`); a test can supply a canned one.

Resuming ACROSS process runs (not just within one, mid-interrupt) is a
real, wired-in feature (`_execute_graph_stage`), not just each stage's own
on-disk artifacts: a SQLite-backed checkpointer (`Workspace.
checkpoint_db_path`) persists every completed node's state, so a crash or
a `BudgetGuard` cutoff mid-graph can be resumed from its last checkpoint on
a later call for the SAME input, instead of re-running (and re-paying for)
every LLM call that already succeeded.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from simulation_platform.config import SETTINGS
from simulation_platform.extraction.storage.artifacts import load_semantic_model
from simulation_platform.extraction.storage.project_store import ProjectStore
from simulation_platform.extraction.workflows.ingestion_graph import build_ingestion_graph
from simulation_platform.modelica_gen.storage.modelica_store import (
    load_compile_result,
    load_result_validation_report,
)
from simulation_platform.modelica_gen.storage.modelica_store import load_manifest as load_modelica_manifest
from simulation_platform.modelica_gen.workflow.modelica_graph import build_modelica_graph
from simulation_platform.shared import BudgetGuard, apply_stage1, apply_stage2, apply_stage3
from simulation_platform.sysml_gen.storage.sysml_store import load_mappings, load_plan
from simulation_platform.sysml_gen.workflow.sysml_graph import build_sysml_graph
from simulation_platform.workspace import Workspace, compute_hash

OnInterrupt = Callable[[dict], object]


def _no_interrupt_handler(payload: dict) -> object:
    raise RuntimeError(
        f"Stage paused for human input but no interrupt handler was supplied: {payload}. "
        "Pass on_interrupt=... (the CLI does this automatically)."
    )


@dataclass
class StageResult:
    stage: str
    project_id: str
    status: str  # whatever the stage's own final `status` field says (READY/FAILED/...)
    details: dict


def workspace(projects_root: Path | None = None) -> Workspace:
    """`projects_root` overrides `SETTINGS.projects_root` -- mainly so tests
    can point this at a `tmp_path` without needing to fight the fact that
    `simulation_platform.config.SETTINGS` is a module-level singleton
    computed once at import (same reason other stages' `Settings.load()`
    were fixed to read live; this is the equivalent fix for the pipeline's
    own use of it)."""

    return Workspace(projects_root or SETTINGS.projects_root)


def _thread_id(project_id: str, stage: str) -> str:
    return f"{project_id}:{stage}"


def _execute_graph_stage(
    ws: Workspace,
    project_id: str,
    stage_key: str,
    thread_id: str,
    graph,
    initial_state: dict,
    guard: BudgetGuard,
    on_interrupt: OnInterrupt,
    input_hash: str,
    force: bool,
) -> dict:
    """Runs `graph` to completion (through any interrupts), checkpointing to
    a real, cross-process-persistent SQLite file (`Workspace.
    checkpoint_db_path`) instead of LangGraph's default in-memory
    checkpointer -- found live: a mid-run `BudgetGuard` cutoff (or any other
    crash) raises straight out of `compiled.invoke(...)`, and with only an
    in-memory checkpointer, a LATER retry had no way to know the graph had
    already gotten partway through, so it re-ran (and re-paid for) every
    LLM call that had already succeeded before the cutoff.

    `status="in_progress"` is written to `state.json` right before invoking
    -- the caller overwrites it with "completed"/"failed" right after this
    function returns. If THIS EXACT call is a retry of an attempt that left
    that "in_progress" marker behind (never got to that final overwrite) for
    the SAME
    `input_hash`, the graph's own last checkpoint is resumed from (`invoke
    (None, ...)`) instead of restarted. Any other case (first attempt,
    input changed since the abandoned attempt, or `force=True`) discards
    whatever checkpoint might exist for this thread first -- resuming into
    a checkpoint from different input, or forcing a "fresh" run that
    silently continues stale state, would both be worse than just
    recomputing everything.
    """

    previous = getattr(ws.load_state(project_id), stage_key)
    resume = not force and previous.status == "in_progress" and previous.input_hash == input_hash
    ws.mark_stage(project_id, stage_key, "in_progress", input_hash=input_hash)

    db_path = ws.checkpoint_db_path(project_id)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        checkpointer.setup()
        compiled = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}, "callbacks": [guard]}

        if resume and compiled.get_state(config).values:
            result = compiled.invoke(None, config=config)
        else:
            checkpointer.delete_thread(thread_id)
            result = compiled.invoke(initial_state, config=config)
        while "__interrupt__" in result:
            payload = result["__interrupt__"][0].value
            answer = on_interrupt(payload)
            result = compiled.invoke(Command(resume=answer), config=config)

    return result


def _stage_budget_guard(limit_usd: float, price_in: float, price_out: float, stage_name: str) -> BudgetGuard:
    return BudgetGuard(limit_usd=limit_usd, price_per_1k_input_usd=price_in, price_per_1k_output_usd=price_out, stage_name=stage_name)


# ---------------------------------------------------------------------------
# Stage 1 -- Document Indexing
# ---------------------------------------------------------------------------


def execute_stage_1(
    project_id: str,
    problem_path: Path | None = None,
    docs_dir: Path | None = None,
    on_interrupt: OnInterrupt = _no_interrupt_handler,
    force: bool = False,
    projects_root: Path | None = None,
) -> StageResult:
    ws = workspace(projects_root)
    store = ProjectStore(ws.projects_root)
    project_dir = ws.project_dir(project_id)

    if docs_dir is not None:
        store.create_project(project_id, project_id, docs_dir)
    elif not project_dir.exists():
        raise FileNotFoundError(
            f"Project {project_id!r} does not exist yet and no --docs was given to create it."
        )

    if problem_path is not None:
        shutil.copy2(problem_path, ws.problem_path(project_id))
        # Also drop it into documents/ so the existing extraction pipeline
        # picks it up like any other engineering document -- no extraction
        # code needs to change for "the problem statement is also a document".
        dest = ws.documents_dir(project_id) / problem_path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(problem_path, dest)

    ws.ensure_layout(project_id)

    # Stale-artifact handling (§31): skip a rerun when the input hasn't
    # actually changed since the last completed run, unless `force`. This
    # is content-based (compute_hash), not a timestamp check, and cascades
    # naturally through the pipeline -- Stage 2/3's own input hashes are
    # computed from the PRECEDING stage's output, so a real Stage 1 change
    # changes Stage 1's output, which changes Stage 2's input hash too.
    input_hash = compute_hash(ws.documents_dir(project_id), ws.problem_path(project_id))
    previous = ws.load_state(project_id).stage_1
    if not force and previous.status == "completed" and previous.input_hash == input_hash:
        return StageResult(
            stage="stage_1", project_id=project_id, status="READY",
            details={"skipped": True, "reason": "input unchanged since last completed run"},
        )

    guard = _stage_budget_guard(
        SETTINGS.stage1_budget_usd, SETTINGS.price_per_1k_input_usd, SETTINGS.price_per_1k_output_usd, "Stage 1"
    )
    graph = build_ingestion_graph(store)
    initial_state = {
        "project_id": project_id,
        "source_dir": str(store.source_original_dir(project_id)),
        "files_discovered": 0, "files_parsed": 0, "files_failed": 0,
        "observations_created": 0,
        "entities_found": 0, "relationships_found": 0, "requirements_found": 0,
        "behaviors_found": 0, "constraints_found": 0,
        "conflicts": 0, "ambiguities": 0, "unknowns": 0, "assumptions": 0, "topology_discrepancies": 0,
        "model_version": "", "status": "INGESTING", "errors": [],
    }
    result = _execute_graph_stage(
        ws, project_id, "stage_1", _thread_id(project_id, "stage1"), graph, initial_state, guard, on_interrupt,
        input_hash, force,
    )

    semantic_model = load_semantic_model(project_dir)
    if semantic_model is not None:
        apply_stage1(ws.system_model_path(project_id), project_id, semantic_model)

    status = result.get("status", "UNKNOWN")
    ws.mark_stage(project_id, "stage_1", "completed" if status == "READY" else "failed", input_hash=input_hash)
    return StageResult(stage="stage_1", project_id=project_id, status=status, details=result)


# ---------------------------------------------------------------------------
# Stage 2 -- SysML v2 Generation
# ---------------------------------------------------------------------------


def execute_stage_2(
    project_id: str,
    on_interrupt: OnInterrupt = _no_interrupt_handler,
    force: bool = False,
    projects_root: Path | None = None,
) -> StageResult:
    ws = workspace(projects_root)

    def resolver(pid: str) -> Path:
        return ws.project_dir(pid)

    # See execute_stage_1's identical check -- Stage 2's input is Stage 1's
    # OUTPUT, so this hash changes automatically whenever Stage 1 actually
    # reran with different results, cascading staleness detection through
    # the pipeline without Stage 2 needing to know anything about Stage 1's
    # own inputs.
    input_hash = compute_hash(ws.extracted_dir(project_id) / "project_knowledge.json")
    previous = ws.load_state(project_id).stage_2
    if not force and previous.status == "completed" and previous.input_hash == input_hash:
        return StageResult(
            stage="stage_2", project_id=project_id, status="READY",
            details={"skipped": True, "reason": "input unchanged since last completed run"},
        )

    guard = _stage_budget_guard(
        SETTINGS.stage2_budget_usd, SETTINGS.price_per_1k_input_usd, SETTINGS.price_per_1k_output_usd, "Stage 2"
    )
    graph = build_sysml_graph(resolver, resolver)
    initial_state = {
        "project_id": project_id, "generation_id": "gen_0001",
        "entities_in_contract": 0, "requirements_in_contract": 0,
        "mappings_created": 0, "files_generated": 0,
        "validation_status": "", "repair_attempt": 0,
        "validation_error_signature": "", "repair_stalled": False,
        "sysml_version": "v0001", "status": "PENDING",
    }
    result = _execute_graph_stage(
        ws, project_id, "stage_2", _thread_id(project_id, "stage2"), graph, initial_state, guard, on_interrupt,
        input_hash, force,
    )

    project_dir = ws.project_dir(project_id)
    mappings = load_mappings(project_dir)
    if mappings:
        # `load_plan` raises if the file's missing -- only call it once we
        # know mappings exist, which means the plan step already succeeded.
        plan = load_plan(project_dir)
        apply_stage2(ws.system_model_path(project_id), project_id, "v0001", plan, mappings)

    status = result.get("status", "UNKNOWN")
    ws.mark_stage(project_id, "stage_2", "completed" if status == "READY" else "failed", input_hash=input_hash)
    return StageResult(stage="stage_2", project_id=project_id, status=status, details=result)


# ---------------------------------------------------------------------------
# Stage 3 -- Modelica Generation + Simulation + Result Validation
# ---------------------------------------------------------------------------


def execute_stage_3(
    project_id: str,
    on_interrupt: OnInterrupt = _no_interrupt_handler,
    force: bool = False,
    projects_root: Path | None = None,
) -> StageResult:
    ws = workspace(projects_root)

    def resolver(pid: str) -> Path:
        return ws.project_dir(pid)

    # See execute_stage_1's identical check -- Stage 3's input is Stage 2's
    # OUTPUT (the generated SysML files).
    input_hash = compute_hash(ws.sysml_dir(project_id) / "generated")
    previous = ws.load_state(project_id).stage_3
    if not force and previous.status == "completed" and previous.input_hash == input_hash:
        return StageResult(
            stage="stage_3", project_id=project_id, status="READY",
            details={"skipped": True, "reason": "input unchanged since last completed run"},
        )

    guard = _stage_budget_guard(
        SETTINGS.stage3_budget_usd, SETTINGS.price_per_1k_input_usd, SETTINGS.price_per_1k_output_usd, "Stage 3"
    )
    graph = build_modelica_graph(resolver, resolver, resolver)
    initial_state = {
        "project_id": project_id, "generation_id": "gen_0001", "modelica_version": "v0001",
        "components_in_contract": 0, "properties_in_contract": 0,
        "legacy_files_found": 0, "legacy_comparisons_found": 0,
        "mappings_created": 0, "files_generated": 0,
        "validation_status": "", "compile_status": "", "result_validation_status": "", "repair_attempt": 0,
        "validation_error_signature": "", "compile_error_signature": "", "result_validation_error_signature": "",
        "repair_stalled": False,
        "status": "PENDING",
    }
    result = _execute_graph_stage(
        ws, project_id, "stage_3", _thread_id(project_id, "stage3"), graph, initial_state, guard, on_interrupt,
        input_hash, force,
    )

    project_dir = ws.project_dir(project_id)
    compile_result = load_compile_result(project_dir)
    if compile_result is not None:
        report = load_result_validation_report(project_dir)
        apply_stage3(ws.system_model_path(project_id), project_id, "v0001", compile_result.status.value, report)

    status = result.get("status", "UNKNOWN")
    ws.mark_stage(project_id, "stage_3", "completed" if status == "READY" else "failed", input_hash=input_hash)
    return StageResult(stage="stage_3", project_id=project_id, status=status, details=result)


# ---------------------------------------------------------------------------
# Full pipeline -- no logic of its own, just calls the three stages in order
# ---------------------------------------------------------------------------


def run_full_pipeline(
    project_id: str,
    problem_path: Path | None = None,
    docs_dir: Path | None = None,
    on_interrupt: OnInterrupt = _no_interrupt_handler,
    force: bool = False,
    projects_root: Path | None = None,
) -> list[StageResult]:
    results = [execute_stage_1(project_id, problem_path, docs_dir, on_interrupt, force=force, projects_root=projects_root)]
    if results[-1].status != "READY":
        return results
    results.append(execute_stage_2(project_id, on_interrupt, force=force, projects_root=projects_root))
    if results[-1].status != "READY":
        return results
    results.append(execute_stage_3(project_id, on_interrupt, force=force, projects_root=projects_root))
    return results


def stage_status_summary(project_id: str, projects_root: Path | None = None) -> dict:
    """Non-mutating read of where a project stands -- backs the `status`
    CLI command (§30/§32)."""

    ws = workspace(projects_root)
    state = ws.load_state(project_id)
    project_dir = ws.project_dir(project_id)
    summary = {
        "project_id": project_id,
        "stage_1": state.stage_1.model_dump(),
        "stage_2": state.stage_2.model_dump(),
        "stage_3": state.stage_3.model_dump(),
    }
    modelica_manifest_path = ws.modelica_dir(project_id) / "generated" / "modelica_manifest.json"
    if modelica_manifest_path.exists():
        try:
            summary["modelica_manifest"] = load_modelica_manifest(project_dir).model_dump()
        except OSError:
            pass

    compile_result = load_compile_result(project_dir)
    if compile_result is not None:
        summary["compile_status"] = compile_result.status.value
        summary["result_validation"] = load_result_validation_report(project_dir)

    return summary
