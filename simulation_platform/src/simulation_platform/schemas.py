"""Every data model the live pipeline actually uses that isn't already in
`contracts.py` (the LLM-facing structured-output models). Replaces a
30-file `schemas/` package inherited from the old structured pipeline --
traced the live import graph and found only these 7 classes, from 3 of
those files, were ever actually imported by code still in use; the other
~27 files were dead weight kept alive only by `schemas/__init__.py`
eagerly importing everything unconditionally.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

# -- project.py: used by project_store.py --------------


class ProjectStatus(str, Enum):
    CREATED = "CREATED"
    INGESTING = "INGESTING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY = "READY"
    FAILED = "FAILED"


class ProjectManifest(BaseModel):
    project_id: str
    name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_root: str
    status: ProjectStatus = ProjectStatus.CREATED
    knowledge_version: str = "v0000"


# -- sysml_validation.py: used by tools/sysml_validator.py -----------------


class SyntaxIssue(BaseModel):
    file: str
    line: int | None = None
    message: str


# -- compiler_result.py: used by tools/modelica_validator.py ----------------


class CompileStatus(str, Enum):
    PREFLIGHT_FAILED = "PREFLIGHT_FAILED"
    PASSED = "PASSED"
    FAILED = "FAILED"


class ErrorCategory(str, Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    CLASS_NOT_FOUND = "CLASS_NOT_FOUND"
    CONNECTOR_TYPE_MISMATCH = "CONNECTOR_TYPE_MISMATCH"
    CONNECTOR_UNCONNECTED = "CONNECTOR_UNCONNECTED"
    DUPLICATE_DECLARATION = "DUPLICATE_DECLARATION"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    OVERDETERMINED_SYSTEM = "OVERDETERMINED_SYSTEM"
    UNDERDETERMINED_SYSTEM = "UNDERDETERMINED_SYSTEM"
    UNKNOWN = "UNKNOWN"


class CompileError(BaseModel):
    error_id: str
    severity: str
    category: ErrorCategory
    file: str
    line: int | None = None
    message: str
    raw: str


class CompileWarning(BaseModel):
    warning_id: str
    category: str
    file: str
    line: int | None = None
    message: str


class CompileResult(BaseModel):
    execution_id: str
    status: CompileStatus
    backend: str
    backend_version: str
    duration_seconds: float
    errors: list[CompileError] = []
    warnings: list[CompileWarning] = []
    # {variable_name: {"min", "max", "final"}} from the real simulation run
    # (see `tools/modelica_validator.py::_parse_result_csv`) -- empty when
    # the simulation didn't run/pass, or CSV output wasn't produced.
    result_summary: dict[str, dict[str, float]] = {}
