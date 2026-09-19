"""File discovery + classification records. Mirrors `Document Agent.md`, Sections 7-8."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class DocumentRole(str, Enum):
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    ENGINEERING_DATA = "ENGINEERING_DATA"
    DESIGN_DECISION = "DESIGN_DECISION"
    DESIGN_NOTE = "DESIGN_NOTE"
    CORRESPONDENCE = "CORRESPONDENCE"
    LEGACY_IMPLEMENTATION = "LEGACY_IMPLEMENTATION"
    DATASHEET = "DATASHEET"
    COMMISSIONING = "COMMISSIONING"
    MEASUREMENT = "MEASUREMENT"
    REFERENCE = "REFERENCE"
    DIAGRAM = "DIAGRAM"
    ARCHITECTURE = "ARCHITECTURE"
    OPERATOR_NOTE = "OPERATOR_NOTE"
    USER_STATEMENT = "USER_STATEMENT"
    UNKNOWN = "UNKNOWN"


class InformationType(str, Enum):
    REQUIREMENTS = "REQUIREMENTS"
    CONSTRAINTS = "CONSTRAINTS"
    CONTROL_LOGIC = "CONTROL_LOGIC"
    COMMISSIONING_DATA = "COMMISSIONING_DATA"
    LEGACY_IMPLEMENTATION = "LEGACY_IMPLEMENTATION"
    ARCHITECTURE = "ARCHITECTURE"
    MEASUREMENT_DATA = "MEASUREMENT_DATA"
    CORRESPONDENCE = "CORRESPONDENCE"
    REFERENCE_DATA = "REFERENCE_DATA"


class ParseStatus(str, Enum):
    PENDING = "PENDING"
    PARSED = "PARSED"
    FAILED = "FAILED"
    UNSUPPORTED = "UNSUPPORTED"


class DocumentRecord(BaseModel):
    """One row of `source_manifest.json` (file discovery + classification, merged)."""

    document_id: str
    path: str                      # relative to source/original/
    filename: str
    extension: str
    size: int
    sha256: str
    modified_time: str
    mime_type: str | None = None

    role: DocumentRole = DocumentRole.UNKNOWN
    information_types: list[InformationType] = []

    parse_status: ParseStatus = ParseStatus.PENDING
    parse_error: str | None = None
    retry_count: int = 0


class SourceManifest(BaseModel):
    project_id: str
    documents: list[DocumentRecord] = []
