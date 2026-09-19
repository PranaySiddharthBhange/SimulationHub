"""Modelica Validation Result. Mirrors `Agent Contracts.md`, Section 11,
and `Modelica Agent.md`, Section 22 -- the pre-compile, static-analysis
result across the five deterministic layers plus one LLM layer, distinct
from the `CompileResult` (real compiler output; see `compiler_result.py`).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .common import ValidationStatus


class ValidationLayer(str, Enum):
    SYNTAX = "SYNTAX"
    STRUCTURAL = "STRUCTURAL"
    CONNECTION = "CONNECTION"
    UNIT = "UNIT"
    PARAMETER = "PARAMETER"
    SEMANTIC = "SEMANTIC"


class ModelicaValidationIssue(BaseModel):
    layer: ValidationLayer
    element: str
    message: str


class ModelicaValidationResult(BaseModel):
    modelica_version: str
    status: ValidationStatus
    issues: list[ModelicaValidationIssue] = []
