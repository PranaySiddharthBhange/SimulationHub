"""SysML Generation Contract. Mirrors `Agent Contracts.md`, Section 2.

Produced by the Engineering Knowledge Agent, consumed here. This is the
input boundary for the whole SysML Agent — nothing downstream ever reads
raw source documents.
"""

from __future__ import annotations

from pydantic import BaseModel

from .common import Comparator, FactStatus, VersionRef


class RequirementItem(BaseModel):
    id: str
    subject: str
    property: str
    operator: Comparator
    value: float | str | None = None
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    status: FactStatus
    evidence: list[str] = []


class EntityItem(BaseModel):
    id: str
    name: str
    type: str
    status: FactStatus
    evidence: list[str] = []


class RelationshipItem(BaseModel):
    source: str
    target: str
    type: str
    evidence: list[str] = []


class BehaviorItem(BaseModel):
    id: str
    trigger_property: str
    trigger_operator: Comparator
    trigger_value: float | str
    trigger_unit: str | None = None
    action_type: str
    action_target: str
    status: FactStatus
    evidence: list[str] = []


class ConstraintItem(BaseModel):
    id: str
    subject: str
    property: str
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    evidence: list[str] = []


class InterfaceItem(BaseModel):
    id: str
    name: str
    kind: str
    source_entity: str
    target_entity: str
    evidence: list[str] = []


class EvidenceRecord(BaseModel):
    evidence_id: str
    document_id: str
    quote: str | None = None


class SysMLGenerationContract(BaseModel):
    project_id: str
    version: VersionRef

    requirements: list[RequirementItem] = []
    entities: list[EntityItem] = []
    relationships: list[RelationshipItem] = []
    behaviors: list[BehaviorItem] = []
    constraints: list[ConstraintItem] = []
    interfaces: list[InterfaceItem] = []

    evidence: list[EvidenceRecord] = []
