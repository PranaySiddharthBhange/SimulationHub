"""LLM vision prompt for diagram/image parsing (Stage 1). Used by
`extraction/parsers/image_parser.py`.
"""

VISION_PROMPT = (
    "You are looking at an engineering architecture/control diagram. "
    "Extract every labeled component and every directed connection between "
    "components, exactly as drawn — do not infer connections that are not "
    "visibly present. Return strict JSON."
)
