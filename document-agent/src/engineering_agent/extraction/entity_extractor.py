"""Entity extraction. Mirrors `Document Agent.md`, Sections 25-26."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engineering_agent.schemas import DocumentRecord, Entity, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction

_SYSTEM_PROMPT = (
    "You extract engineering ENTITIES (physical components, subsystems, sensors, "
    "controllers, actuators, zones, sources, boundaries) from a set of observations "
    "drawn from one engineering document. Every entity must cite at least one "
    "observation id as evidence — never invent an entity that isn't grounded in the "
    "text. If the same physical thing appears under multiple names in this "
    "document, list the other names as aliases rather than creating a second entity.\n\n"
    "Some observations come from Modelica source code or a diagram of a Modelica "
    "block model, not prose. Those show low-level implementation wiring — gain "
    "blocks, unit-conversion constants, intermediate signal variables (e.g. a bare "
    "variable name like `ductIn`, `traceVolume`, or `gainSensor` with no further "
    "description). Do NOT create an entity for a signal, gain, or wiring artifact "
    "that only exists to connect two real components — represent it as part of the "
    "relationship between those components instead. Only extract an entity there "
    "if it is a real named physical or logical component (sensor, controller, "
    "actuator, air handling unit, valve, tank, zone, source, boundary) that a "
    "systems engineer would model as its own part."
)


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
