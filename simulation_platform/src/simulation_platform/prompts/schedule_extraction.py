"""LLM system prompt for scheduled-command extraction (Stage 1). Used by
`extraction/extraction/schedule_extractor.py`.
"""

SYSTEM_PROMPT = (
    "You extract SCHEDULED COMMANDS -- an explicit, time-stamped operator "
    "command or event schedule (e.g. a test procedure's 'at 20 s, issue START' "
    "or 'at 700 s, issue SHUT') -- from a set of observations drawn from one "
    "document. This is DISTINCT from a behavior (a discrete IF/THEN rule "
    "triggered by a measured property, e.g. 'close the valve when level > 8m') "
    "and from a control law (a continuous relationship): a scheduled command is "
    "an externally-imposed stimulus at a stated point in time, not a property of "
    "the system responding to itself.\n\n"
    "Only extract one when the document states an actual number for the time "
    "and an actual named command/event -- never invent a time or a command name "
    "that isn't written down. A table with a 'Time' column and a 'Command' "
    "column (or equivalent prose, e.g. 'at t=20s the operator presses START') is "
    "exactly the shape to look for. Every scheduled command must cite at least "
    "one observation id as evidence."
)
