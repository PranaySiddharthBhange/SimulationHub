"""Layer 4 — Traceability validation. Mirrors `SysML V2 Agent.md`, Section 17."""

from __future__ import annotations

from simulation_platform.schemas import SysMLElementMapping, TraceabilityIssue


def validate_traceability(mappings: list[SysMLElementMapping]) -> list[TraceabilityIssue]:
    return [
        TraceabilityIssue(element=mapping.engineering_id, error="Mapping has no evidence.")
        for mapping in mappings
        if not mapping.evidence
    ]
