"""LangGraph ingestion workflow. Mirrors `Document Agent.md`, Section 52.

    START -> discover_files -> classify_files -> process_files
          -> build_indexes -> semantic_extraction -> entity_resolution
          -> reconciliation -> detect_uncertainty -> quality_check
          -> needs_user_input? --yes--> interrupt --> apply_decision -> quality_check
                              --no ---> build_semantic_model -> final_validation
          -> publish_version -> END

Each node reads/writes the project folder itself; the graph `KnowledgeState`
stays small (ids/counts/status only), per Section 53.
"""

from __future__ import annotations

from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from engineering_agent.evidence.evidence_manager import save_evidence
from engineering_agent.extraction.id_sequence import IdSequence
from engineering_agent.extraction.semantic_extractor import extract_semantic_model
from engineering_agent.indexes.index_builder import (
    build_entity_index,
    build_evidence_index,
    build_file_index,
    build_information_type_index,
    build_relationship_index,
    build_requirement_index,
    build_topic_index,
    save_index,
)
from engineering_agent.ingestion.dispatcher import process_documents
from engineering_agent.ingestion.file_classifier import classify_documents
from engineering_agent.ingestion.file_discovery import discover_files
from engineering_agent.ingestion.manifest import load_source_manifest, save_source_manifest
from engineering_agent.observations.observation_store import append_observations, load_observations
from engineering_agent.reconciliation.conflict_engine import detect_and_resolve_conflicts
from engineering_agent.resolution.entity_resolution import remap_relationship_endpoints, resolve_entities
from engineering_agent.schemas import Decision, ImpactLevel, ParseStatus, ProjectStatus
from engineering_agent.storage.artifacts import (
    load_ambiguities,
    load_semantic_model,
    publish_version,
    save_ambiguities,
    save_assumptions,
    save_conflicts,
    save_decisions,
    save_report,
    save_semantic_model,
    save_unknowns,
)
from engineering_agent.storage.project_store import ProjectStore
from engineering_agent.uncertainty.unknown_detector import detect_unknowns

from .state import KnowledgeState


