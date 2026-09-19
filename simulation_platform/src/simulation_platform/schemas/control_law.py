"""Control Law schema. A continuous/proportional control relationship --
distinct from `Behavior` (a discrete IF/THEN interlock: a single threshold
comparison triggering a discrete action). "Increase ventilation
proportionally to CO2 excess" or "the valve opening is proportional to the
level error" is not expressible as a Comparator/trigger_value/action_target
triple; it's a continuous functional relationship between two properties,
optionally with an integral term, so it needs its own shape rather than
overloading `Behavior`'s.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .common import FactStatus


class ControlLawType(str, Enum):
    PROPORTIONAL = "PROPORTIONAL"
    PI = "PI"
    PID = "PID"
    LINEAR = "LINEAR"  # a stated linear relationship with no explicit gain terminology


class ControlLaw(BaseModel):
    control_law_id: str
    law_type: ControlLawType

    controlled_property: str  # what this law computes/adjusts (the output)
    input_property: str  # what it reacts to (the measured/error signal)

    # Only ever populated from an explicitly stated number -- never a
    # fabricated "reasonable" gain. A missing gain means this can't be
    # rendered as a real equation later (see modelica_generator.py); it
    # stays a disclosed gap, not a guess.
    gain_p: float | None = None
    gain_i: float | None = None
    gain_d: float | None = None
    setpoint: float | str | None = None
    setpoint_unit: str | None = None

    status: FactStatus
    evidence: list[str] = []
