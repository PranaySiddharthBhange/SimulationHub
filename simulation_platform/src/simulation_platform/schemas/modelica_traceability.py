"""Modelica Traceability Record. Mirrors `Agent Contracts.md`, Section 12,
and `Modelica Agent.md`, Section 21.
"""

from __future__ import annotations

from pydantic import BaseModel


class ModelicaTraceEntity(BaseModel):
    engineering_id: str
    sysml_element: str
    modelica_class: str
    file: str


class ModelicaTraceRequirement(BaseModel):
    requirement_id: str
    sysml_requirement: str
    modelica_elements: list[str] = []  # e.g. "Controller.CO2Limit"
    evidence: list[str] = []


class ModelicaTraceability(BaseModel):
    modelica_version: str
    sysml_version: str
    knowledge_version: str
    entities: list[ModelicaTraceEntity] = []
    requirements: list[ModelicaTraceRequirement] = []
