"""Property Mapping -- deterministic. Mirrors `Modelica Agent.md`, Section
11: preserve value, unit, meaning, source, and requirement -- a numeric
requirement bound maps directly to a Modelica `parameter`, no LLM judgment
call needed for this specific, mechanical transformation (unlike component
or behavior mapping, which genuinely need engineering judgment and are
handled by `element_mapper.py` instead).
"""

from __future__ import annotations

from simulation_platform.schemas import ModelicaMapping, ModelicaMappingType


def map_properties(requirement_ids: list[str], sysml_contract_raw: dict) -> list[ModelicaMapping]:
    requirements_by_id = {r["id"]: r for r in sysml_contract_raw.get("requirements", [])}

    mappings: list[ModelicaMapping] = []
    for requirement_id in requirement_ids:
        requirement = requirements_by_id.get(requirement_id)
        if requirement is None:
            continue

        bound = requirement.get("max") if requirement.get("max") is not None else requirement.get(
            "min", requirement.get("value")
        )
        unit = requirement.get("unit") or ""
        mappings.append(
            ModelicaMapping(
                sysml_element=requirement_id,
                mapping_type=ModelicaMappingType.PARAMETER,
                target="Real",
                reason=(
                    f"Requirement bound ({requirement.get('subject')}.{requirement.get('property')} "
                    f"{requirement.get('operator')} {bound} {unit}) preserved as a Modelica parameter."
                ),
                evidence=requirement.get("evidence", []),
            )
        )
    return mappings
