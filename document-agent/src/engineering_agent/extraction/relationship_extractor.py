"""Relationship extraction. Mirrors `Document Agent.md`, Section 27."""

from __future__ import annotations

from pydantic import BaseModel

from engineering_agent.schemas import DocumentRecord, Entity, FactStatus, Observation, Relationship

from .id_sequence import IdSequence
from .llm import run_structured_extraction

_SYSTEM_PROMPT = (
    "You extract relationships between engineering entities from a set of "
    "observations drawn from one document. Only use the entity names given to "
    "you; do not invent new entities here. Valid relationship types include: "
    "contains, part_of, composed_of, connected_to, supplies, serves, controls, "
    "regulates, requires, depends_on, triggers, causes, responds_to, air_flow, "
    "water_flow, signal_flow, electrical_flow. Every relationship must cite at "
    "least one observation id as evidence."
)


class _ExtractedRelationship(BaseModel):
    source_entity_name: str
    target_entity_name: str
    type: str
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _RelationshipExtractionResult(BaseModel):
    relationships: list[_ExtractedRelationship]


def extract_relationships(
    document: DocumentRecord,
    observations: list[Observation],
    known_entities: list[Entity],
    id_seq: IdSequence,
) -> list[Relationship]:
    name_to_id = {entity.name.lower(): entity.entity_id for entity in known_entities}
    for entity in known_entities:
        for alias in entity.aliases:
            name_to_id.setdefault(alias.lower(), entity.entity_id)

    entity_prompt = f"{_SYSTEM_PROMPT}\n\nKnown entities in this document: {[e.name for e in known_entities]}"
    result = run_structured_extraction(entity_prompt, document, observations, _RelationshipExtractionResult)

    relationships: list[Relationship] = []
    for item in result.relationships:
        source_id = name_to_id.get(item.source_entity_name.lower())
        target_id = name_to_id.get(item.target_entity_name.lower())
        if source_id is None or target_id is None:
            continue  # relationship referencing an entity we never extracted — drop rather than invent one
        relationships.append(
            Relationship(
                relationship_id=id_seq.next("REL"),
                source=source_id,
                target=target_id,
                type=item.type,
                status=item.status,
                evidence=item.evidence_observation_ids,
            )
        )
    return relationships
