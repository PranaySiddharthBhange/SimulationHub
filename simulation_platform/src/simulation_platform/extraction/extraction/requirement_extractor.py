"""Requirement extraction. Mirrors `Document Agent.md`, Section 28."""

from __future__ import annotations

from pydantic import BaseModel, Field

from simulation_platform.prompts.requirement_extraction import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import Comparator, DocumentRecord, FactStatus, Observation, Requirement

from .id_sequence import IdSequence
from .llm import run_structured_extraction


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
