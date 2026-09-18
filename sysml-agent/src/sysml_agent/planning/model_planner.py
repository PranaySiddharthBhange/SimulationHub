"""Model Planner — LLM stage 1. Mirrors `SysML V2 Agent.md`, Section 6.

The first LLM stage does not generate SysML code. It decides *what* needs
to exist (packages, parts, requirements, interfaces, behaviors) and flags
anything it can't decide as an open question, rather than guessing.
"""

from __future__ import annotations

from pydantic import BaseModel

from sysml_agent.config import SETTINGS
from sysml_agent.llm import run_structured
from sysml_agent.schemas import OpenQuestion, SysMLGenerationContract, SysMLGenerationPlan

_SYSTEM_PROMPT = """\
You are the Model Planner for a SysML v2 Creator Agent. Given a structured \
engineering knowledge contract, decide the SHAPE of the SysML model to build \
- packages, parts (components), which requirements/interfaces/behaviors to \
represent - WITHOUT writing any SysML syntax yet. That happens in a later stage.

Do not invent requirements, entities, or behaviors that are not in the contract.
If something is genuinely ambiguous (e.g. two entities that might be the same \
part, or a relationship whose architectural meaning isn't clear from the \
contract alone), add it to open_questions instead of guessing.
"""


class _PlanResponse(BaseModel):
    packages: list[str]
    parts: list[str]
    requirements: list[str]
    interfaces: list[str]
    behaviors: list[str]
    open_questions: list[OpenQuestion] = []


def create_generation_plan(contract: SysMLGenerationContract, generation_id: str) -> SysMLGenerationPlan:
    user_prompt = (
        f"Project: {contract.project_id}\n\n"
        f"Entities: {[e.model_dump() for e in contract.entities]}\n\n"
        f"Relationships: {[r.model_dump() for r in contract.relationships]}\n\n"
        f"Requirements: {[r.model_dump() for r in contract.requirements]}\n\n"
        f"Behaviors: {[b.model_dump() for b in contract.behaviors]}\n\n"
        f"Interfaces: {[i.model_dump() for i in contract.interfaces]}\n\n"
        f"Constraints: {[c.model_dump() for c in contract.constraints]}"
    )
    response = run_structured(SETTINGS.planning_model, _SYSTEM_PROMPT, user_prompt, _PlanResponse)
    return SysMLGenerationPlan(
        project_id=contract.project_id,
        generation_id=generation_id,
        packages=response.packages,
        parts=response.parts,
        requirements=response.requirements,
        interfaces=response.interfaces,
        behaviors=response.behaviors,
        open_questions=response.open_questions,
    )
