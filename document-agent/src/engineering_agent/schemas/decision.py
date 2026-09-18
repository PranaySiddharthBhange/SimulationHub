"""Decision ledger. Mirrors `Document Agent.md`, Section 39 and `Agent Contracts.md`, Section 22."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ClarificationRequest(BaseModel):
    question_id: str
    requested_by_agent: str = "engineering_knowledge_agent"
    question: str
    candidates: list[str]
    impact: str
    affects: list[str] = []


class Decision(BaseModel):
    decision_id: str
    question_id: str
    question: str
    answer: str
    source: str = "USER"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    affects: list[str] = []
