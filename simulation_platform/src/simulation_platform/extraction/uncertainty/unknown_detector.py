"""Unknown detection. Mirrors `Document Agent.md`, Section 35.

An "unknown" is a property that is clearly required (the extractor found a
requirement/constraint referencing it) but for which no source gave a
numeric value. Never invent the missing value — record it as `OPEN` instead.
"""

from __future__ import annotations

from simulation_platform.schemas import Constraint, Requirement, Unknown


def detect_unknowns(requirements: list[Requirement], constraints: list[Constraint]) -> list[Unknown]:
    unknowns: list[Unknown] = []
    counter = 0

    for req in requirements:
        if req.value is None and req.min is None and req.max is None:
            counter += 1
            unknowns.append(
                Unknown(
                    unknown_id=f"UNK-{counter:04d}",
                    property=req.property,
                    entity=req.subject,
                    reason=f"Requirement {req.requirement_id} references this property but no source gives a numeric bound.",
                )
            )

    for con in constraints:
        if con.min is None and con.max is None:
            counter += 1
            unknowns.append(
                Unknown(
                    unknown_id=f"UNK-{counter:04d}",
                    property=con.property,
                    entity=con.subject,
                    reason=f"Constraint {con.constraint_id} references this property but no source gives a numeric bound.",
                )
            )

    return unknowns
