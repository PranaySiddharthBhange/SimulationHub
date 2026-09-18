"""Semantic Mapper — LLM stage 2. Mirrors `SysML V2 Agent.md`, Sections 7-13.

Maps every engineering concept in the contract to a SysML v2 construct
(`part def`, `requirement def`, `interface def`, `action def`, ...). The
mapping is determined by model semantics, not by blind keyword matching —
that's exactly what this LLM call is for. The result is validated
deterministically afterward (`validation/`), not trusted outright.

One call per category (entities, requirements, behaviors, constraints,
interfaces), not one call covering all five — found live, not assumed
(see `DECISIONS.md`): on a real, large dataset (67 entities + 159
requirements + 73 behaviors + 73 constraints = 372 items), a single
combined call returned a complete, validly-parsed JSON response that
nonetheless only covered the *first* category (all 67 entities) and
silently omitted every requirement/behavior/constraint, despite the
prompt explicitly asking for "exactly one mapping per input item" across
all five. Not a truncation bug — the response was ~59KB of well-formed
JSON, it just stopped after entities. Splitting by category means each
call's exhaustive-enumeration burden is bounded by one category's size,
not the whole contract's.

The categories are mapped sequentially, each one told which
(name, package) pairs earlier categories already used, and told not to
reuse one for a different concept. Also found live, immediately after
fixing the above: with each category mapped in total isolation, a
requirement and a constraint describing the same real-world idea (e.g.
"Tank1 initial level") independently landed on the identical SysML name
in the identical package — caught correctly by `validation/
structure_validator.py`'s existing name-collision check, but the fix
belongs here, not there.

The prompt instruction above is not, on its own, fully reliable — a
second live run (with that instruction already in place) still produced
one collision *within* a single category's own response (two different
requirements both named `STOP_event_time_650s_requirement`, in the same
call). `_deduplicate_names` is the deterministic backstop: every mapping
is guaranteed a unique (name, package) pair before it's ever handed to
the generator, regardless of what the model actually returns.
"""

from __future__ import annotations

from pydantic import BaseModel

from sysml_agent.config import SETTINGS
from sysml_agent.llm import run_structured
from sysml_agent.schemas import SysMLElementMapping, SysMLGenerationContract, SysMLGenerationPlan

_CONSTRUCT_GUIDANCE = {
    "entities": '"part def" for a system/physical component.',
    "requirements": '"requirement def" for every item — there is no other valid construct for a requirement.',
    "behaviors": '"action def" for an if/then control rule.',
    "constraints": '"constraint def" for a bounded-range constraint.',
    "interfaces": '"interface def" for a signal/fluid/thermal/electrical/mechanical interface.',
}

_SYSTEM_PROMPT_TEMPLATE = """\
You are the Semantic Mapper for a SysML v2 Creator Agent. For every {category} \
in the contract, decide the correct SysML v2 construct: {guidance}

Produce exactly one mapping per input item (matching `engineering_id` to the \
item's own id) — every single one, however many there are. Give each a \
sysml_element_name (a legal SysML identifier - letters, digits, underscore, \
no spaces) and the package it belongs in (from the plan's package list). \
State your rationale briefly.

Earlier categories have already claimed some (name, package) pairs — these \
are given to you below. Never reuse one of them for a different concept, \
even if it describes the same real-world idea (e.g. a requirement and a \
constraint about the same tank level still need two distinct SysML names). \
Pick a different, still-descriptive name instead.
"""


class _MappingResponse(BaseModel):
    mappings: list[SysMLElementMapping]


def _map_category(
    model_name: str, category: str, packages: list[str], items: list, claimed_names: set[tuple[str, str]]
) -> list[SysMLElementMapping]:
    if not items:
        return []
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(category=category, guidance=_CONSTRUCT_GUIDANCE[category])
    user_prompt = (
        f"Packages available: {packages}\n\n"
        f"Names already claimed by earlier categories (name, package): {sorted(claimed_names)}\n\n"
        f"{category.capitalize()}: {[i.model_dump() for i in items]}"
    )
    response = run_structured(model_name, system_prompt, user_prompt, _MappingResponse)
    return response.mappings


def _deduplicate_names(
    category_mappings: list[SysMLElementMapping], claimed_names: set[tuple[str, str]]
) -> list[SysMLElementMapping]:
    """Guarantees every (sysml_element_name, package) pair in the returned
    list is unique, both against `claimed_names` and against each other —
    the deterministic backstop behind the prompt instruction, which isn't
    fully reliable on its own (see module docstring)."""

    seen = set(claimed_names)
    deduped: list[SysMLElementMapping] = []
    for mapping in category_mappings:
        name, package = mapping.sysml_element_name, mapping.package
        if (name, package) not in seen:
            seen.add((name, package))
            deduped.append(mapping)
            continue

        suffix = 2
        while (f"{name}_{suffix}", package) in seen:
            suffix += 1
        new_name = f"{name}_{suffix}"
        seen.add((new_name, package))
        deduped.append(mapping.model_copy(update={"sysml_element_name": new_name}))

    return deduped


def map_elements(contract: SysMLGenerationContract, plan: SysMLGenerationPlan) -> list[SysMLElementMapping]:
    mappings: list[SysMLElementMapping] = []
    claimed_names: set[tuple[str, str]] = set()

    for category, items in (
        ("entities", contract.entities),
        ("requirements", contract.requirements),
        ("behaviors", contract.behaviors),
        ("constraints", contract.constraints),
        ("interfaces", contract.interfaces),
    ):
        category_mappings = _map_category(SETTINGS.mapping_model, category, plan.packages, items, claimed_names)
        category_mappings = _deduplicate_names(category_mappings, claimed_names)
        mappings.extend(category_mappings)
        claimed_names.update((m.sysml_element_name, m.package) for m in category_mappings)

    return mappings
