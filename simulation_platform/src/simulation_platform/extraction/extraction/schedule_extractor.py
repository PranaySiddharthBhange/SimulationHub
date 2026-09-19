"""Scheduled-command extraction -- a time-based operator command/event
schedule, distinct from `behavior_extractor.py`'s discrete IF/THEN
interlocks and `control_law_extractor.py`'s continuous relationships. See
`schemas/scheduled_command.py`."""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.schedule_extraction import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import DocumentRecord, FactStatus, Observation, ScheduledCommand

from .id_sequence import IdSequence
from .llm import run_structured_extraction


class _ExtractedScheduledCommand(BaseModel):
    command_name: str
    time_value: float
    time_unit: str | None = None
    expected_response: str | None = None
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _ScheduleExtractionResult(BaseModel):
    scheduled_commands: list[_ExtractedScheduledCommand]


def extract_scheduled_commands(
    document: DocumentRecord, observations: list[Observation], id_seq: IdSequence
) -> list[ScheduledCommand]:
    result = run_structured_extraction(_SYSTEM_PROMPT, document, observations, _ScheduleExtractionResult)
    return [
        ScheduledCommand(
            command_id=id_seq.next("CMD"),
            command_name=item.command_name,
            time_value=item.time_value,
            time_unit=item.time_unit,
            expected_response=item.expected_response,
            status=item.status,
            evidence=item.evidence_observation_ids,
        )
        for item in result.scheduled_commands
    ]
