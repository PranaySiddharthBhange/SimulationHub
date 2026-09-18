"""SysML Validation Result. Mirrors `Agent Contracts.md`, Section 5."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"


class SyntaxIssue(BaseModel):
    file: str
    line: int | None = None
    message: str


class StructuralIssue(BaseModel):
    element: str
    error: str


class RequirementCoverage(BaseModel):
    total: int
    implemented: int
    missing: list[str] = []


class TraceabilityIssue(BaseModel):
    element: str
    error: str


class SemanticIssue(BaseModel):
    element: str
    expected: str
    actual: str


class SysMLValidationResult(BaseModel):
    generation_id: str
    status: ValidationStatus

    syntax_errors: list[SyntaxIssue] = []
    structural_errors: list[StructuralIssue] = []
    requirement_coverage: RequirementCoverage
    traceability_errors: list[TraceabilityIssue] = []
    semantic_errors: list[SemanticIssue] = []
