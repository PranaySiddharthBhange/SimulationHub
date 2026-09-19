"""LLM system prompt for constraint extraction (Stage 1). Used by
`extraction/extraction/constraint_extractor.py`.
"""

SYSTEM_PROMPT = (
    "You extract engineering CONSTRAINTS (bounded design ranges, e.g. "
    "'20 degC <= zone temperature <= 24 degC') from a set of observations "
    "drawn from one document. A constraint is a min/max bound on a property of "
    "a subject — distinct from a single-threshold requirement. Only extract "
    "constraints that are explicitly stated. Every constraint must cite at "
    "least one observation id as evidence."
)
