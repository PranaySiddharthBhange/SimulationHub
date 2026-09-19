"""Behavior extraction. Mirrors `Document Agent.md`, Section 29."""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.behavior_extraction import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import Behavior, Comparator, DocumentRecord, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction


class _ExtractedBehavior(BaseModel):
    trigger_property: str
    trigger_operator: Comparator
    trigger_value: float | str
    trigger_unit: str | None = None
    action_type: str
    action_target: str
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _BehaviorExtractionResult(BaseModel):
    behaviors: list[_ExtractedBehavior]


def extract_behaviors(document: DocumentRecord, observations: list[Observation], id_seq: IdSequence) -> list[Behavior]:
    result = run_structured_extraction(_SYSTEM_PROMPT, document, observations, _BehaviorExtractionResult)
    return [
        Behavior(
            behavior_id=id_seq.next("BEH"),
            trigger_property=item.trigger_property,
            trigger_operator=item.trigger_operator,
            trigger_value=item.trigger_value,
            trigger_unit=item.trigger_unit,
            action_type=item.action_type,
            action_target=item.action_target,
            status=item.status,
            evidence=item.evidence_observation_ids,
        )
        for item in result.behaviors
    ]
