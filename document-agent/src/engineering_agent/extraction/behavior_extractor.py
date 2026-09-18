"""Behavior extraction. Mirrors `Document Agent.md`, Section 29."""

from __future__ import annotations

from pydantic import BaseModel

from engineering_agent.schemas import Behavior, Comparator, DocumentRecord, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction

_SYSTEM_PROMPT = (
    "You extract IF-THEN control behaviors from a set of observations drawn "
    "from one document (e.g. 'IF CO2 > 1000 ppm THEN increase ventilation'). "
    "A behavior is a condition on a measured/monitored property that triggers a "
    "control response — not a description of static wiring or structure.\n\n"
    "Some observations come from Modelica source code or a diagram of a Modelica "
    "block model. A `connect(a, b)` statement, an arrow between two blocks in a "
    "diagram, or an equation that just assigns one signal to another (e.g. "
    "`ductIn = freshAir`) describes topology, not a behavior — do NOT extract "
    "those as behaviors. Only extract a real behavior from code when there is an "
    "actual conditional or control law: a comparison against a threshold, a "
    "min/max clamp, a PID-style expression, or an explicit if/then. Represent the "
    "trigger as a property/operator/value/unit and the action as a type + "
    "target. Only extract behaviors that are explicitly stated. Every behavior "
    "must cite at least one observation id as evidence."
)


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
