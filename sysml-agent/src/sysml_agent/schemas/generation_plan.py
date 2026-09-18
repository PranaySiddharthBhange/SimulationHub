"""SysML Generation Plan. Mirrors `Agent Contracts.md`, Section 3.

Produced by the Model Planner (LLM stage 1). Planning and code generation
are kept as separate stages on purpose — see `SysML V2 Agent.md`, Section 6.
"""

from __future__ import annotations

from pydantic import BaseModel


class OpenQuestion(BaseModel):
    question_id: str
    question: str
    candidates: list[str]
    blocks: list[str] = []


class SysMLGenerationPlan(BaseModel):
    project_id: str
    generation_id: str

    packages: list[str]
    parts: list[str]
    requirements: list[str]
    interfaces: list[str]
    behaviors: list[str]

    open_questions: list[OpenQuestion] = []
