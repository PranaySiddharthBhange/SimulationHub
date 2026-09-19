"""Layer 4 -- Unit validation. Mirrors `Modelica Agent.md`, Section 22:
"Are units compatible?" and Section 11's "using proper Modelica units/types
rather than silently treating everything as dimensionless."

A small allow-list of real Modelica/SI unit strings actually used across
the four golden datasets, not a full unit-algebra checker -- this catches
an obviously-wrong or malformed unit string, not a dimensional-analysis
error inside an equation (that would need a real unit-propagation engine,
out of scope here; the real compiler catches those anyway).
"""

from __future__ import annotations

import re

from simulation_platform.schemas import ModelicaValidationIssue, ValidationLayer
from simulation_platform.tools.unit_tables import RECOGNIZED_UNITS as _RECOGNIZED_UNITS

_PARAMETER_UNIT = re.compile(r'parameter\s+\w+\s+(\w+)\s*\([^)]*unit\s*=\s*"([^"]*)"')


def validate_units(filename: str, text: str) -> list[ModelicaValidationIssue]:
    issues: list[ModelicaValidationIssue] = []
    for match in _PARAMETER_UNIT.finditer(text):
        name, unit = match.groups()
        if unit and unit not in _RECOGNIZED_UNITS:
            issues.append(
                ModelicaValidationIssue(
                    layer=ValidationLayer.UNIT, element=name,
                    message=f"Unit '{unit}' on parameter '{name}' in {filename} is not a recognized unit string.",
                )
            )
    return issues
