"""SysML Semantic Model -- internal to the Modelica Agent. Not a boundary
contract (so it isn't in `Agent Contracts.md`); it's the output of
`analysis/sysml_analyzer.py`, Step 1 in `Modelica Agent.md`, Section 6:
"the agent shouldn't rely only on an LLM to understand the SysML -- use
parser/AST information wherever possible."

Holds *structural* facts recovered from the actual generated `.sysml` text
(part/instance names, connections, requirement/interface/behavior/constraint
names). Numeric/typed values (bounds, units) are not reparsed from the doc
comment they're rendered into -- those are cross-referenced from the
upstream SysML Generation Contract JSON instead, since that's the actual
typed source of truth (see `storage/from_sysml_agent.py`).
"""

from __future__ import annotations

from pydantic import BaseModel


class SysMLPart(BaseModel):
    part_def: str
    instance_name: str


class SysMLConnection(BaseModel):
    source_instance: str
    target_instance: str
    relationship_type: str | None = None


class SysMLRequirement(BaseModel):
    name: str
    doc: str | None = None
    property: str | None = None


class SysMLInterface(BaseModel):
    name: str


class SysMLBehavior(BaseModel):
    name: str
    comment: str | None = None


class SysMLConstraint(BaseModel):
    name: str
    property: str | None = None


class SysMLSemanticModel(BaseModel):
    parts: list[SysMLPart] = []
    connections: list[SysMLConnection] = []
    requirements: list[SysMLRequirement] = []
    interfaces: list[SysMLInterface] = []
    behaviors: list[SysMLBehavior] = []
    constraints: list[SysMLConstraint] = []
