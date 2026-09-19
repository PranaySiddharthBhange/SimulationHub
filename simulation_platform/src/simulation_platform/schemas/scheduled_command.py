"""Scheduled Command schema. A time-based operator command/event schedule
(e.g. a test procedure's "at 20s, START; at 220s, STOP; at 700s, SHUT") --
distinct from `Behavior` (a discrete IF/THEN interlock triggered by a
measured property) and `ControlLaw` (a continuous relationship): this is an
externally-imposed simulation stimulus, not a property of the system being
modeled. Found live: a real Tank test procedure specified an exact command
schedule and a benchmark ground-truth trace, but the generated model had no
way to represent it at all -- every named command variable (`startCmd`,
`stopCmd`, `shutCmd`) was left permanently `false` (an honestly-labeled
placeholder, but one that made the whole simulation physically inert: the
controller never left its initial state and no tank level ever changed).
"""

from __future__ import annotations

from pydantic import BaseModel

from .common import FactStatus


class ScheduledCommand(BaseModel):
    command_id: str
    command_name: str  # e.g. "START", "STOP", "SHUT" -- matched against a variable name downstream
    time_value: float
    time_unit: str | None = None
    expected_response: str | None = None  # free text, e.g. "Begin or resume automatic operation"
    status: FactStatus
    evidence: list[str] = []
