"""Small handoffs; engineering reasoning stays in prose, not entity taxonomies."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Simulation(Record):
    start_time: float = Field(default=0, description="Run start time in seconds.")
    stop_time: float = Field(description=(
        "Run end time in seconds, taken from the stated experiment duration. If no note "
        "states one, choose the shortest horizon that lets every stated behaviour complete "
        "and record that choice as an assumption."
    ))
    intervals: int = Field(default=1000, ge=1, le=1000000, description="Number of output samples.")
    tolerance: float = Field(default=1e-6, gt=0, le=0.01, description="Solver tolerance.")

    @model_validator(mode="after")
    def valid_duration(self):
        if self.stop_time <= self.start_time:
            raise ValueError("stop_time must be greater than start_time")
        return self


class Check(Record):
    """One mechanically evaluable acceptance criterion.

    Every field carries a description because the model filling this in only
    ever sees the generated JSON schema -- a Python comment here reaches
    nobody. Confirmed live: with the fields undescribed, the same prompt
    produced evaluable expressions on one dataset and a prose sentence
    describing the criterion on another, and a
    prose expression cannot be checked against a result file at all.
    """

    name: str = Field(description="Short label for this criterion, e.g. its requirement id and intent.")
    expression: str = Field(description=(
        "An arithmetic or Boolean expression over the model's reported variable names, "
        "evaluable against a result file. Use the exact variable names declared in the "
        "narrative, combined with + - * / ( ), comparisons, and and/or/not. "
        "It must NOT be an English sentence: 'quantity_a >= limit_a' is a valid expression, "
        "'the quantity reaches its limit before the next phase' is not."
    ))
    kind: Literal["final", "always", "at", "ever"] = Field(description=(
        "'final' compares the value at the end of the run, 'always' requires the "
        "expression to hold at every sample, 'at' compares it at the instant in at_time, "
        "and 'ever' requires it to hold at a minimum of one sample during the run. "
        "Use 'ever' for a target that is reached and then left behind, which is most "
        "stage targets in a sequenced process: a later stage undoes the condition an "
        "earlier one had to meet. Marking such a target 'final' asserts it still holds "
        "at the end, and contradicts the check for the stage that undid it."
    ))
    at_time: float | None = Field(default=None, description=(
        "The instant this is evaluated at, in seconds. Required when kind is 'at', null otherwise."
    ))
    expected: float = Field(description=(
        "The numeric value the expression should equal. For a Boolean condition use 1.0, "
        "meaning the condition holds."
    ))
    absolute_tolerance: float = Field(default=1e-6, ge=0, description=(
        "Absolute tolerance on the VALUE of the expression. It is never a tolerance on "
        "time: to allow slack around an instant, choose an at_time safely inside the "
        "interval where the condition must hold, rather than widening this. "
        "For a Boolean expression with expected 1.0 it must be 0, because a tolerance of "
        "1.0 or more also admits false and the check can then never fail. Otherwise use "
        "the tolerance the evidence states, or one the quantity's own precision justifies."
    ))
    relative_tolerance: float = Field(default=0, ge=0, description="Relative tolerance, when the evidence gives one.")
    source: str = Field(description=(
        "Where this criterion came from: the note's own filename, and the requirement "
        "identifier that states it when the note records one. Take both from the note "
        "itself; never write an identifier that does not appear there."
    ))

    @model_validator(mode="after")
    def tolerance_cannot_admit_false(self):
        """A Boolean check with a tolerance of 1.0 or more can never fail.

        Clamped rather than rejected: a hard error here would fail the whole
        Merge stage over one field. Found live -- asked for acceptance criteria
        on a sequencing benchmark, the model expressed the allowed slack around
        an event's INSTANT as a tolerance on the expression's value, giving five
        of eleven checks a tolerance of 2.0 against an expected of 1.0. Every
        one of them passed whether the condition held or not.
        """

        boolean_like = any(token in self.expression for token in ("==", "!=", ">=", "<=", ">", "<", " and ", " or ", "not "))
        if boolean_like and self.expected in (0.0, 1.0) and self.absolute_tolerance >= 0.5:
            object.__setattr__(self, "absolute_tolerance", 0.0)
        return self


class TableRole(Record):
    path: str = Field(description="The source document this table came from, as the notes name it.")
    role: Literal["input", "reference", "supporting"] = Field(description=(
        "'input' supplies the scenario the model must run; 'reference' is a recorded "
        "result to compare against and must never drive the model; 'supporting' is "
        "context that does neither."
    ))
    reason: str = Field(description="What in the notes establishes that role.")


class MergeClarification(Record):
    """A material Merge decision presented to the Clarify stage."""

    id: str
    question: str
    reasoning: str
    suggested_value: str = ""
    options: list[str] = Field(default_factory=list)


class ResolvedConflict(Record):
    """A material conflict Merge settled on the evidence, shown to the human anyway.

    Merge only ever surfaced what it could NOT resolve. As extraction improved,
    it began resolving conflicts it used to ask about -- on one benchmark the
    open questions went from three to zero in a single run -- so the better it
    got, the less a reviewer saw. The decisions did not stop being consequential
    just because the evidence settled them, and an engineer may still disagree
    with a change record the documents themselves disagree about. Recording them
    here lets Clarify present each one already answered, for confirmation or
    override, instead of applying it silently.
    """

    id: str = Field(description="Stable identifier for this decision, e.g. resolve_<quantity>.")
    topic: str = Field(description="The quantity or behaviour in dispute, in a few words.")
    chosen: str = Field(description="The value or behaviour adopted, with its unit.")
    rejected: list[str] = Field(default_factory=list, description=(
        "Each candidate not adopted, with the reason it lost -- superseded, proposed, "
        "observed once, archived."
    ))
    reasoning: str = Field(description=(
        "The evidence that decided it: which note, which status, which change record."
    ))


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
    # Conflicts Merge DID settle. Surfaced to the human for confirmation so a
    # resolution is never applied silently -- see `ResolvedConflict`.
    resolutions: list[ResolvedConflict] = Field(default_factory=list)
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
    # True when Merge already settled this on the evidence and is asking the
    # reviewer to confirm rather than to decide. Kept explicit rather than
    # inferred from the id or the wording, because the UI presents the two
    # cases quite differently: one is a question, the other is a sign-off.
    resolved: bool = False


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


class CheckResult(Record):
    """One acceptance check from the brief, evaluated against the real run.

    Reported per check rather than summarised, because a check nobody
    evaluated and a check that passed look identical in prose. Confirmed
    live: a run that never accepted a STOP command, and so could not satisfy
    the two checks covering pause and resume, was still described as mostly
    working -- the failing checks appeared as narrative issues rather than as
    checks marked failed.
    """

    name: str = Field(description="The check's name exactly as the brief states it.")
    expression: str = Field(description="The check's expression exactly as the brief states it.")
    outcome: Literal["pass", "fail", "not_evaluable"] = Field(description=(
        "`pass` when the real numbers satisfy it within its tolerance, `fail` when they do "
        "not, and `not_evaluable` ONLY when a variable it names is absent from the result "
        "file. Never report `not_evaluable` because a value is hard to read off: find it."
    ))
    observed: str = Field(description=(
        "The actual value or event found in the result data, with the time it was read at, "
        "and the expected value beside it. Quote real numbers -- this is the evidence the "
        "outcome rests on."
    ))


class ValidationReport(Record):
    """Stage 4's output -- an independent review of the REAL simulated
    trajectory against the actual problem statement, never the generating
    model's own self-report. See `skills/stage4_validation.py`."""

    verdict: Literal["valid", "invalid", "partially_valid"]
    check_results: list[CheckResult] = Field(default_factory=list, description=(
        "Every acceptance check in the brief, in the order the brief lists them, each with "
        "its own outcome. Omit none: a check missing from this list reads as one that was "
        "never looked at."
    ))
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


