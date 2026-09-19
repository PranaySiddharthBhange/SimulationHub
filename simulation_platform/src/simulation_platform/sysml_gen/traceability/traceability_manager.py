"""Traceability builder. Mirrors `SysML V2 Agent.md`, Section 16."""

from __future__ import annotations

from simulation_platform.schemas import SysMLConstruct, SysMLElementMapping, SysMLTraceability, SysMLTraceEntry

_FILE_BY_CONSTRUCT = {
    SysMLConstruct.PART_DEF: "Architecture.sysml",
    SysMLConstruct.PART: "Architecture.sysml",
    SysMLConstruct.REQUIREMENT_DEF: "Requirements.sysml",
    SysMLConstruct.REQUIREMENT: "Requirements.sysml",
    SysMLConstruct.INTERFACE_DEF: "Interfaces.sysml",
    SysMLConstruct.PORT_DEF: "Interfaces.sysml",
    SysMLConstruct.ACTION_DEF: "Behaviors.sysml",
    SysMLConstruct.STATE_DEF: "Behaviors.sysml",
    SysMLConstruct.CONSTRAINT_DEF: "Constraints.sysml",
    SysMLConstruct.ATTRIBUTE: "Constraints.sysml",
    SysMLConstruct.CONNECTION: "Architecture.sysml",
}


def build_traceability(sysml_version: str, mappings: list[SysMLElementMapping]) -> SysMLTraceability:
    entries = [
        SysMLTraceEntry(
            engineering_id=mapping.engineering_id,
            sysml_element=mapping.sysml_element_name,
            file=_FILE_BY_CONSTRUCT.get(mapping.sysml_construct, "Architecture.sysml"),
            evidence=mapping.evidence,
        )
        for mapping in mappings
    ]
    return SysMLTraceability(sysml_version=sysml_version, entries=entries)
