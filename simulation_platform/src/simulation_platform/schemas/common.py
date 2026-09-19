"""Shared primitives used across extraction, SysML generation, and Modelica
generation. Consolidated from three near-identical copies (one per former
package) into one canonical definition each -- `Comparator`/`FactStatus`
were byte-identical across all copies; `VersionRef` is kept as the
Modelica-side superset (adds `modelica_version`/`execution_id`, both
optional, so every existing use of the smaller SysML-side shape still
works unchanged).
"""

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


class VersionRef(BaseModel):
    knowledge_version: str
    sysml_version: str | None = None
    modelica_version: str | None = None
    execution_id: str | None = None


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"


class OpenQuestion(BaseModel):
    question_id: str
    question: str
    candidates: list[str]
    blocks: list[str] = []  # ids of plan items that cannot proceed until answered