# --- Stage 1 cloud extraction -------------------------------------------
# The local model writes free text (constrained decoding is slow and
# hang-prone on it). A cloud extraction has no such limit, so it returns a
# typed result instead: every field is validated, no section can go missing,
# and -- most importantly -- each item carries the exact source span it came
# from, which makes fabrication mechanically detectable rather than a
# judgement call. See `_verify_quotes` in `reasoner_pipeline.py`.

_EXTRACTION_CATEGORIES = Literal[
    "requirement",
    "constraint",
    "behavior",
    "physical_relationship",
    "control_law",
    "scheduled_command",
]

# What KIND of document this is, which is what decides how much weight a
# statement in it carries. Confirmed necessary: resolving the tank benchmark
# required treating an operator's shift note as an observation that loses to an
# approved requirement and a test procedure, and nothing in the extraction
# recorded that distinction -- Merge had to re-derive it from prose.
CANONICAL_DOCUMENT_KIND = (
    "requirement_spec",
    # A multi-sheet engineering register: requirements alongside equipment
    # schedules, IO lists, operating parameters and a change log. Every dataset
    # in this benchmark has one, and it is neither a pure specification nor a
    # recorded dataset -- classifying it as either loses what it is.
    "engineering_register",
    "datasheet",
    "test_procedure",
    "design_note",
    "correspondence",
    "legacy_model",
    "operator_log",
    "dataset",
    "drawing",
    "other",
)

