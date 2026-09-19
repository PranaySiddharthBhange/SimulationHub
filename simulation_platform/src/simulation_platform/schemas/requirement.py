"""Requirement schema. Mirrors `Document Agent.md`, Section 28."""

from __future__ import annotations

from pydantic import BaseModel

from .common import Comparator, FactStatus


class Requirement(BaseModel):
    requirement_id: str
    subject: str
    property: str
    operator: Comparator
    value: float | str | None = None
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    condition: str | None = None
    status: FactStatus
    evidence: list[str] = []
