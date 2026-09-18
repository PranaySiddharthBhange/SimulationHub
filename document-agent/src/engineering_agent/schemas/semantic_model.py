"""Semantic model container. Mirrors `Document Agent.md`, Section 40."""

from __future__ import annotations

from pydantic import BaseModel

from .behavior import Behavior
from .constraint import Constraint
from .decision import Decision
from .entity import Entity
from .evidence import Evidence
from .relationship import Relationship
from .requirement import Requirement
from .uncertainty import Ambiguity, Assumption, Conflict, Unknown


class SemanticModel(BaseModel):
    model_version: str
    project_id: str

    entities: list[Entity] = []
    relationships: list[Relationship] = []
    requirements: list[Requirement] = []
    behaviors: list[Behavior] = []
    constraints: list[Constraint] = []

    evidence: list[Evidence] = []

    conflicts: list[Conflict] = []
    ambiguities: list[Ambiguity] = []
    unknowns: list[Unknown] = []
    assumptions: list[Assumption] = []
    decisions: list[Decision] = []
