"""Layer 3 — Requirement coverage. Mirrors `SysML V2 Agent.md`, Section 17."""

from __future__ import annotations

from simulation_platform.schemas import RequirementCoverage, SysMLElementMapping, SysMLGenerationContract


def validate_requirement_coverage(
    contract: SysMLGenerationContract, mappings: list[SysMLElementMapping]
) -> RequirementCoverage:
    mapped_ids = {m.engineering_id for m in mappings}
    all_ids = [r.id for r in contract.requirements]
    missing = [rid for rid in all_ids if rid not in mapped_ids]
    return RequirementCoverage(total=len(all_ids), implemented=len(all_ids) - len(missing), missing=missing)
