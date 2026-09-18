"""Entity schema. Mirrors `Document Agent.md`, Section 26."""

from __future__ import annotations

from pydantic import BaseModel

from .common import FactStatus


class Entity(BaseModel):
    entity_id: str
    name: str
    type: str
    status: FactStatus
    evidence: list[str] = []
    aliases: list[str] = []
