"""Entity extraction. Mirrors `Document Agent.md`, Sections 25-26."""

from __future__ import annotations

from pydantic import BaseModel, Field

from simulation_platform.prompts.entity_extraction import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import DocumentRecord, Entity, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction


class _ExtractedEntity(BaseModel):
    name: str
    type: str = Field(description="e.g. AirHandlingUnit, CO2Sensor, Controller, Zone, Tank, Valve")
    aliases: list[str] = []
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _EntityExtractionResult(BaseModel):
    entities: list[_ExtractedEntity]


def extract_entities(document: DocumentRecord, observations: list[Observation], id_seq: IdSequence) -> list[Entity]:
    result = run_structured_extraction(_SYSTEM_PROMPT, document, observations, _EntityExtractionResult)
    return [
        Entity(
            entity_id=id_seq.next("ENT"),
            name=item.name,
            type=item.type,
            status=item.status,
            evidence=item.evidence_observation_ids,
            aliases=item.aliases,
        )
        for item in result.entities
    ]
