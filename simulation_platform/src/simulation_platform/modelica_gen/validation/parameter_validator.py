"""Layer 5 -- Parameter validation. Mirrors `Modelica Agent.md`, Section
22: "Are parameter values valid?" Two independent checks: every generated
`parameter` declaration actually has a value (not blank), and every
requirement bound with both a min and a max is internally sane (min <=
max) before it ever reaches generation.
"""

from __future__ import annotations

import re

from simulation_platform.schemas import ModelicaValidationIssue, ValidationLayer

_PARAMETER_DECL = re.compile(r"parameter\s+\w+\s+(\w+)\s*(?:\([^)]*\))?\s*=\s*([^;]*);")


def validate_parameter_values(filename: str, text: str) -> list[ModelicaValidationIssue]:
    issues: list[ModelicaValidationIssue] = []
    for match in _PARAMETER_DECL.finditer(text):
        name, value = match.groups()
        if not value.strip():
            issues.append(
                ModelicaValidationIssue(
                    layer=ValidationLayer.PARAMETER, element=name,
                    message=f"Parameter '{name}' in {filename} has no value.",
                )
            )
    return issues


def validate_parameter_bounds(requirement_bounds: list[dict]) -> list[ModelicaValidationIssue]:
    issues: list[ModelicaValidationIssue] = []
    for bound in requirement_bounds:
        min_value, max_value = bound.get("min"), bound.get("max")
        if min_value is not None and max_value is not None and float(min_value) > float(max_value):
            issues.append(
                ModelicaValidationIssue(
                    layer=ValidationLayer.PARAMETER,
                    element=f"{bound.get('subject')}.{bound.get('property')}",
                    message=f"min ({min_value}) is greater than max ({max_value}).",
                )
            )
    return issues
