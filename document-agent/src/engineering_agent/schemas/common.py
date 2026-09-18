"""Shared primitives. Mirrors `Agent Contracts.md`, Section 1 (Shared Primitives)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SourceLocation(BaseModel):
    """Exactly one of these is populated, matching the source document's format."""

    page: int | None = None
    section: str | None = None
    sheet: str | None = None
    cell: str | None = None
    json_path: str | None = None
    file: str | None = None
    line: int | None = None
    bbox: tuple[float, float, float, float] | None = None


class EvidenceRef(BaseModel):
    evidence_id: str
    document_id: str
    location: SourceLocation
    quote: str | None = Field(default=None, max_length=500)


class FactStatus(str, Enum):
    EXPLICIT = "EXPLICIT"
    CONFIRMED = "CONFIRMED"
    INFERRED = "INFERRED"
    ASSUMED = "ASSUMED"
    PROPOSED = "PROPOSED"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"
    USER_CONFIRMED = "USER_CONFIRMED"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"


class Comparator(str, Enum):
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    EQ = "=="
    RANGE = "RANGE"
