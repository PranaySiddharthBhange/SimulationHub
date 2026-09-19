"""Legacy Modelica analysis. The `LegacyComparison` part mirrors
`Agent Contracts.md`, Section 10, and `Modelica Agent.md`, Section 15.
`LegacyClass`/`LegacyParameter`/`LegacyVariable` are internal to this
agent -- the structured output of `analysis/legacy_analyzer.py` parsing an
actual `.mo` file (Step in `Modelica Agent.md`, Section 14).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class LegacyParameter(BaseModel):
    name: str
    type: str
    value: str | None = None
    unit: str | None = None
    line: int


class LegacyVariable(BaseModel):
    name: str
    type: str
    unit: str | None = None
    # Both found live on a real dataset (see DECISIONS.md D50): the
    # original regex captured a variable's `unit="..."` modifier but
    # silently discarded the `discrete` qualifier and any `start=...`
    # value on reuse -- for a genuinely free discrete variable like
    # `discrete StepState seq(start=StepState.IDLE);` (never reassigned
    # anywhere in the source, by design -- it's meant to be driven by a
    # sequencer this fragment doesn't include), dropping `start=` left
    # the reused class with no way to determine its value at all.
    is_discrete: bool = False
    start_value: str | None = None
    line: int


class LegacyClass(BaseModel):
    kind: str  # model | block | connector | record | package | class
    name: str
    parameters: list[LegacyParameter] = []
    variables: list[LegacyVariable] = []
    connects: list[tuple[str, str]] = []
    equations: list[str] = []
    # Kept separate from `equations` -- Modelica requires `:=` assignments
    # and `when...then...end when;` blocks to live in an `algorithm`
    # section, never `equation` (found live: a legacy file with both
    # sections, merged into one on reuse, failed the real compiler with
    # "Equations can not contain assignments"; see DECISIONS.md).
    algorithm_statements: list[str] = []
    # Raw `type X = enumeration(...);` lines, verbatim. Found live: a
    # legacy file's algorithm section referenced a variable of a custom
    # enum type ("StepState"); without also capturing and re-emitting the
    # enum type itself, the reused class would declare the variable but
    # never define its type, or (before this field existed) skip the
    # variable entirely while still referencing it -- either way, "Variable
    # ... not found in scope" from the real compiler. See DECISIONS.md.
    type_declarations: list[str] = []


class LegacyModel(BaseModel):
    filename: str
    classes: list[LegacyClass] = []


class LegacyRecommendation(str, Enum):
    REUSE_AS_IS = "REUSE_AS_IS"
    MODIFY_LEGACY = "MODIFY_LEGACY"
    REPLACE = "REPLACE"


class LegacyComparison(BaseModel):
    sysml_element: str
    legacy_class: str
    legacy_file: str
    matches: list[str]
    differences: list[str]
    recommendation: LegacyRecommendation
    evidence: list[str] = []
    # legacy parameter name -> new value, for every difference above -- kept
    # machine-readable (not just the human-readable `differences` prose) so
    # `generation/modelica_generator.py` can actually apply a MODIFY_LEGACY
    # recommendation instead of silently reusing the stale legacy value.
    overrides: dict[str, str] = {}
