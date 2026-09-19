"""Model Planner — LLM stage 1. Mirrors `SysML V2 Agent.md`, Section 6.

The first LLM stage does not generate SysML code. It decides *what* needs
to exist (packages, parts, requirements, interfaces, behaviors) and flags
anything it can't decide as an open question, rather than guessing.
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.sysml_planning import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.skills import with_sysml_skills
from simulation_platform.sysml_gen.config import SETTINGS
from simulation_platform.sysml_gen.llm import run_structured
from simulation_platform.schemas import OpenQuestion, SysMLGenerationContract, SysMLGenerationPlan

_SYSTEM_PROMPT = with_sysml_skills(_BASE_SYSTEM_PROMPT)


class _PlanResponse(BaseModel):
    packages: list[str]
    parts: list[str]
    requirements: list[str]
    interfaces: list[str]
    behaviors: list[str]
    control_laws: list[str] = []
    system_boundary: str = ""
    physical_domains: list[str] = []
    sensors: list[str] = []
    actuators: list[str] = []
    identified_control_laws: list[str] = []
    open_questions: list[OpenQuestion] = []


def create_generation_plan(
    contract: SysMLGenerationContract, generation_id: str, extra_context: str = ""
) -> SysMLGenerationPlan:
    user_prompt = (
        f"Project: {contract.project_id}\n\n"
        f"Entities: {[e.model_dump() for e in contract.entities]}\n\n"
        f"Relationships: {[r.model_dump() for r in contract.relationships]}\n\n"
        f"Requirements: {[r.model_dump() for r in contract.requirements]}\n\n"
        f"Behaviors: {[b.model_dump() for b in contract.behaviors]}\n\n"
        f"Control laws: {[cl.model_dump() for cl in contract.control_laws]}\n\n"
        f"Interfaces: {[i.model_dump() for i in contract.interfaces]}\n\n"
        f"Constraints: {[c.model_dump() for c in contract.constraints]}"
    )
    if extra_context:
        # A retrieval pass over problem.md/documents/ run after a first
        # attempt left open_questions (`new direction.txt` §9/§40: retrieve
        # only when a stage actually discovers it needs something, rather
        # than reading everything up front) -- may resolve some of them.
        user_prompt += f"\n\nAdditional information found by searching the project's own documents:\n{extra_context}"
    response = run_structured(SETTINGS.planning_model, _SYSTEM_PROMPT, user_prompt, _PlanResponse)
    return SysMLGenerationPlan(
        project_id=contract.project_id,
        generation_id=generation_id,
        packages=response.packages,
        parts=response.parts,
        requirements=response.requirements,
        interfaces=response.interfaces,
        behaviors=response.behaviors,
        control_laws=response.control_laws,
        system_boundary=response.system_boundary,
        physical_domains=response.physical_domains,
        sensors=response.sensors,
        actuators=response.actuators,
        identified_control_laws=response.identified_control_laws,
        open_questions=response.open_questions,
    )
