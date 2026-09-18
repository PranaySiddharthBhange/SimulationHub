"""Requirement extraction. Mirrors `Document Agent.md`, Section 28."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engineering_agent.schemas import Comparator, DocumentRecord, FactStatus, Observation, Requirement

from .id_sequence import IdSequence
from .llm import run_structured_extraction

_SYSTEM_PROMPT = (
    "You extract engineering REQUIREMENTS from a set of observations drawn from "
    "one document. A requirement is a MEASURABLE constraint on a property of a "
    "subject: a numeric bound (value/min/max with a unit), or equality against a "
    "small, fixed set of named states (e.g. 'control mode == PID'). Only extract "
    "requirements that are explicitly stated — never infer a numeric bound that "
    "isn't written down.\n\n"
    "Do NOT extract a requirement for a plain architectural or narrative "
    "statement that has no measurable value — e.g. 'the room shall be "
    "represented as a single well-mixed volume', 'the model shall provide "
    "outdoor air through the supply path', or 'verification evidence shall "
    "record occupant count and room CO2'. Those describe structure or process, "
    "not a bounded property — represent the entities/relationships involved "
    "through entity and relationship extraction instead, and only create a "
    "requirement here when there is an actual number and unit, or a fixed "
    "enumerable state, being constrained.\n\n"
    "Every requirement must cite at least one observation id as evidence."
)


class _ExtractedRequirement(BaseModel):
    subject: str
    property: str
    operator: Comparator
    value: float | str | None = None
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    condition: str | None = Field(default=None, description="e.g. 'during occupied hours'")
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _RequirementExtractionResult(BaseModel):
    requirements: list[_ExtractedRequirement]


def extract_requirements(document: DocumentRecord, observations: list[Observation], id_seq: IdSequence) -> list[Requirement]:
    result = run_structured_extraction(_SYSTEM_PROMPT, document, observations, _RequirementExtractionResult)
    return [
        Requirement(
            requirement_id=id_seq.next("REQ"),
            subject=item.subject,
            property=item.property,
            operator=item.operator,
            value=item.value,
            min=item.min,
            max=item.max,
            unit=item.unit,
            condition=item.condition,
            status=item.status,
            evidence=item.evidence_observation_ids,
        )
        for item in result.requirements
    ]
