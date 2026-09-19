"""SysML Agent LangGraph workflow. Mirrors `SysML V2 Agent.md`, Section 27.

    START -> build_generation_contract -> create_generation_plan (LLM)
          -> map_elements (LLM) -> generate_sysml -> validate_generation
          -> passed?          --yes--> publish_version -> END
                    --no, attempts left--> repair_sysml (LLM) -> validate_generation (loop)
                    --no, attempts exhausted--> human_review (interrupt) -> publish_version -> END

Auto-repair: on a validation failure, up to `SETTINGS.max_repair_attempts`
LLM repair passes are attempted (feeding the exact structured validation
errors back to the model — see `repair/sysml_repairer.py`) before falling
back to a human review interrupt. `MAX_REPAIR_ATTEMPTS=0` disables this and
restores the original fail-straight-to-human-review behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from simulation_platform.sysml_gen.config import SETTINGS
from simulation_platform.sysml_gen.generation.sysml_generator import generate_sysml_files
from simulation_platform.sysml_gen.llm import LLMUnavailable
from simulation_platform.sysml_gen.mapping.element_mapper import map_elements
from simulation_platform.sysml_gen.planning.model_planner import create_generation_plan
from simulation_platform.sysml_gen.repair.sysml_repairer import repair_sysml_files
from simulation_platform.schemas import SysMLManifest, ValidationStatus
from simulation_platform.shared import BudgetExceeded, BudgetGuard, build_retrieval_context
from simulation_platform.sysml_gen.storage.from_document_agent import contract_from_semantic_model
from simulation_platform.sysml_gen.storage.sysml_store import (
    load_contract,
    load_generated_files,
    load_mappings,
    load_plan,
    load_validation_report,
    publish_version,
    save_contract,
    save_generated_files,
    save_manifest,
    save_mappings,
    save_plan,
    save_traceability,
    save_validation_report,
    sysml_dir,
)
from simulation_platform.sysml_gen.traceability.traceability_manager import build_traceability
from simulation_platform.sysml_gen.validation.semantic_validator import validate_semantics
from simulation_platform.sysml_gen.validation.validator import validate_generation

from .state import SysMLState


def _error_signature(result) -> str:
    """A stable fingerprint of exactly what's wrong, so the repair loop can
    tell "the same error came back" (repair isn't helping, stop early) from
    "a different error now" (still making progress, keep going)."""

    payload = json.dumps(
        {
            "syntax": [e.model_dump() for e in result.syntax_errors],
            "structural": [e.model_dump() for e in result.structural_errors],
            "coverage_missing": sorted(result.requirement_coverage.missing),
            "traceability": [e.model_dump() for e in result.traceability_errors],
            "semantic": [e.model_dump() for e in result.semantic_errors],
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_sysml_graph(document_agent_project_dir_resolver, sysml_project_dir_resolver):
    """Both resolvers are `project_id -> Path`, so this agent stays decoupled
    from where the Document Agent's projects/ or this agent's projects/ live."""

    # One guard per (project_id, generation_id): the repair loop can call
    # the LLM up to SETTINGS.max_repair_attempts times across many
    # `repair_sysml` node visits within a single `graph.invoke(...)` run,
    # and this needs to accumulate across all of them -- a fresh guard per
    # node call couldn't ever catch a cumulative overspend. Keyed rather
    # than a single shared instance so this graph object (built once, then
    # invoked repeatedly for different projects) never leaks spend between
    # unrelated generation runs.
    repair_budget_guards: dict[tuple[str, str], BudgetGuard] = {}

    def _repair_budget_guard(project_id: str, generation_id: str) -> BudgetGuard:
        key = (project_id, generation_id)
        if key not in repair_budget_guards:
            repair_budget_guards[key] = BudgetGuard(
                limit_usd=SETTINGS.repair_budget_usd,
                price_per_1k_input_usd=SETTINGS.price_per_1k_input_usd,
                price_per_1k_output_usd=SETTINGS.price_per_1k_output_usd,
                stage_name="SysML repair",
            )
        return repair_budget_guards[key]

    def build_generation_contract_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        contract = contract_from_semantic_model(document_agent_project_dir)
        save_contract(sysml_project_dir, contract)
        return {
            "entities_in_contract": len(contract.entities),
            "requirements_in_contract": len(contract.requirements),
        }

    def create_generation_plan_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        contract = load_contract(sysml_project_dir)
        plan = create_generation_plan(contract, state["generation_id"])
        if plan.open_questions:
            # Retrieve on demand (§9/§40) rather than guess or immediately
            # escalate to a human -- only kept if it actually reduces the
            # number of open questions; never regresses on the first attempt.
            document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
            context = build_retrieval_context(document_agent_project_dir, [q.question for q in plan.open_questions])
            if context:
                retried = create_generation_plan(contract, state["generation_id"], extra_context=context)
                if len(retried.open_questions) < len(plan.open_questions):
                    plan = retried
        save_plan(sysml_project_dir, plan)
        return {}

    def map_elements_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        contract = load_contract(sysml_project_dir)
        plan = load_plan(sysml_project_dir)
        mappings = map_elements(contract, plan)
        save_mappings(sysml_project_dir, mappings)
        return {"mappings_created": len(mappings)}

    def generate_sysml_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        contract = load_contract(sysml_project_dir)
        mappings = load_mappings(sysml_project_dir)
        files = generate_sysml_files(contract, mappings)
        save_generated_files(sysml_project_dir, files)

        traceability = build_traceability(state["sysml_version"], mappings)
        save_traceability(sysml_project_dir, traceability)

        manifest = SysMLManifest(
            sysml_version=state["sysml_version"],
            knowledge_version=contract.version.knowledge_version,
            files=sorted(files.keys()),
            requirement_map={m.engineering_id: m.sysml_element_name for m in mappings if m.engineering_id.startswith("REQ")},
            entity_map={m.engineering_id: m.sysml_element_name for m in mappings if m.engineering_id.startswith("ENT")},
        )
        save_manifest(sysml_project_dir, manifest)
        return {"files_generated": len(files)}

    def validate_generation_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        contract = load_contract(sysml_project_dir)
        plan = load_plan(sysml_project_dir)
        mappings = load_mappings(sysml_project_dir)
        files = load_generated_files(sysml_project_dir)

        result = validate_generation(
            state["generation_id"],
            contract,
            plan,
            mappings,
            files,
            use_real_parser=SETTINGS.use_real_syntax_parser,
            real_parser_timeout=SETTINGS.real_parser_timeout_seconds,
        )

        # `_error_signature`/`stalled` are computed from the DETERMINISTIC
        # result only, before Layer 5 (semantic, LLM) is appended below --
        # an LLM review's exact wording can vary slightly between calls
        # even at temperature=0, and folding it into the signature would
        # make "same error came back" detection unreliable. Semantic
        # issues are purely advisory (see `validator.py`'s own docstring:
        # "shouldn't block the deterministic gate") -- saved to the report
        # for a human to see, never affecting `status`/the repair loop.
        new_signature = _error_signature(result)
        stalled = (
            result.status != ValidationStatus.PASSED
            and new_signature == state.get("validation_error_signature", "")
        )

        try:
            result.semantic_errors.extend(validate_semantics(contract, files))
        except (LLMUnavailable, BudgetExceeded):
            pass  # best-effort -- no key, or the stage budget is already spent on more essential calls

        save_validation_report(sysml_project_dir, result)
        return {
            "validation_status": result.status.value,
            "validation_error_signature": new_signature,
            "repair_stalled": stalled,
        }

    def validation_passed(state: SysMLState) -> str:
        if state["validation_status"] == ValidationStatus.PASSED.value:
            return "publish_version"
        if state["repair_stalled"]:
            return "human_review"  # same error came back -- repair isn't helping, stop early
        if state["repair_attempt"] < SETTINGS.max_repair_attempts:
            return "repair_sysml"
        return "human_review"

    def repair_sysml_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        files = load_generated_files(sysml_project_dir)
        mappings = load_mappings(sysml_project_dir)
        validation_result = load_validation_report(sysml_project_dir)
        guard = _repair_budget_guard(state["project_id"], state["generation_id"])
        repaired_files, updated_mappings = repair_sysml_files(files, validation_result, mappings, callbacks=[guard])
        save_generated_files(sysml_project_dir, repaired_files)
        # Keeps `mappings.json` from silently drifting from the actual
        # files whenever a repair adds/renames a traceable element (see
        # `sysml_repairer.py`'s own docstring for the real gap this
        # closes) -- a no-op write when the repair only touched syntax.
        save_mappings(sysml_project_dir, updated_mappings)
        return {"repair_attempt": state["repair_attempt"] + 1}

    def human_review_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        report_path = sysml_dir(sysml_project_dir) / "validation" / "sysml_validation_report.json"
        interrupt({"validation_report_path": str(report_path)})
        return {"status": "REVIEWED"}

    def publish_version_node(state: SysMLState) -> dict:
        # See the identical fix in `modelica_gen/workflow/modelica_graph.py`'s
        # `publish_version_node` -- this used to unconditionally report
        # "READY" even when reached via an exhausted-repair human-review
        # acknowledgment where nothing was actually fixed, which
        # `pipeline.py` and `run_full_pipeline` then treated as success.
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        publish_version(sysml_project_dir, state["sysml_version"], parent=None)
        if state.get("status") == "REVIEWED":
            return {"status": "NEEDS_REVIEW"}
        return {"status": "READY"}

    graph = StateGraph(SysMLState)
    graph.add_node("build_generation_contract", build_generation_contract_node)
    graph.add_node("create_generation_plan", create_generation_plan_node)
    graph.add_node("map_elements", map_elements_node)
    graph.add_node("generate_sysml", generate_sysml_node)
    graph.add_node("validate_generation", validate_generation_node)
    graph.add_node("repair_sysml", repair_sysml_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("publish_version", publish_version_node)

    graph.add_edge(START, "build_generation_contract")
    graph.add_edge("build_generation_contract", "create_generation_plan")
    graph.add_edge("create_generation_plan", "map_elements")
    graph.add_edge("map_elements", "generate_sysml")
    graph.add_edge("generate_sysml", "validate_generation")
    graph.add_conditional_edges(
        "validate_generation",
        validation_passed,
        {"publish_version": "publish_version", "repair_sysml": "repair_sysml", "human_review": "human_review"},
    )
    graph.add_edge("repair_sysml", "validate_generation")
    graph.add_edge("human_review", "publish_version")
    graph.add_edge("publish_version", END)

    return graph
