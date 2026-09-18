"""SysML Agent LangGraph workflow. Mirrors `SysML V2 Agent.md`, Section 27.

    START -> build_generation_contract -> create_generation_plan (LLM)
          -> map_elements (LLM) -> generate_sysml -> validate_generation
          -> passed? --yes--> publish_version -> END
                    --no ---> human_review (interrupt) -> publish_version -> END

Auto-repair (Section 19) is intentionally not wired in yet — see
`DECISIONS.md` for the scope call. On a validation failure this routes to
a human review interrupt rather than looping an LLM repair attempt.
"""

from __future__ import annotations

from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from sysml_agent.config import SETTINGS
from sysml_agent.generation.sysml_generator import generate_sysml_files
from sysml_agent.mapping.element_mapper import map_elements
from sysml_agent.planning.model_planner import create_generation_plan
from sysml_agent.schemas import SysMLManifest, ValidationStatus
from sysml_agent.storage.from_document_agent import contract_from_semantic_model
from sysml_agent.storage.sysml_store import (
    load_contract,
    load_generated_files,
    load_mappings,
    load_plan,
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
from sysml_agent.traceability.traceability_manager import build_traceability
from sysml_agent.validation.validator import validate_generation

from .state import SysMLState


def build_sysml_graph(document_agent_project_dir_resolver, sysml_project_dir_resolver):
    """Both resolvers are `project_id -> Path`, so this agent stays decoupled
    from where the Document Agent's projects/ or this agent's projects/ live."""

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
        save_validation_report(sysml_project_dir, result)
        return {"validation_status": result.status.value}

    def validation_passed(state: SysMLState) -> str:
        return "publish_version" if state["validation_status"] == ValidationStatus.PASSED.value else "human_review"

    def human_review_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        report_path = sysml_dir(sysml_project_dir) / "validation" / "sysml_validation_report.json"
        interrupt({"validation_report_path": str(report_path)})
        return {"status": "REVIEWED"}

    def publish_version_node(state: SysMLState) -> dict:
        sysml_project_dir = sysml_project_dir_resolver(state["project_id"])
        publish_version(sysml_project_dir, state["sysml_version"], parent=None)
        return {"status": "READY"}

    graph = StateGraph(SysMLState)
    graph.add_node("build_generation_contract", build_generation_contract_node)
    graph.add_node("create_generation_plan", create_generation_plan_node)
    graph.add_node("map_elements", map_elements_node)
    graph.add_node("generate_sysml", generate_sysml_node)
    graph.add_node("validate_generation", validate_generation_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("publish_version", publish_version_node)

    graph.add_edge(START, "build_generation_contract")
    graph.add_edge("build_generation_contract", "create_generation_plan")
    graph.add_edge("create_generation_plan", "map_elements")
    graph.add_edge("map_elements", "generate_sysml")
    graph.add_edge("generate_sysml", "validate_generation")
    graph.add_conditional_edges(
        "validate_generation", validation_passed, {"publish_version": "publish_version", "human_review": "human_review"}
    )
    graph.add_edge("human_review", "publish_version")
    graph.add_edge("publish_version", END)

    return graph
