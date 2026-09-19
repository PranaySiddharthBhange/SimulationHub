"""Deterministic connector-domain compatibility. Used by
`validation/connection_validator.py`. Section 12 in `Modelica Agent.md`:
"the actual connector selection must depend on the engineering domain --
for physical systems it could instead involve a fluid, thermal, electrical,
mechanical, or signal connector."

A connection is compatible only when both sides are the same connector
domain -- a signal can't plug into a fluid port, no matter how plausible
an LLM might make it sound. Within SIGNAL, an input must pair with an
output (or an unspecified side, when one end's kind isn't known yet).
"""

from __future__ import annotations

from simulation_platform.tools.library_catalog import CONNECTOR_KINDS


def connector_kinds_compatible(kind_a: str | None, kind_b: str | None) -> bool:
    if kind_a is None or kind_b is None:
        return True  # unknown -- not enough information to flag as incompatible
    if kind_a not in CONNECTOR_KINDS or kind_b not in CONNECTOR_KINDS:
        return False
    return kind_a == kind_b
