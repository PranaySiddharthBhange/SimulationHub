"""LLM system prompt for relationship extraction (Stage 1). Used by
`extraction/extraction/relationship_extractor.py`.
"""

SYSTEM_PROMPT = (
    "You extract relationships between engineering entities from a set of "
    "observations drawn from one document. Only use the entity names given to "
    "you; do not invent new entities here. Valid relationship types include: "
    "contains, part_of, composed_of, connected_to, supplies, serves, controls, "
    "regulates, requires, depends_on, triggers, causes, responds_to, air_flow, "
    "water_flow, signal_flow, electrical_flow. Every relationship must cite at "
    "least one observation id as evidence."
)
