"""SysML Element Mapping. Mirrors `Agent Contracts.md`, Section 4."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class SysMLConstruct(str, Enum):
    PART_DEF = "part def"
    PART = "part"
    REQUIREMENT_DEF = "requirement def"
    REQUIREMENT = "requirement"
    INTERFACE_DEF = "interface def"
    PORT_DEF = "port def"
    ACTION_DEF = "action def"
    STATE_DEF = "state def"
    CONSTRAINT_DEF = "constraint def"
    ATTRIBUTE = "attribute"
    CONNECTION = "connection"


class SysMLElementMapping(BaseModel):
    engineering_id: str
    engineering_type: str
    sysml_construct: SysMLConstruct
    sysml_element_name: str
    package: str
    rationale: str = ""
    evidence: list[str] = []
