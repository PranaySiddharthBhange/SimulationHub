"""Compile Result. Mirrors `Agent Contracts.md`, Section 15, and
`Compiler Agent.md`, Section 9.

Produced here by `compiler/openmodelica_client.py` -- a thin local stand-in
for the not-yet-built, standalone Compiler / Simulation Agent (see that
module's docstring and `DECISIONS.md`). The schema is unchanged either way:
whichever agent eventually produces it, the Modelica Agent consumes this
exact shape.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


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
    # (see `compiler/openmodelica_client.py::_parse_result_csv`) -- empty
    # when the simulation didn't run/pass, or CSV output wasn't produced.
    result_summary: dict[str, dict[str, float]] = {}
