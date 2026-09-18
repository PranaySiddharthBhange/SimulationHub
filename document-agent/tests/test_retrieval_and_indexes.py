"""Index builders and the retrieval layer, seeded with a hand-built semantic
model so they can be verified without ever calling an LLM.
"""

from __future__ import annotations

from pathlib import Path

from engineering_agent.indexes.index_builder import (
    build_entity_index,
    build_evidence_index,
    build_relationship_index,
    build_requirement_index,
)
from engineering_agent.ingestion.manifest import save_source_manifest
from engineering_agent.observations.observation_store import append_observations
from engineering_agent.retrieval.knowledge import ProjectKnowledge
from engineering_agent.retrieval.tools import build_retrieval_tools
from engineering_agent.schemas import (
    Comparator,
    DocumentRecord,
    Entity,
    Evidence,
    EvidenceType,
    FactStatus,
    Observation,
    ObservationType,
    Relationship,
    Requirement,
    SemanticModel,
    SourceLocation,
    SourceManifest,
)
from engineering_agent.storage.artifacts import save_semantic_model


def _sample_model() -> SemanticModel:
    return SemanticModel(
        model_version="v0001",
        project_id="p1",
        entities=[Entity(entity_id="ENT-0001", name="AHU-01", type="AirHandlingUnit", status=FactStatus.EXPLICIT, evidence=["EV-1"])],
        relationships=[Relationship(relationship_id="REL-0001", source="ENT-0001", target="ENT-0001", type="contains", status=FactStatus.EXPLICIT, evidence=["EV-1"])],
        requirements=[
            Requirement(requirement_id="REQ-0001", subject="Zone-01", property="CO2", operator=Comparator.LTE, max=1000, unit="ppm", status=FactStatus.CONFIRMED, evidence=["EV-1"])
        ],
        evidence=[Evidence(evidence_id="EV-1", fact_id="REQ-0001", type=EvidenceType.EXPLICIT_TEXT, document_id="doc_0001", location=SourceLocation(page=8), quote="CO2 shall not exceed 1000 ppm.")],
    )


def _seed_project(project_dir: Path) -> None:
    manifest = SourceManifest(
        project_id="p1",
        documents=[
            DocumentRecord(
                document_id="doc_0001", path="01_requirements/req.pdf", filename="req.pdf",
                extension=".pdf", size=1, sha256="x", modified_time="2026-01-01T00:00:00Z",
            )
        ],
    )
    save_source_manifest(project_dir, manifest)
    append_observations(
        project_dir,
        [
            Observation(
                observation_id="obs_0001", document_id="doc_0001", type=ObservationType.TEXT,
                content="CO2 shall not exceed 1000 ppm.", location=SourceLocation(page=8), parser="pdf_parser",
            )
        ],
    )
    save_semantic_model(project_dir, _sample_model())


def test_index_builders_against_semantic_model() -> None:
    model = _sample_model()
    entity_index = build_entity_index(model)
    requirement_index = build_requirement_index(model)
    relationship_index = build_relationship_index(model)
    evidence_index = build_evidence_index(model)

    assert entity_index["ENT-0001"]["name"] == "AHU-01"
    assert requirement_index["REQ-0001"]["sources"][0]["document_id"] == "doc_0001"
    assert requirement_index["REQ-0001"]["sources"][0]["page"] == 8
    assert relationship_index["REL-0001"] == {"source": "ENT-0001", "target": "ENT-0001", "type": "contains", "evidence": ["EV-1"]}
    assert evidence_index["REQ-0001"] == ["EV-1"]


def test_project_knowledge_retrieval(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    knowledge = ProjectKnowledge(tmp_path)

    assert [e.name for e in knowledge.search_entities("ahu")] == ["AHU-01"]
    assert [r.requirement_id for r in knowledge.search_requirements("co2")] == ["REQ-0001"]
    assert knowledge.get_requirement("REQ-0001").max == 1000
    assert knowledge.get_evidence("REQ-0001")[0].evidence_id == "EV-1"
    assert knowledge.get_source_section("doc_0001")[0].content.startswith("CO2 shall not exceed")
    assert knowledge.get_entity("ENT-0001").type == "AirHandlingUnit"
    assert knowledge.get_conflicts() == []
    assert knowledge.get_unknowns() == []
    assert knowledge.get_decisions() == []


def test_retrieval_tools_wrap_knowledge_correctly(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    knowledge = ProjectKnowledge(tmp_path)
    tools = build_retrieval_tools(knowledge)
    tool_by_name = {t.name: t for t in tools}

    assert set(tool_by_name) == {
        "search_files", "search_entities", "search_requirements", "get_entity",
        "get_requirement", "get_evidence", "get_source_section", "get_conflicts",
        "get_ambiguities", "get_unknowns", "get_decisions", "get_dataset_statistics",
        "get_dataset_rows",
    }

    result = tool_by_name["get_requirement"].invoke({"requirement_id": "REQ-0001"})
    assert result["max"] == 1000
    assert tool_by_name["search_entities"].invoke({"query": "ahu"})[0]["name"] == "AHU-01"
    assert tool_by_name["get_conflicts"].invoke({}) == []
