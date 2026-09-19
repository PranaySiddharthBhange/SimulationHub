"""Constraint extraction. Mirrors `Document Agent.md`, Section 25 (constraints) and `Agent Contracts.md`, Section 2."""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.constraint_extraction import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import Constraint, DocumentRecord, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction


class _ExtractedConstraint(BaseModel):
    subject: str
    property: str
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _ConstraintExtractionResult(BaseModel):
    constraints: list[_ExtractedConstraint]


def extract_constraints(document: DocumentRecord, observations: list[Observation], id_seq: IdSequence) -> list[Constraint]:
    result = run_structured_extraction(_SYSTEM_PROMPT, document, observations, _ConstraintExtractionResult)
    return [
        Constraint(
            constraint_id=id_seq.next("CON"),
            subject=item.subject,
            property=item.property,
            min=item.min,
            max=item.max,
            unit=item.unit,
            status=item.status,
            evidence=item.evidence_observation_ids,
        )
        for item in result.constraints
    ]