def build_ingestion_graph(store: ProjectStore):
    def discover_files_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        manifest = discover_files(state["project_id"], store.source_original_dir(state["project_id"]))
        save_source_manifest(project_dir, manifest)
        return {"files_discovered": len(manifest.documents)}

    def classify_files_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        manifest = load_source_manifest(project_dir)
        classify_documents(manifest)
        save_source_manifest(project_dir, manifest)
        return {}

    def process_files_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        manifest = load_source_manifest(project_dir)
        observations = process_documents(manifest, store.source_original_dir(state["project_id"]))
        append_observations(project_dir, observations)
        save_source_manifest(project_dir, manifest)  # persists parse_status updates

        parsed = sum(1 for d in manifest.documents if d.parse_status == ParseStatus.PARSED)
        failed = sum(1 for d in manifest.documents if d.parse_status == ParseStatus.FAILED)
        return {
            "files_parsed": parsed,
            "files_failed": failed,
            "observations_created": len(observations),
        }

    def build_indexes_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        manifest = load_source_manifest(project_dir)
        observations = load_observations(project_dir)
        save_index(project_dir, "file_index", build_file_index(manifest, observations))
        save_index(project_dir, "topic_index", build_topic_index(manifest, observations))
        save_index(project_dir, "information_type_index", build_information_type_index(manifest))
        return {}

    def semantic_extraction_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        manifest = load_source_manifest(project_dir)
        observations = load_observations(project_dir)
        model = extract_semantic_model(state["project_id"], manifest, observations)
        save_semantic_model(project_dir, model)
        return {
            "entities_found": len(model.entities),
            "relationships_found": len(model.relationships),
            "requirements_found": len(model.requirements),
            "behaviors_found": len(model.behaviors),
            "constraints_found": len(model.constraints),
        }

    def entity_resolution_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        model = load_semantic_model(project_dir)
        id_seq = IdSequence()
        result = resolve_entities(model.entities, id_seq)
        model.entities = result.resolved_entities
        model.relationships = remap_relationship_endpoints(model.relationships, result.id_remap)
        model.assumptions.extend(result.assumptions)
        save_semantic_model(project_dir, model)
        save_ambiguities(project_dir, result.ambiguities)
        save_assumptions(project_dir, model.assumptions)
        return {"assumptions": len(model.assumptions), "ambiguities": len(result.ambiguities)}

    def reconciliation_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        manifest = load_source_manifest(project_dir)
        model = load_semantic_model(project_dir)
        conflicts = detect_and_resolve_conflicts(model.requirements, model.evidence, manifest)
        model.conflicts = conflicts
        save_semantic_model(project_dir, model)
        save_conflicts(project_dir, conflicts)
        return {"conflicts": len(conflicts)}

    def detect_uncertainty_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        model = load_semantic_model(project_dir)
        unknowns = detect_unknowns(model.requirements, model.constraints)
        model.unknowns = unknowns
        save_semantic_model(project_dir, model)
        save_unknowns(project_dir, unknowns)
        return {"unknowns": len(unknowns)}

    def quality_check_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        open_high_impact = _open_high_impact_ambiguities(project_dir)
        save_report(
            project_dir,
            "coverage_report",
            {
                "files_discovered": state["files_discovered"],
                "files_parsed": state["files_parsed"],
                "files_failed": state["files_failed"],
                "open_high_impact_ambiguities": len(open_high_impact),
            },
        )
        return {"status": "NEEDS_CLARIFICATION" if open_high_impact else "READY"}

    def needs_user_input(state: KnowledgeState) -> str:
        return "interrupt" if state["status"] == "NEEDS_CLARIFICATION" else "build_semantic_model"

    def interrupt_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        pending = _open_high_impact_ambiguities(project_dir)
        answer = interrupt({"pending_ambiguities": [a.model_dump() for a in pending]})
        # `answer` is whatever the caller resumes with via Command(resume=...):
        # {"ambiguity_id": ..., "answer": ...}
        decisions = [
            Decision(
                decision_id=f"DEC-{i + 1:04d}",
                question_id=item["ambiguity_id"],
                question=next((a.question for a in pending if a.ambiguity_id == item["ambiguity_id"]), ""),
                answer=item["answer"],
                affects=next((a.affects for a in pending if a.ambiguity_id == item["ambiguity_id"]), []),
            )
            for i, item in enumerate(answer if isinstance(answer, list) else [answer])
        ]
        save_decisions(project_dir, decisions)
        _mark_ambiguities_resolved(project_dir, {d.question_id for d in decisions})
        return {"status": "READY"}

    def build_semantic_model_node(state: KnowledgeState) -> dict:
        project_dir = store.project_dir(state["project_id"])
        model = load_semantic_model(project_dir)

        save_evidence(project_dir, model.evidence)
        save_index(project_dir, "entity_index", build_entity_index(model))
        save_index(project_dir, "requirement_index", build_requirement_index(model))
        save_index(project_dir, "relationship_index", build_relationship_index(model))
        save_index(project_dir, "evidence_index", build_evidence_index(model))

        publish_version(project_dir, "v0001", "initial ingestion", parent=None)
        manifest = store.load_manifest(state["project_id"])
        manifest.status = ProjectStatus.READY
        manifest.knowledge_version = "v0001"
        store.save_manifest(manifest)
        return {"model_version": model.model_version}

    graph = StateGraph(KnowledgeState)
    graph.add_node("discover_files", discover_files_node)
    graph.add_node("classify_files", classify_files_node)
    graph.add_node("process_files", process_files_node)
    graph.add_node("build_indexes", build_indexes_node)
    graph.add_node("semantic_extraction", semantic_extraction_node)
    graph.add_node("entity_resolution", entity_resolution_node)
    graph.add_node("reconciliation", reconciliation_node)
    graph.add_node("detect_uncertainty", detect_uncertainty_node)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("interrupt", interrupt_node)
    graph.add_node("build_semantic_model", build_semantic_model_node)

    graph.add_edge(START, "discover_files")
    graph.add_edge("discover_files", "classify_files")
    graph.add_edge("classify_files", "process_files")
    graph.add_edge("process_files", "build_indexes")
    graph.add_edge("build_indexes", "semantic_extraction")
    graph.add_edge("semantic_extraction", "entity_resolution")
    graph.add_edge("entity_resolution", "reconciliation")
    graph.add_edge("reconciliation", "detect_uncertainty")
    graph.add_edge("detect_uncertainty", "quality_check")
    graph.add_conditional_edges(
        "quality_check", needs_user_input, {"interrupt": "interrupt", "build_semantic_model": "build_semantic_model"}
    )
    graph.add_edge("interrupt", "quality_check")
    graph.add_edge("build_semantic_model", END)

    return graph


def _open_high_impact_ambiguities(project_dir: Path):
    return [a for a in load_ambiguities(project_dir) if a.impact == ImpactLevel.HIGH and a.status == "OPEN"]


def _mark_ambiguities_resolved(project_dir: Path, question_ids: set[str]) -> None:
    ambiguities = load_ambiguities(project_dir)
    for amb in ambiguities:
        if amb.ambiguity_id in question_ids:
            amb.status = "RESOLVED"
    save_ambiguities(project_dir, ambiguities)
