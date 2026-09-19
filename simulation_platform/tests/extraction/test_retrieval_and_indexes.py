"""Index builders, seeded with a hand-built semantic model so they can be
verified without ever calling an LLM.

The retrieval-layer tests that used to live here (`ProjectKnowledge`,
`build_retrieval_tools`) were dropped along with the optional
investigation-mode agent -- not part of the core index -> sysml -> simulate
pipeline (see ARCHITECTURE_REDESIGN_PLAN.md).
"""

from __future__ import annotations

from simulation_platform.extraction.indexes.index_builder import (
    build_entity_index,
    build_evidence_index,
    build_relationship_index,
    build_requirement_index,
)
from simulation_platform.schemas import (
    Comparator,
    Entity,
    Evidence,
    EvidenceType,
    FactStatus,
    Relationship,
    Requirement,
    SemanticModel,
    SourceLocation,
)


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
