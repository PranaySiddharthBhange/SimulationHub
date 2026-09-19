"""State Machine Synthesis -- LLM stage 3 (mapping phase). Composes an
ORDERED SET of already-extracted Behaviors into a coherent state machine
(states + ordered transitions) for a reused legacy sequencer variable
(e.g. `discrete StepState seq`) that would otherwise stay permanently
frozen at whatever `start=` value the legacy source gave it (see
`generation/modelica_generator.py`'s never-assigned-variable path).

Inferring narrative ordering/grouping across a set of behavior facts is a
language-understanding task, not something deterministic pattern-matching
could do robustly and generically -- the reasoning behind choosing an LLM
call here, not a hand-written heuristic (same tradeoff already made for
`element_mapper.py`'s trigger_variable/control_input_variable fields).

Same "propose real ids only, verify before rendering" discipline as
everywhere else: the LLM is given the EXACT enum literal names already
declared in a reused legacy class and the EXACT ids of the behaviors/
requirements it may reference -- it never invents a state name or a fact
id. `generation/modelica_generator.py`'s renderer independently
re-verifies every reference before ever emitting a real `when` block;
anything unresolvable is dropped with a disclosed comment, never guessed.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.generation.modelica_generator import _is_ever_assigned
from simulation_platform.modelica_gen.llm import run_structured
from simulation_platform.prompts.state_machine_synthesis import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.schemas import LegacyModel, StateMachine
from simulation_platform.skills import with_modelica_skills

_SYSTEM_PROMPT = with_modelica_skills(_BASE_SYSTEM_PROMPT)

_ENUM_TYPE_PATTERN = re.compile(r"type\s+(\w+)\s*=\s*enumeration\s*\(([^)]*)\)")


def _enum_literals(legacy_models: list[LegacyModel]) -> dict[str, list[str]]:
    """type name -> its REAL declared literal names, for every `type X =
    enumeration(...)` in every reused legacy class -- the ONLY state names
    a synthesized state machine may ever reference (see
    `StateMachine.target_type_hint`'s own docstring)."""

    literals: dict[str, list[str]] = {}
    for legacy_model in legacy_models:
        for legacy_class in legacy_model.classes:
            for type_decl in legacy_class.type_declarations:
                match = _ENUM_TYPE_PATTERN.search(type_decl)
                if match:
                    names = [n.strip() for n in match.group(2).split(",") if n.strip()]
                    literals[match.group(1)] = names
    return literals


def _never_assigned_discrete_vars(legacy_models: list[LegacyModel]) -> list[dict]:
    """Every discrete variable, across every reused legacy class, that the
    legacy source itself never assigns anywhere -- exactly the population
    `_render_legacy_based_class`'s placeholder-equation path applies to,
    and therefore the only kind of variable a synthesized state machine
    could ever actually attach to."""

    candidates: list[dict] = []
    for legacy_model in legacy_models:
        for legacy_class in legacy_model.classes:
            all_statements = legacy_class.equations + legacy_class.algorithm_statements
            for var in legacy_class.variables:
                if var.is_discrete and not _is_ever_assigned(var.name, all_statements):
                    candidates.append({
                        "class_name": legacy_class.name,
                        "variable": var.name,
                        "type": var.type,
                        "declared_variables": [v.name for v in legacy_class.variables],
                        "declared_parameters": [p.name for p in legacy_class.parameters],
                    })
    return candidates


class _StateMachineResponse(BaseModel):
    state_machines: list[StateMachine]


def synthesize_state_machines(legacy_models: list[LegacyModel], sysml_contract_raw: dict) -> list[StateMachine]:
    enum_literals = _enum_literals(legacy_models)
    candidates = _never_assigned_discrete_vars(legacy_models)

    # Only bother calling the LLM for a type that's BOTH a real enum AND
    # actually the type of some never-assigned discrete variable -- no
    # candidate, no call (an ordinary numeric/boolean legacy variable is
    # already handled by the existing placeholder-equation path and isn't
    # a state machine at all).
    relevant_types = sorted({c["type"] for c in candidates if c["type"] in enum_literals})
    if not relevant_types:
        return []

    behaviors = sysml_contract_raw.get("behaviors", [])
    requirements = sysml_contract_raw.get("requirements", [])

    user_prompt = (
        f"Reused legacy sequencer variables awaiting a real state machine: {candidates}\n\n"
        f"Known enum types and their REAL declared literals (use ONLY these names, exactly, "
        f"as target_type_hint/states/initial_state): {{ {', '.join(f'{t!r}: {enum_literals[t]!r}' for t in relevant_types)} }}\n\n"
        f"Extracted behaviors (reference by their real id as trigger_behavior_id): {behaviors}\n\n"
        f"Extracted requirements (reference by their real id as wait_parameter_id): {requirements}"
    )
    response = run_structured(SETTINGS.mapping_model, _SYSTEM_PROMPT, user_prompt, _StateMachineResponse)
    return response.state_machines
