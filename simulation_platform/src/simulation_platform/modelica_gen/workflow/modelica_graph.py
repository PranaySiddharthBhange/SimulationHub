"""Modelica Agent LangGraph workflow. Mirrors `Modelica Agent.md`, Section
30. The real compile check is best-effort (skipped, not faked, when `omc`
isn't installed) -- `validate_generation`'s Layer 6 (semantic, LLM review of
"does this actually represent the system it was supposed to", see `validate
_semantics`) is the same: best-effort, appended to the saved report for a
human to see, but never affecting `validation_status`/the repair loop.

    START -> build_generation_contract -> analyze_and_compare_legacy
          -> create_modelica_plan (LLM) -> map_elements (LLM + deterministic)
          -> synthesize_state_machines (LLM) -> generate_modelica -> validate_generation
          -> passed?         --no, attempts left--> repair_modelica (LLM) -> generate_modelica (loop)
                              --no, exhausted-------> human_review (interrupt) -> publish_version -> END
                    --yes-> compile_check (real omc, best-effort)
                              -> compiled or skipped?     -> publish_version -> END
                              -> failed, attempts left    -> repair_modelica (LLM) -> generate_modelica (loop)
                              -> failed, exhausted         -> human_review (interrupt) -> publish_version -> END

Auto-repair fixes the MAPPINGS (see `repair/modelica_repairer.py`), not raw
.mo text, since files are always deterministically regenerated from
mappings — a fix has to re-enter at `generate_modelica` to survive that.
`MAX_REPAIR_ATTEMPTS=0` disables this and restores the original
fail-straight-to-human-review behavior.
"""

from __future__ import annotations

import hashlib
import json

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from simulation_platform.modelica_gen.analysis import analyze_legacy_file, analyze_sysml_files
from simulation_platform.compiler import CompilerUnavailable, compile_files
from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.generation import generate_modelica_files
from simulation_platform.modelica_gen.legacy import compare_legacy_models
from simulation_platform.modelica_gen.llm import LLMUnavailable
from simulation_platform.modelica_gen.mapping import (
    map_connectors,
    map_elements,
    map_properties,
    suggest_parameter_values,
    synthesize_state_machines,
)
from simulation_platform.modelica_gen.planning import create_modelica_plan
from simulation_platform.modelica_gen.repair import repair_modelica_mappings
from simulation_platform.schemas import ModelicaManifest
from simulation_platform.shared import (
    BudgetExceeded,
    BudgetGuard,
    build_retrieval_context,
    derive_simulation_window,
    evaluate_simulation_result,
)
from simulation_platform.modelica_gen.storage import build_upstream_bundle, requirement_bounds
from simulation_platform.modelica_gen.storage.modelica_store import (
    load_command_overrides,
    load_compile_result,
    load_contract,
    load_legacy_comparisons,
    load_mappings,
    load_plan,
    load_result_validation_report,
    load_state_machines,
    load_validation_report,
    modelica_dir,
    publish_version,
    save_command_overrides,
    save_compile_result,
    save_contract,
    save_generated_files,
    save_legacy_comparisons,
    save_manifest,
    save_mappings,
    save_plan,
    save_result_validation_report,
    save_state_machines,
    save_traceability,
    save_validation_report,
)
from simulation_platform.modelica_gen.traceability import build_traceability
from simulation_platform.modelica_gen.validation import validate_generation, validate_semantics

from .state import ModelicaState


