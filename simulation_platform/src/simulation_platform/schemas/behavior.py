"""Behavior schema. Mirrors `Document Agent.md`, Section 29."""

from __future__ import annotations

from pydantic import BaseModel

from .common import Comparator, FactStatus


class Behavior(BaseModel):
    behavior_id: str
    trigger_property: str
    trigger_operator: Comparator
    trigger_value: float | str
    trigger_unit: str | None = None
    action_type: str
    action_target: str
    status: FactStatus
    evidence: list[str] = []
