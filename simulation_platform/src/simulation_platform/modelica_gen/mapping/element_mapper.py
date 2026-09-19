"""Semantic Mapper -- LLM stage 2. Mirrors `Modelica Agent.md`, Sections
9-13, 16, 18: decide, for every component/behavior/constraint the plan
kept, the correct Modelica construct (`MODEL`, `BLOCK`, `LIBRARY_COMPONENT`,
`EQUATION`, `ALGORITHM`, `ASSERTION`). The library candidates and legacy
comparisons are already resolved deterministically before this call --
this stage picks among them and provides the engineering rationale, it
does not invent a library class name that isn't in `library_catalog.py`.

Response schema uses the real `ModelicaMapping` model directly (not a bare
`dict`) -- the exact class of bug the SysML Agent's planner shipped with,
already fixed there after its first live run (see `DECISIONS.md` D20).
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.libraries import resolve_component
from simulation_platform.modelica_gen.llm import run_structured
from simulation_platform.prompts.modelica_mapping import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.skills import with_modelica_skills
from simulation_platform.schemas import (
    LegacyComparison,
    ModelicaGenerationContract,
    ModelicaGenerationPlan,
    ModelicaMapping,
)

_SYSTEM_PROMPT = with_modelica_skills(_BASE_SYSTEM_PROMPT)


class _MappingResponse(BaseModel):
    mappings: list[ModelicaMapping]


def map_elements(
    contract: ModelicaGenerationContract,
    plan: ModelicaGenerationPlan,
    sysml_contract_raw: dict,
    legacy_comparisons: list[LegacyComparison],
) -> list[ModelicaMapping]:
    entities_by_id = {e["id"]: e for e in sysml_contract_raw.get("entities", [])}
    behaviors_by_id = {b["id"]: b for b in sysml_contract_raw.get("behaviors", [])}
    control_laws_by_id = {cl["id"]: cl for cl in sysml_contract_raw.get("control_laws", [])}
    constraints_by_id = {c["id"]: c for c in sysml_contract_raw.get("constraints", [])}

    component_context = []
    for component_id in plan.components:
        entity = entities_by_id.get(component_id)
        if entity is None:
            continue
        resolution = resolve_component(entity.get("name", ""), entity.get("type"))
        component_context.append(
            {
                "id": component_id,
                "name": entity.get("name"),
                "type": entity.get("type"),
                "evidence": entity.get("evidence", []),
                "library_candidates": [c.model_dump() for c in resolution.candidates],
                "library_ambiguous": resolution.ambiguous,
            }
        )

    user_prompt = (
        f"Project: {contract.project_id}\n\n"
        f"Components to map: {component_context}\n\n"
        f"Behaviors to map: {[behaviors_by_id[b] for b in plan.behaviors if b in behaviors_by_id]}\n\n"
        f"Control laws to map: {[control_laws_by_id[cl] for cl in plan.control_laws if cl in control_laws_by_id]}\n\n"
        f"Constraints to map: {[constraints_by_id[c] for c in plan.constraints if c in constraints_by_id]}\n\n"
        f"Legacy comparisons: {[c.model_dump() for c in legacy_comparisons]}"
    )
    response = run_structured(SETTINGS.mapping_model, _SYSTEM_PROMPT, user_prompt, _MappingResponse)
    return response.mappings
