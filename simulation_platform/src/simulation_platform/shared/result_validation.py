"""Result Validation (`new direction.txt` §21-22): "successful compilation
is not enough." Checks the ACTUAL simulated trajectory (from
`compiler/openmodelica_client.py`'s CSV result summary) against the
requirements it was supposed to satisfy, and derives a problem-appropriate
simulation window instead of one hardcoded duration for every problem.

Deliberately domain-neutral -- no Tank/CO2/Magnetic-specific logic. A
NaN/Inf check applies to any system in any domain. A requirement's bound is
checked only via a HIGH-confidence name match to an actual simulated
variable (same "never invent a match" discipline as
`modelica_gen/generation/modelica_generator.py::_render_behavior_equation`)
-- an unmatched requirement is reported as unmatched, never silently
skipped or guessed at.
"""

from __future__ import annotations

import math

from rapidfuzz import fuzz

_COLUMN_MATCH_THRESHOLD = 90.0

_TIME_UNIT_SECONDS = {
    "s": 1.0, "sec": 1.0, "second": 1.0, "seconds": 1.0,
    "min": 60.0, "minute": 60.0, "minutes": 60.0,
    "hr": 3600.0, "hour": 3600.0, "hours": 3600.0,
}


def derive_simulation_window(requirements: list[dict]) -> tuple[float, float, int]:
    """(start_time, stop_time, number_of_intervals), derived from any
    time-valued requirement found in the contract -- §21: "do not hardcode
    one simulation duration for every problem." Falls back to a short,
    explicitly documented default (10s/10 intervals) when nothing
    time-like is found -- an honest fallback, never a fabricated duration."""

    max_seconds = 0.0
    for req in requirements:
        unit = (req.get("unit") or "").strip().lower()
        multiplier = _TIME_UNIT_SECONDS.get(unit)
        if multiplier is None:
            continue
        for key in ("value", "max", "min"):
            raw = req.get(key)
            if isinstance(raw, (int, float)):
                max_seconds = max(max_seconds, abs(raw) * multiplier)

    if max_seconds <= 0:
        return 0.0, 10.0, 10  # nothing time-like found -- the old, documented default

    # A handful of cycles of the slowest identified timed behavior, clamped
    # to a sane range so a real omc run can't hang on an absurd duration.
    stop_time = min(max(max_seconds * 5.0, 10.0), 3600.0)
    return 0.0, stop_time, 100


def evaluate_simulation_result(result_summary: dict[str, dict[str, float]], requirements: list[dict]) -> dict:
    """Returns a report `{"status", "checked", "unmatched", "issues"}` --
    never raises, this informs a human/repair decision rather than gating
    the pipeline on its own.

    status: "PASSED" (something was checked, nothing flagged), "FLAGGED"
    (a NaN/Inf or an out-of-bound requirement was found), or "UNKNOWN"
    (nothing in `requirements` could be confidently matched to a simulated
    variable -- not a failure, just nothing to validate against)."""

    issues: list[str] = []

    for name, stats in result_summary.items():
        for key in ("min", "max", "final"):
            value = stats.get(key)
            if value is not None and (math.isnan(value) or math.isinf(value)):
                issues.append(f"{name}: {key} is {value} -- not a physically meaningful value")

    column_names = list(result_summary.keys())
    checked: list[str] = []
    unmatched: list[str] = []

    for req in requirements:
        subject = req.get("subject") or ""
        prop = req.get("property") or ""
        label = f"{subject} {prop}".strip()
        bound_min, bound_max = req.get("min"), req.get("max")
        if not label or (bound_min is None and bound_max is None):
            continue

        best_match, best_score = None, 0.0
        for name in column_names:
            score = fuzz.token_sort_ratio(label.lower(), name.lower().replace(".", " "))
            if score > best_score:
                best_match, best_score = name, score

        if best_match is None or best_score < _COLUMN_MATCH_THRESHOLD:
            unmatched.append(label)
            continue

        stats = result_summary[best_match]
        checked.append(f"{label} -> {best_match}")
        if bound_max is not None and stats["max"] > bound_max:
            issues.append(f"{label} ({best_match}) reached {stats['max']}, exceeding max {bound_max}")
        if bound_min is not None and stats["min"] < bound_min:
            issues.append(f"{label} ({best_match}) reached {stats['min']}, below min {bound_min}")

    status = "FLAGGED" if issues else ("PASSED" if checked else "UNKNOWN")
    return {"status": status, "checked": checked, "unmatched": unmatched, "issues": issues}
