"""Parameter Value Suggestion -- LLM stage, runs AFTER a first
deterministic generation pass (`generation/modelica_generator.py`)
surfaces every value this pipeline could not derive on its own: a generic
MSL library placeholder, a parameter with no requirement bound, a
from-scratch stub's sensed field, or a never-assigned legacy variable with
no matching scheduled command. Grounds each suggestion in the actual
project documents (already-extracted entities/requirements/behaviors/
control laws) instead of leaving the earlier generic default as the
suggestion a human is asked to confirm -- directly implements `new
direction.txt` §15's "never a placeholder, always suggest a sensible
value grounded in the problem, ask the user" directive for every
remaining gap category, not just the scheduled-command case that
motivated the original propose-then-confirm mechanism.

Same discipline as everywhere else in this pipeline: this LLM call only
PROPOSES a replacement suggestion -- nothing here applies it. See
`workflow/modelica_graph.py`'s `generate_modelica_node`, which raises the
REFINED suggestions through the same `interrupt()` mechanism already used
for every other pending decision, and only applies one once a human
actually confirms it.
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.llm import run_structured
from simulation_platform.prompts.parameter_value_suggestion import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.skills import with_modelica_skills

_SYSTEM_PROMPT = with_modelica_skills(_BASE_SYSTEM_PROMPT)


class _Suggestion(BaseModel):
    variable: str
    suggested_value: str
    reason: str


class _SuggestionResponse(BaseModel):
    suggestions: list[_Suggestion]


def suggest_parameter_values(
    pending_decisions: list[dict],
    sysml_contract_raw: dict,
    legacy_files: dict[str, str] | None = None,
    legacy_comparisons: list | None = None,
) -> list[dict]:
    """Returns `pending_decisions` with `suggested_value`/`reason` replaced
    for every entry not already marked `grounded` -- an entry already
    `grounded=True` (e.g. a real scheduled-command pulse, already derived
    from an exact extracted timestamp) is returned completely untouched,
    never second-guessed by an LLM call that could only make it worse.

    In practice, a human confirming this suggestion is a rubber stamp, not
    an independent check -- nothing here re-verifies a *value* the way
    `_render_behavior_equation`/`_render_state_machine` re-verify an *id*
    (there's no ground truth to check a number against). So the suggestion
    itself has to carry the real weight: `legacy_files` is the RAW
    `.mo` source text (not `analysis/legacy_analyzer.py`'s parsed
    `LegacyClass`, which deliberately strips `// ...` comments for its own
    deterministic purposes) -- a real legacy file often has exactly the
    geometry/material data a derived value (e.g. a magnetic reluctance from
    length/area/permeability) needs, including explicit stale-value
    corrections written only as comments (`STALE: CR-MAG-004 -> 1200`).
    Passing the parsed form here would silently throw that away.

    Matches suggestions back to `pending_decisions` by `variable` (the
    same stable key `command_overrides` is later keyed by) -- an entry the
    LLM didn't return a suggestion for is left with its original generic
    value, not dropped."""

    refinable = [d for d in pending_decisions if not d.get("grounded")]
    if not refinable:
        return pending_decisions

    user_prompt = (
        f"Values needing a grounded suggestion (each currently only has a generic placeholder): {refinable}\n\n"
        f"Project entities: {sysml_contract_raw.get('entities', [])}\n\n"
        f"Requirements: {sysml_contract_raw.get('requirements', [])}\n\n"
        f"Behaviors: {sysml_contract_raw.get('behaviors', [])}\n\n"
        f"Control laws: {sysml_contract_raw.get('control_laws', [])}\n\n"
        f"Raw legacy Modelica source files (read these fully, including comments -- they often carry "
        f"the real geometry/material data and stale-value corrections a derived value needs): "
        f"{legacy_files or {}}\n\n"
        f"Legacy comparison notes (differences/overrides already identified between the legacy file "
        f"and the current requirements): {[c.model_dump() for c in (legacy_comparisons or [])]}"
    )
    response = run_structured(SETTINGS.mapping_model, _SYSTEM_PROMPT, user_prompt, _SuggestionResponse)
    suggestion_by_variable = {s.variable: s for s in response.suggestions}

    refined: list[dict] = []
    for decision in pending_decisions:
        suggestion = suggestion_by_variable.get(decision["variable"])
        if suggestion is None:
            refined.append(decision)
        else:
            refined.append({**decision, "suggested_value": suggestion.suggested_value, "reason": suggestion.reason})
    return refined