def _validation_signature(result) -> str:
    """A stable fingerprint of exactly what's wrong, so the repair loop can
    tell "the same error came back" (repair isn't helping, stop early) from
    "a different error now" (still making progress, keep going)."""

    payload = json.dumps([i.model_dump() for i in result.issues], sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compile_signature(result) -> str:
    payload = json.dumps([e.model_dump() for e in result.errors], sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _result_validation_signature(report: dict) -> str:
    """Same "did repair actually change anything" fingerprint as
    `_compile_signature`, but for a physically-wrong-trajectory report --
    a compile that keeps PASSING with the exact same out-of-bound/NaN
    issues every retry is just as stalled as one that keeps failing to
    compile, and must stop auto-repair the same way."""

    payload = json.dumps(report.get("issues", []), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_modelica_graph(
    document_agent_project_dir_resolver, sysml_project_dir_resolver, modelica_project_dir_resolver
):
    """Three resolvers (`project_id -> Path` each), so this agent stays as
    decoupled from the other two as it would be as a separate service --
    identical call already made once for the SysML Agent's own two-resolver
    `build_sysml_graph`."""

    # See `sysml_gen/workflow/sysml_graph.py`'s identical guard for why this
    # is keyed per (project_id, generation_id) rather than one shared
    # instance or a fresh one per node call.
    repair_budget_guards: dict[tuple[str, str], BudgetGuard] = {}

    def _repair_budget_guard(project_id: str, generation_id: str) -> BudgetGuard:
        key = (project_id, generation_id)
        if key not in repair_budget_guards:
            repair_budget_guards[key] = BudgetGuard(
                limit_usd=SETTINGS.repair_budget_usd,
                price_per_1k_input_usd=SETTINGS.price_per_1k_input_usd,
                price_per_1k_output_usd=SETTINGS.price_per_1k_output_usd,
                stage_name="Modelica repair",
            )
        return repair_budget_guards[key]

    def build_generation_contract_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        save_contract(modelica_project_dir, bundle.contract)
        return {
            "components_in_contract": len(bundle.contract.components),
            "properties_in_contract": len(bundle.contract.properties),
            "legacy_files_found": len(bundle.contract.legacy_models),
        }

    def analyze_and_compare_legacy_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        sysml_semantic_model = analyze_sysml_files(bundle.sysml_generated_files)
        legacy_models = [analyze_legacy_file(name, text) for name, text in bundle.legacy_files.items()]
        bounds = requirement_bounds(bundle.sysml_contract_raw)
        comparisons = compare_legacy_models(
            sysml_semantic_model.parts, legacy_models, bounds, bundle.engineering_id_by_sysml_element_name()
        )
        save_legacy_comparisons(modelica_project_dir, comparisons)
        return {"legacy_comparisons_found": len(comparisons)}

    def create_modelica_plan_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        contract = load_contract(modelica_project_dir)
        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        sysml_semantic_model = analyze_sysml_files(bundle.sysml_generated_files)
        comparisons = load_legacy_comparisons(modelica_project_dir)

        plan = create_modelica_plan(
            contract, state["generation_id"], sysml_semantic_model, comparisons,
            sysml_contract_raw=bundle.sysml_contract_raw,
        )
        if plan.open_questions:
            # Retrieve on demand (§9/§40) rather than guess or immediately
            # escalate to a human -- only kept if it actually reduces the
            # number of open questions; never regresses on the first attempt.
            context = build_retrieval_context(document_agent_project_dir, [q.question for q in plan.open_questions])
            if context:
                retried = create_modelica_plan(
                    contract, state["generation_id"], sysml_semantic_model, comparisons, extra_context=context,
                    sysml_contract_raw=bundle.sysml_contract_raw,
                )
                if len(retried.open_questions) < len(plan.open_questions):
                    plan = retried
        save_plan(modelica_project_dir, plan)
        return {}

    def map_elements_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        contract = load_contract(modelica_project_dir)
        plan = load_plan(modelica_project_dir)
        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        comparisons = load_legacy_comparisons(modelica_project_dir)

        mappings = []
        mappings.extend(map_properties(plan.properties, bundle.sysml_contract_raw))
        mappings.extend(map_connectors(contract.interfaces, bundle.sysml_contract_raw))
        mappings.extend(map_elements(contract, plan, bundle.sysml_contract_raw, comparisons))

        save_mappings(modelica_project_dir, mappings)
        return {"mappings_created": len(mappings)}

    def synthesize_state_machines_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        legacy_models = [analyze_legacy_file(name, text) for name, text in bundle.legacy_files.items()]

        # Composes the already-extracted behaviors into a real state machine
        # for any never-assigned legacy sequencer variable (e.g. `discrete
        # StepState seq`) -- a no-op (empty list) when there's no such
        # variable, or no behaviors that clearly describe its sequence (see
        # `mapping/state_machine_synthesizer.py`).
        state_machines = synthesize_state_machines(legacy_models, bundle.sysml_contract_raw)
        save_state_machines(modelica_project_dir, state_machines)
        return {"state_machines_synthesized": len(state_machines)}

    def generate_modelica_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        contract = load_contract(modelica_project_dir)
        mappings = load_mappings(modelica_project_dir)
        comparisons = load_legacy_comparisons(modelica_project_dir)
        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        sysml_semantic_model = analyze_sysml_files(bundle.sysml_generated_files)
        legacy_models = [analyze_legacy_file(name, text) for name, text in bundle.legacy_files.items()]

        # Every value this pipeline could not derive on its own -- a
        # never-assigned legacy variable, a generic library placeholder, a
        # parameter with no requirement bound, or a from-scratch stub's
        # sensed field (`new direction.txt` §15: propose, explain why, ask,
        # only then treat as final -- never bake in a placeholder
        # unconfirmed). Already-confirmed answers from an earlier run are
        # applied immediately, with no re-prompt; anything new the first
        # pass finds is first refined by an LLM call that grounds the
        # suggestion in the actual project documents (see `mapping/
        # parameter_value_suggester.py` -- skips anything already marked
        # `grounded`, e.g. a real scheduled-command pulse), THEN raised to
        # a human via the same shared interrupt mechanism every other
        # stage uses.
        command_overrides = load_command_overrides(modelica_project_dir)
        state_machines = load_state_machines(modelica_project_dir)
        pending_decisions: list[dict] = []
        files, entry_class, class_names, _declared_instances = generate_modelica_files(
            contract.project_id, mappings, comparisons, legacy_models, sysml_semantic_model, bundle.sysml_contract_raw,
            bundle.engineering_id_by_sysml_element_name(),
            command_overrides=command_overrides, pending_decisions=pending_decisions, state_machines=state_machines,
        )
        if pending_decisions:
            pending_decisions = suggest_parameter_values(
                pending_decisions, bundle.sysml_contract_raw, bundle.legacy_files, comparisons,
            )
            answers = interrupt({"pending_value_decisions": pending_decisions})
            for decision, answer in zip(pending_decisions, answers if isinstance(answers, list) else [answers] * len(pending_decisions)):
                if answer:
                    command_overrides[decision["variable"]] = answer if isinstance(answer, str) else decision["suggested_value"]
            save_command_overrides(modelica_project_dir, command_overrides)
            files, entry_class, class_names, _declared_instances = generate_modelica_files(
                contract.project_id, mappings, comparisons, legacy_models, sysml_semantic_model,
                bundle.sysml_contract_raw, bundle.engineering_id_by_sysml_element_name(),
                command_overrides=command_overrides, state_machines=state_machines,
            )
        save_generated_files(modelica_project_dir, files)

        sysml_element_names_by_id = {
            e["id"]: e["name"] for e in bundle.sysml_contract_raw.get("entities", [])
        } | {
            r["id"]: r.get("subject", r["id"]) for r in bundle.sysml_contract_raw.get("requirements", [])
        }
        traceability = build_traceability(
            state["modelica_version"], contract.version.sysml_version or "", contract.version.knowledge_version,
            mappings, entry_class, sysml_element_names_by_id,
        )
        save_traceability(modelica_project_dir, traceability)

        manifest = ModelicaManifest(
            modelica_version=state["modelica_version"],
            sysml_version=contract.version.sysml_version or "",
            knowledge_version=contract.version.knowledge_version,
            entry_class=entry_class,
            classes=class_names,
            files=sorted(files.keys()),
        )
        save_manifest(modelica_project_dir, manifest)
        return {"files_generated": len(files)}

    def validate_generation_node(state: ModelicaState) -> dict:
        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        contract = load_contract(modelica_project_dir)
        mappings = load_mappings(modelica_project_dir)
        comparisons = load_legacy_comparisons(modelica_project_dir)
        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        sysml_semantic_model = analyze_sysml_files(bundle.sysml_generated_files)
        legacy_models = [analyze_legacy_file(name, text) for name, text in bundle.legacy_files.items()]

        # Deterministic pure function -- recomputing it here (rather than
        # reloading from disk) guarantees the class_names/declared_instance_names
        # this validator needs are exactly consistent with what generate_modelica_node
        # wrote, with no risk of the two ever drifting apart.
        files, entry_class, class_names, _declared_instances = generate_modelica_files(
            contract.project_id, mappings, comparisons, legacy_models, sysml_semantic_model, bundle.sysml_contract_raw,
            bundle.engineering_id_by_sysml_element_name(), state_machines=load_state_machines(modelica_project_dir),
        )

        component_mappings = [m for m in mappings if m.mapping_type.value in ("MODEL", "BLOCK", "LIBRARY_COMPONENT")]
        bounds = requirement_bounds(bundle.sysml_contract_raw)

        result = validate_generation(
            state["modelica_version"], files, class_names,
            bundle.sysml_contract_raw.get("interfaces", []), component_mappings, bounds, entry_class,
        )

        # `_validation_signature`/`stalled` are computed from the
        # DETERMINISTIC result only, before Layer 6 (semantic, LLM) is
        # appended below -- an LLM review's exact wording can vary
        # slightly between calls even at temperature=0, and folding it
        # into the signature would make "same error came back" detection
        # unreliable. Semantic issues are purely advisory (see `validator
        # .py`'s own docstring: "shouldn't block the deterministic gate")
        # -- saved to the report for a human to see, never affecting
        # `status`/the repair loop.
        new_signature = _validation_signature(result)
        stalled = result.status.value != "PASSED" and new_signature == state.get("validation_error_signature", "")

        try:
            result.issues.extend(validate_semantics(bundle.sysml_contract_raw, files))
        except (LLMUnavailable, BudgetExceeded):
            pass  # best-effort -- no key, or the stage budget is already spent on more essential calls

        save_validation_report(modelica_project_dir, result)
        return {
            "validation_status": result.status.value,
            "validation_error_signature": new_signature,
            "repair_stalled": stalled,
        }

    def validation_passed(state: ModelicaState) -> str:
        if state["validation_status"] == "PASSED":
            return "compile_check"
        if state["repair_stalled"]:
            return "human_review"  # same error came back -- repair isn't helping, stop early
        if state["repair_attempt"] < SETTINGS.max_repair_attempts:
            return "repair_modelica"
        return "human_review"

    def compile_check_node(state: ModelicaState) -> dict:
        if not SETTINGS.use_real_compiler:
            return {"compile_status": "SKIPPED"}

        document_agent_project_dir = document_agent_project_dir_resolver(state["project_id"])
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])

        contract = load_contract(modelica_project_dir)
        mappings = load_mappings(modelica_project_dir)
        comparisons = load_legacy_comparisons(modelica_project_dir)
        bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
        sysml_semantic_model = analyze_sysml_files(bundle.sysml_generated_files)
        legacy_models = [analyze_legacy_file(name, text) for name, text in bundle.legacy_files.items()]

        files, entry_class, _class_names, _declared_instances = generate_modelica_files(
            contract.project_id, mappings, comparisons, legacy_models, sysml_semantic_model, bundle.sysml_contract_raw,
            bundle.engineering_id_by_sysml_element_name(), state_machines=load_state_machines(modelica_project_dir),
        )

        requirements = bundle.sysml_contract_raw.get("requirements", [])
        start_time, stop_time, number_of_intervals = derive_simulation_window(requirements)

        try:
            result = compile_files(
                execution_id=state["generation_id"], files=files, entry_class=entry_class,
                timeout=SETTINGS.omc_timeout_seconds,
                start_time=start_time, stop_time=stop_time, number_of_intervals=number_of_intervals,
            )
        except CompilerUnavailable:
            return {"compile_status": "SKIPPED"}

        save_compile_result(modelica_project_dir, result)

        report = None
        if result.status.value == "PASSED" and result.result_summary:
            # "Successful compilation is not enough" (§22) -- check the
            # actual simulated trajectory against the requirements it was
            # supposed to satisfy, not just that it ran without erroring.
            report = evaluate_simulation_result(result.result_summary, requirements)
            save_result_validation_report(modelica_project_dir, report)

        new_compile_signature = _compile_signature(result)
        new_result_validation_signature = (
            _result_validation_signature(report) if report is not None
            else state.get("result_validation_error_signature", "")
        )
        result_flagged = report is not None and report["status"] == "FLAGGED"
        stalled = (
            (result.status.value == "FAILED" and new_compile_signature == state.get("compile_error_signature", ""))
            or (result_flagged and new_result_validation_signature == state.get("result_validation_error_signature", ""))
        )
        return {
            "compile_status": result.status.value,
            "compile_error_signature": new_compile_signature,
            "result_validation_status": report["status"] if report is not None else "",
            "result_validation_error_signature": new_result_validation_signature,
            "repair_stalled": stalled,
        }

    def compile_passed(state: ModelicaState) -> str:
        # A run that compiles fine but produces a physically-wrong
        # trajectory (e.g. tank levels that never move) is just as broken
        # as one that fails to compile -- "successful compilation is not
        # enough" (§22) has to actually gate the repair loop, not just get
        # reported into a file nobody reads until a human looks for it.
        if state["compile_status"] != "FAILED" and state.get("result_validation_status") != "FLAGGED":
            return "publish_version"
        if state["repair_stalled"]:
            return "human_review"  # same error came back -- repair isn't helping, stop early
        if state["repair_attempt"] < SETTINGS.max_repair_attempts:
            return "repair_modelica"
        return "human_review"

    def repair_modelica_node(state: ModelicaState) -> dict:
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])
        mappings = load_mappings(modelica_project_dir)
        # Whichever of these is present depends on which check tripped (a
        # compile failure only happens after validation already passed, and
        # a result-validation report only exists once compile itself
        # PASSED), so there is never a stale failing report to confuse this.
        validation_result = load_validation_report(modelica_project_dir) if state["validation_status"] != "PASSED" else None
        compile_result = load_compile_result(modelica_project_dir) if state["compile_status"] == "FAILED" else None
        result_validation_report = (
            load_result_validation_report(modelica_project_dir)
            if state.get("result_validation_status") == "FLAGGED"
            else None
        )
        guard = _repair_budget_guard(state["project_id"], state["generation_id"])
        repaired_mappings = repair_modelica_mappings(
            mappings, validation_result, compile_result, result_validation_report, callbacks=[guard]
        )
        save_mappings(modelica_project_dir, repaired_mappings)
        return {"repair_attempt": state["repair_attempt"] + 1}

    def human_review_node(state: ModelicaState) -> dict:
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])
        report_path = modelica_dir(modelica_project_dir) / "validation" / "modelica_validation_report.json"
        interrupt({"validation_report_path": str(report_path), "compile_status": state.get("compile_status")})
        return {"status": "REVIEWED"}

    def publish_version_node(state: ModelicaState) -> dict:
        # Found live: this used to unconditionally return {"status":
        # "READY"} regardless of how this node was reached -- so a run that
        # exhausted auto-repair with a genuinely unfixed validation/compile
        # failure, where a human only pressed Enter to ACKNOWLEDGE the
        # report (nothing was actually fixed), still reported "READY" to
        # `pipeline.py` (`"completed" if status == "READY" else "failed"`),
        # which `run_full_pipeline` then treated as a successful run. The
        # real failure was still visible in `compile_status`/
        # `result_validation` elsewhere, but the stage-level status/✓
        # checkmark actively lied. `publish_version` itself still runs
        # either way -- the generated files/version are real artifacts
        # worth recording for inspection even when they don't pass.
        modelica_project_dir = modelica_project_dir_resolver(state["project_id"])
        publish_version(modelica_project_dir, state["modelica_version"], parent=None)
        if state.get("status") == "REVIEWED":
            return {"status": "NEEDS_REVIEW"}
        return {"status": "READY"}

    graph = StateGraph(ModelicaState)
    graph.add_node("build_generation_contract", build_generation_contract_node)
    graph.add_node("analyze_and_compare_legacy", analyze_and_compare_legacy_node)
    graph.add_node("create_modelica_plan", create_modelica_plan_node)
    graph.add_node("map_elements", map_elements_node)
    graph.add_node("synthesize_state_machines", synthesize_state_machines_node)
    graph.add_node("generate_modelica", generate_modelica_node)
    graph.add_node("validate_generation", validate_generation_node)
    graph.add_node("compile_check", compile_check_node)
    graph.add_node("repair_modelica", repair_modelica_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("publish_version", publish_version_node)

    graph.add_edge(START, "build_generation_contract")
    graph.add_edge("build_generation_contract", "analyze_and_compare_legacy")
    graph.add_edge("analyze_and_compare_legacy", "create_modelica_plan")
    graph.add_edge("create_modelica_plan", "map_elements")
    graph.add_edge("map_elements", "synthesize_state_machines")
    graph.add_edge("synthesize_state_machines", "generate_modelica")
    graph.add_edge("generate_modelica", "validate_generation")
    graph.add_conditional_edges(
        "validate_generation",
        validation_passed,
        {"compile_check": "compile_check", "repair_modelica": "repair_modelica", "human_review": "human_review"},
    )
    graph.add_conditional_edges(
        "compile_check",
        compile_passed,
        {"publish_version": "publish_version", "repair_modelica": "repair_modelica", "human_review": "human_review"},
    )
    graph.add_edge("repair_modelica", "generate_modelica")
    graph.add_edge("human_review", "publish_version")
    graph.add_edge("publish_version", END)

    return graph
