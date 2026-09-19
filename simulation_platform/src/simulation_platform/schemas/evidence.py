"""Evidence model. Mirrors `Document Agent.md`, Section 41."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .common import SourceLocation


class EvidenceType(str, Enum):
    EXPLICIT_TEXT = "EXPLICIT_TEXT"
    TABLE_CELL = "TABLE_CELL"
    JSON_VALUE = "JSON_VALUE"
    CODE = "CODE"
    DIAGRAM_RELATION = "DIAGRAM_RELATION"
    EMAIL = "EMAIL"


class Evidence(BaseModel):
    evidence_id: str
    fact_id: str                 # the entity_id / requirement_id / relationship_id / behavior_id it supports
    type: EvidenceType
    document_id: str
    location: SourceLocation
    quote: str | None = None
