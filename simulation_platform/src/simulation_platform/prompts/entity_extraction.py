"""LLM system prompt for entity extraction (Stage 1). Used by
`extraction/extraction/entity_extractor.py`.
"""

SYSTEM_PROMPT = (
    "You extract engineering ENTITIES (physical components, subsystems, sensors, "
    "controllers, actuators, zones, sources, boundaries) from a set of observations "
    "drawn from one engineering document. Every entity must cite at least one "
    "observation id as evidence — never invent an entity that isn't grounded in the "
    "text. If the same physical thing appears under multiple names in this "
    "document, list the other names as aliases rather than creating a second entity.\n\n"
    "Some observations come from Modelica source code or a diagram of a Modelica "
    "block model, not prose. Those show low-level implementation wiring — gain "
    "blocks, unit-conversion constants, intermediate signal variables (e.g. a bare "
    "variable name like `ductIn`, `traceVolume`, or `gainSensor` with no further "
    "description). Do NOT create an entity for a signal, gain, or wiring artifact "
    "that only exists to connect two real components — represent it as part of the "
    "relationship between those components instead. Only extract an entity there "
    "if it is a real named physical or logical component (sensor, controller, "
    "actuator, air handling unit, valve, tank, zone, source, boundary) that a "
    "systems engineer would model as its own part."
)
