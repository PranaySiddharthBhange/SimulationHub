"""Small handoffs; engineering reasoning stays in prose, not entity taxonomies."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Simulation(Record):
    start_time: float = 0
    stop_time: float
    intervals: int = Field(default=1000, ge=1, le=1000000)
    tolerance: float = Field(default=1e-6, gt=0, le=0.01)

    @model_validator(mode="after")
    def valid_duration(self):
        if self.stop_time <= self.start_time:
            raise ValueError("stop_time must be greater than start_time")
        return self


class Check(Record):
    name: str
    # A restricted arithmetic/Boolean expression over simulation variable names.
    # Bracketed names can be accessed with value("component.x"). Never Python eval.
    expression: str
    kind: Literal["final", "always", "at"]
    at_time: float | None = None
    expected: float
    absolute_tolerance: float = Field(default=1e-6, ge=0)
    relative_tolerance: float = Field(default=0, ge=0)
    source: str


class TableRole(Record):
    path: str
    role: Literal["input", "reference", "supporting"]
    reason: str


class Understanding(Record):
    title: str
    # The principal handoff: purpose, system boundary, resolved configuration,
    # units, equations, event priorities, initial conditions, and acceptance.
    narrative: str
    simulation: Simulation
    checks: list[Check]
    tables: list[TableRole] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)


class SysMLDraft(Record):
    code: str
    corrections: list[str] = Field(default_factory=list)


class ReferenceColumn(Record):
    path: str
    time_column: str
    reference_column: str
    model_variable: str
    absolute_tolerance: float = Field(ge=0)
    relative_tolerance: float = Field(default=0, ge=0)
    # Event traces often have a specified sample period. Discrete variables
    # must use step interpolation rather than invent intermediate states.
    interpolation: Literal["linear", "previous"] = "linear"
    reason: str


class ModelicaDraft(Record):
    model_name: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    code: str
    references: list[ReferenceColumn] = Field(default_factory=list)
    corrections: list[str] = Field(default_factory=list)


class Review(Record):
    passed: bool
    issues: list[str]


class SyntaxIssue(Record):
    file: str
    line: int | None = None
    message: str
