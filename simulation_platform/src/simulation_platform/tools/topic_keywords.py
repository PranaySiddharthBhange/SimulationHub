"""Deterministic keyword -> topic tagging (Stage 1 document indexing). Data
only, no logic -- the matching/compilation lives in
`tools/extraction/index_builder.py`. Extend this dict as new domains are
added; it never invents a topic that isn't literally present in the text.
"""

TOPIC_KEYWORDS: dict[str, str] = {
    r"\bco2\b": "CO2_CONTROL",
    r"\btemperature\b|\bdegc\b": "TEMPERATURE_CONTROL",
    r"\boccupan": "OCCUPANCY",
    r"\bflux\b|\bmagnetic\b|\breluctance\b": "MAGNETIC_CIRCUIT",
    r"\bnacl\b|\bevaporat": "EVAPORATION_PROCESS",
    r"\btank\b|\blevel\b": "TANK_LEVEL_CONTROL",
    r"\bvalve\b|\bpump\b": "FLUID_ACTUATION",
    r"\bcommissioning\b|\bacceptance\b": "COMMISSIONING",
}
