"""Layer 2 — Structural validation. Mirrors `SysML V2 Agent.md`, Section 17.

Checks: every relationship endpoint has a mapping, every mapping's package
is one the plan actually declared, and no two mappings collide on the same
generated SysML element name.
"""

from __future__ import annotations

from sysml_agent.schemas import (
    StructuralIssue,
    SysMLElementMapping,
    SysMLGenerationContract,
    SysMLGenerationPlan,
)


def validate_structure(
    contract: SysMLGenerationContract,
    plan: SysMLGenerationPlan,
    mappings: list[SysMLElementMapping],
) -> list[StructuralIssue]:
    issues: list[StructuralIssue] = []
    mapping_by_id = {m.engineering_id: m for m in mappings}
    known_packages = set(plan.packages)

    for rel in contract.relationships:
        if rel.source not in mapping_by_id:
            issues.append(StructuralIssue(element=rel.source, error="Relationship source has no SysML mapping."))
        if rel.target not in mapping_by_id:
            issues.append(StructuralIssue(element=rel.target, error="Relationship target has no SysML mapping."))

    for mapping in mappings:
        if mapping.package not in known_packages:
            issues.append(
                StructuralIssue(
                    element=mapping.engineering_id,
                    error=f"Mapping references package '{mapping.package}', which is not in the generation plan.",
                )
            )

    seen_names: dict[tuple[str, str], str] = {}
    for mapping in mappings:
        key = (mapping.package, mapping.sysml_element_name)
        existing = seen_names.get(key)
        if existing is not None and existing != mapping.engineering_id:
            issues.append(
                StructuralIssue(
                    element=mapping.engineering_id,
                    error=f"SysML element name '{mapping.sysml_element_name}' in package '{mapping.package}' "
                    f"collides with mapping for '{existing}'.",
                )
            )
        seen_names[key] = mapping.engineering_id

    return issues
