"""Constraint schema, matching `Agent Contracts.md`, Section 2 (ConstraintItem)."""

from __future__ import annotations

from pydantic import BaseModel

from .common import FactStatus


class Constraint(BaseModel):
    constraint_id: str
    subject: str
    property: str
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    status: FactStatus
    evidence: list[str] = []
