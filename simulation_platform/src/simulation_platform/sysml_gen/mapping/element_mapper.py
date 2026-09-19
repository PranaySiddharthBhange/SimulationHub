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

from simulation_platform.prompts.sysml_mapping import CONSTRUCT_GUIDANCE as _CONSTRUCT_GUIDANCE
from simulation_platform.prompts.sysml_mapping import SYSTEM_PROMPT_TEMPLATE as _SYSTEM_PROMPT_TEMPLATE
from simulation_platform.skills import with_sysml_skills
from simulation_platform.sysml_gen.config import SETTINGS
from simulation_platform.sysml_gen.llm import run_structured
from simulation_platform.schemas import SysMLElementMapping, SysMLGenerationContract, SysMLGenerationPlan


class _MappingResponse(BaseModel):
    mappings: list[SysMLElementMapping]


def _map_category(
    model_name: str, category: str, packages: list[str], items: list, claimed_names: set[tuple[str, str]]
) -> list[SysMLElementMapping]:
    if not items:
        return []
    system_prompt = with_sysml_skills(
        _SYSTEM_PROMPT_TEMPLATE.format(category=category, guidance=_CONSTRUCT_GUIDANCE[category])
    )
    user_prompt = (
        f"Packages available: {packages}\n\n"
        f"Names already claimed by earlier categories (name, package): {sorted(claimed_names)}\n\n"
        f"{category.capitalize()}: {[i.model_dump() for i in items]}"
    )
    response = run_structured(model_name, system_prompt, user_prompt, _MappingResponse)
    return response.mappings


def _backfill_evidence(category_mappings: list[SysMLElementMapping], items: list) -> list[SysMLElementMapping]:
    """Deterministic backstop, same discipline as `_deduplicate_names`
    below -- found live on a real dataset: 413 of 420 real mappings came
    back with `evidence: []` even though every source item was GIVEN its
    own real evidence ids as part of the prompt input. A prompt
    instruction alone ("copy the item's evidence verbatim") isn't fully
    reliable (see this module's own docstring on `_deduplicate_names` for
    an identical lesson); this guarantees it by copying the source item's
    own evidence directly whenever the model left a mapping's evidence
    empty, so `validate_traceability` never has a real, traceable fact
    silently reported as untraceable."""

    evidence_by_id = {item.id: item.evidence for item in items}
    return [
        mapping.model_copy(update={"evidence": evidence_by_id.get(mapping.engineering_id, [])})
        if not mapping.evidence and evidence_by_id.get(mapping.engineering_id)
        else mapping
        for mapping in category_mappings
    ]


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
        ("control_laws", contract.control_laws),
        ("constraints", contract.constraints),
        ("interfaces", contract.interfaces),
    ):
        category_mappings = _map_category(SETTINGS.mapping_model, category, plan.packages, items, claimed_names)
        category_mappings = _backfill_evidence(category_mappings, items)
        category_mappings = _deduplicate_names(category_mappings, claimed_names)
        mappings.extend(category_mappings)
        claimed_names.update((m.sysml_element_name, m.package) for m in category_mappings)

    return mappings
