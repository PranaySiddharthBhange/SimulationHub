"""SysML Generation Plan. Mirrors `Agent Contracts.md`, Section 3.

Produced by the Model Planner (LLM stage 1). Planning and code generation
are kept as separate stages on purpose — see `SysML V2 Agent.md`, Section 6.
"""

from __future__ import annotations

from pydantic import BaseModel

from .common import OpenQuestion


class SysMLGenerationPlan(BaseModel):
    project_id: str
    generation_id: str

    packages: list[str]
    parts: list[str]
    requirements: list[str]
    interfaces: list[str]
    behaviors: list[str]
    control_laws: list[str] = []  # engineering ids of ControlLawItem entries to map, like `behaviors` above

    # Real system-reasoning output (`new direction.txt` §10), not just the
    # shape decision above -- what's in/out of scope, which physical domains
    # are involved, and which contract elements are sensors/actuators/control
    # laws. Grounded in the contract, never invented; flows into the central
    # `ResolvedSystemModel` (see `shared/system_model_builder.py`). Short
    # descriptive labels, NOT engineering ids -- distinct from `control_laws`
    # above, which is the shape-decision list of ids to actually map.
    system_boundary: str = ""
    physical_domains: list[str] = []
    sensors: list[str] = []
    actuators: list[str] = []
    identified_control_laws: list[str] = []

    open_questions: list[OpenQuestion] = []
