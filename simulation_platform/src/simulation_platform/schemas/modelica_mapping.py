"""Modelica Mapping Record. Mirrors `Agent Contracts.md`, Section 9, and
`Modelica Agent.md`, Sections 8-13.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ModelicaMappingType(str, Enum):
    MODEL = "MODEL"
    BLOCK = "BLOCK"
    CONNECTOR = "CONNECTOR"
    PARAMETER = "PARAMETER"
    EQUATION = "EQUATION"
    ALGORITHM = "ALGORITHM"
    ASSERTION = "ASSERTION"
    LIBRARY_COMPONENT = "LIBRARY_COMPONENT"


class ModelicaMapping(BaseModel):
    sysml_element: str
    mapping_type: ModelicaMappingType
    target: str  # e.g. "Modelica.Blocks.Interfaces.RealInput" or a local class name
    reason: str
    evidence: list[str] = []

    # Only meaningful for a trigger-based control-behavior EQUATION mapping
    # (an IF/THEN interlock, not a general physical/balance equation).
    # Populated ONLY when the mapper can confidently resolve the behavior's
    # trigger/action to REAL declared identifiers in the generated model --
    # left null otherwise. The generator independently re-verifies both
    # against what was actually declared before ever trusting them (see
    # `generation/modelica_generator.py::_render_behavior_equation` and
    # `skills/modelica_modeling.py`): a wrong-but-confident `when` clause is
    # worse than falling back to a comment, so nothing here is trusted blind.
    trigger_variable: str | None = None  # e.g. "tank1.level" -- must be "<declared_instance>.<field>"
    action_variable: str | None = None  # e.g. "inletValve.opening"
    action_value: str | None = None  # the literal RHS to assign, e.g. "0", "1", "true", "false"

    # Only meaningful for a continuous/proportional control-law EQUATION
    # mapping (see `schemas/control_law.py`) -- distinct from the
    # trigger/action fields above, which are for a discrete IF/THEN
    # behavior. Same "resolve to real identifiers, verify before trusting"
    # discipline as trigger_variable/action_variable -- see
    # `generation/modelica_generator.py::_render_control_law_equation`.
    control_law_type: str | None = None  # PROPORTIONAL | PI | PID | LINEAR
    control_input_variable: str | None = None  # "<declared_instance>.<field>"
    control_output_variable: str | None = None  # "<declared_instance>.<field>"
    control_gain_p: float | None = None
    control_gain_i: float | None = None
    control_setpoint: float | None = None
