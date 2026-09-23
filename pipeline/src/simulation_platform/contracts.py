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


class MergeClarification(Record):
    """A material Merge decision presented to the Clarify stage."""

    id: str
    question: str
    reasoning: str
    suggested_value: str = ""
    options: list[str] = Field(default_factory=list)


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
    clarifications: list[MergeClarification] = Field(default_factory=list)
    # Which general engineering domain(s) this system belongs to (from
    # `skills.domains.DOMAIN_SKILLS`'s keys), so Stage 2/3 can be handed the
    # relevant domain's standard equations/conventions -- see
    # `skills/domains.py` for why this is domain knowledge, not
    # problem-specific detail, and never invented ids/values. Free-text, not
    # a strict enum: an unrecognized key just means no extra domain skill
    # text gets appended, never a validation failure.
    domains: list[str] = Field(default_factory=list)


class Clarification(Record):
    """One genuinely unresolved decision Stage 2 needs a human for -- see
    `skills/stage2_sysml.py`'s own instructions for when the model should
    populate this (materially ambiguous/missing, never a stylistic choice).
    `suggested_value` is mandatory so the UI always has a one-click default
    to offer, and `code` is always written using it, so an unanswered
    clarification never blocks the pipeline outright -- it degrades to
    "proceeded on the model's own suggested default", not a hang."""

    id: str
    question: str
    reasoning: str
    suggested_value: str
    options: list[str] = Field(default_factory=list)


class MermaidDraft(Record):
    """A validated handoff for the human-readable system flow diagram."""

    code: str = Field(min_length=1)
    corrections: list[str] = Field(default_factory=list)


class SysMLDraft(Record):
    code: str
    corrections: list[str] = Field(default_factory=list)
    clarifications: list[Clarification] = Field(default_factory=list)


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


class ModelicaFile(Record):
    """One loadable file in a generated Modelica model bundle.

    Files are ordered by dependency: reusable plant/controller components first,
    and the top-level system model last. Keeping that order explicit avoids
    relying on filename sorting when OpenModelica loads a multi-file design.
    """

    filename: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*\.mo$")
    role: Literal["component", "controller", "system", "support"]
    code: str = Field(min_length=1)


class ModelicaDraft(Record):
    entry_class: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    files: list[ModelicaFile] = Field(min_length=2)
    # Fully-qualified Modelica Standard Library classes actually instantiated
    # by the generated bundle. Stage 3 receives a verified domain catalog and
    # records its concrete selection here for review and reproducibility.
    library_components: list[str] = Field(default_factory=list)
    references: list[ReferenceColumn] = Field(default_factory=list)
    corrections: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_bundle(self):
        filenames = [file.filename for file in self.files]
        if len(filenames) != len(set(filenames)):
            raise ValueError("Modelica bundle filenames must be unique")
        if sum(file.role == "system" for file in self.files) != 1:
            raise ValueError("Modelica bundle must contain exactly one system file")
        if not any(f"model {self.entry_class}" in file.code for file in self.files):
            raise ValueError(f"entry_class {self.entry_class!r} is not declared by any generated file")
        return self


class Review(Record):
    passed: bool
    issues: list[str]


class ValidationReport(Record):
    """Stage 4's output -- an independent review of the REAL simulated
    trajectory against the actual problem statement, never the generating
    model's own self-report. See `skills/stage4_validation.py`."""

    verdict: Literal["valid", "invalid", "partially_valid"]
    # One plain-language paragraph for the person who commissioned the run,
    # not another engineer -- see the prompt's own instruction on audience.
    summary: str
    issues: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    root_causes: list[str] = Field(default_factory=list)


class SyntaxIssue(Record):
    file: str
    line: int | None = None
    message: str
