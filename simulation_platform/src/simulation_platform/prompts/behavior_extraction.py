"""LLM system prompt for behavior extraction (Stage 1). Used by
`extraction/extraction/behavior_extractor.py`.
"""

SYSTEM_PROMPT = (
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
