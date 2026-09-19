"""Uncertainty schemas. Mirrors `Document Agent.md`, Sections 31-36."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ConflictStatus(str, Enum):
    OPEN = "OPEN"
    SUPERSEDED = "SUPERSEDED"
    RESOLVED = "RESOLVED"


class Conflict(BaseModel):
    conflict_id: str
    fact_ids: list[str]           # the competing claims (entity/requirement ids)
    description: str
    status: ConflictStatus = ConflictStatus.OPEN
    superseded_by: str | None = None
    resolved_value: str | None = None


class Ambiguity(BaseModel):
    ambiguity_id: str
    question: str
    candidates: list[str]
    impact: ImpactLevel
    status: str = "OPEN"          # OPEN | RESOLVED
    affects: list[str] = []


class Unknown(BaseModel):
    unknown_id: str
    property: str
    entity: str
    reason: str
    status: str = "OPEN"


class Assumption(BaseModel):
    assumption_id: str
    statement: str
    status: str = "PROPOSED"      # PROPOSED | USER_CONFIRMED | REJECTED
    requires_confirmation: bool = True
    affects: list[str] = []
