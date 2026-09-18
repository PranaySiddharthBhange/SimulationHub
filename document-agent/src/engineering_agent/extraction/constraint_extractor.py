"""Constraint extraction. Mirrors `Document Agent.md`, Section 25 (constraints) and `Agent Contracts.md`, Section 2."""

from __future__ import annotations

from pydantic import BaseModel

from engineering_agent.schemas import Constraint, DocumentRecord, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction

_SYSTEM_PROMPT = (
    "You extract engineering CONSTRAINTS (bounded design ranges, e.g. "
    "'20 degC <= zone temperature <= 24 degC') from a set of observations "
    "drawn from one document. A constraint is a min/max bound on a property of "
    "a subject — distinct from a single-threshold requirement. Only extract "
    "constraints that are explicitly stated. Every constraint must cite at "
    "least one observation id as evidence."
)


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
