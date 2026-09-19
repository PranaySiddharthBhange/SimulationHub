"""Modelica Generation Plan -- internal to the Modelica Agent (Model Planner
stage -> mapping stages). Not a boundary contract in `Agent Contracts.md`
(that document only formalizes the *SysML* plan, Section 3); this mirrors
the identical role for Modelica, per `Modelica Agent.md` Section 29's
`ModelicaState.generation_plan`.
"""

from __future__ import annotations

from pydantic import BaseModel

from .common import OpenQuestion


class ModelicaGenerationPlan(BaseModel):
    project_id: str
    generation_id: str

    packages: list[str]
    components: list[str]  # engineering_id references, part-typed
    properties: list[str]  # engineering_id references, requirement-typed
    behaviors: list[str]
    control_laws: list[str] = []
    constraints: list[str]

    open_questions: list[OpenQuestion] = []