# Whether a value governs or has been replaced. The benchmark datasets are built
# around this: one states a high-level setpoint twice with different numbers, one
# gives a nominal and an as-built gap, one carries a literal "STALE: superseded
# by CR-017" marker. Across the three datasets there are ~300 such status words.
#
# Deliberately a free string rather than a closed enum. Confirmed live: a strict
# Literal rejected `status="released"` -- a word the tank URS genuinely uses --
# and failed the whole extraction call. Document vocabulary is open ("released",
# "issued", "final", "Rev B"), and losing an entire document because it used an
# unanticipated but perfectly valid word is far worse than accepting the word and
# normalising it afterwards. `reasoner_pipeline._canonical_status` maps the common
# variants onto CANONICAL_STATUS for machine use while the raw word is preserved.
CANONICAL_STATUS = (
    "current", "approved", "nominal", "as_built", "measured",
    "observed", "proposed", "archived", "superseded", "unknown",
)


class ExtractedValue(Record):
    """One numeric value with its unit and its standing in the evidence."""

    quantity: str
    # Exactly as written, without normalising or converting.
    value: str
    unit: str = ""
    status: str = "unknown"
    # What this value replaces, or what replaces it, when the document says so
    # ("superseded by CR-017", "supersedes Legacy Model v1.0").
    supersedes: str = ""
    quote: str


class ExtractedEntity(Record):
    """One real component, actor or control element named by the document."""

    name: str
    kind: str
    aliases: list[str] = Field(default_factory=list)
    values: list[ExtractedValue] = Field(default_factory=list)
    # The document's own identifier for this item, when it has one.
    ref: str = ""
    # The "[page N]" or "[sheet X]" marker this came from, copied verbatim from
    # the document text. `sources.py` emits these; nothing used to keep them.
    anchor: str = ""
    # True when this was read from an accompanying image rather than the
    # document text. A diagram carries no quotable substring, so quote
    # verification skips these and `quote` holds where in the image it was
    # seen. Without this the quote rule silently emptied image-only
    # documents -- a reference control diagram, the single most
    # topology-rich file in its dataset, extracted nothing at all because
    # the model correctly refused to invent a quote for it.
    from_image: bool = False
    quote: str


class ExtractedRelationship(Record):
    """A connection, containment, control or arrangement between two entities."""

    subject: str
    predicate: str
    object: str
    detail: str = ""
    ref: str = ""
    anchor: str = ""
    # True when this was read from an accompanying image rather than the
    # document text. A diagram carries no quotable substring, so quote
    # verification skips these and `quote` holds where in the image it was
    # seen. Without this the quote rule silently emptied image-only
    # documents -- a reference control diagram, the single most
    # topology-rich file in its dataset, extracted nothing at all because
    # the model correctly refused to invent a quote for it.
    from_image: bool = False
    quote: str


class ExtractedFact(Record):
    """A requirement, constraint, behavior, equation, control law or command."""

    category: _EXTRACTION_CATEGORIES
    statement: str
    # The requirement/criterion id the document gives it -- "AC-01", "CR-017",
    # "URS-M-003". These are the traceability anchors the acceptance checks
    # carry through to `Check.source`.
    ref: str = ""
    anchor: str = ""
    status: str = "unknown"
    # True when this was read from an accompanying image rather than the
    # document text. A diagram carries no quotable substring, so quote
    # verification skips these and `quote` holds where in the image it was
    # seen. Without this the quote rule silently emptied image-only
    # documents -- a reference control diagram, the single most
    # topology-rich file in its dataset, extracted nothing at all because
    # the model correctly refused to invent a quote for it.
    from_image: bool = False
    quote: str


class ExtractedDocument(Record):
    document: str
    # What kind of system this document is about, in the document's own terms.
    # Not a classification into a fixed taxonomy -- that happens in Merge.
    subject: str
    kind: str = "other"
    entities: list[ExtractedEntity] = Field(default_factory=list)
    relationships: list[ExtractedRelationship] = Field(default_factory=list)
    facts: list[ExtractedFact] = Field(default_factory=list)
    # Anything present but unreadable (a figure with no legend, a truncated
    # formula). Recorded rather than guessed at.
    unreadable: list[str] = Field(default_factory=list)
