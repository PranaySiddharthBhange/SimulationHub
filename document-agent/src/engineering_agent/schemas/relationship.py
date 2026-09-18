"""Relationship schema. Mirrors `Document Agent.md`, Section 27."""

from __future__ import annotations

from pydantic import BaseModel

from .common import FactStatus


class Relationship(BaseModel):
    relationship_id: str
    source: str                 # Entity.entity_id
    target: str                 # Entity.entity_id
    type: str                   # contains | connected_to | controls | supplies | ...
    status: FactStatus
    evidence: list[str] = []
