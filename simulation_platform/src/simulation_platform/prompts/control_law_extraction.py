"""LLM system prompt for control law extraction (Stage 1). Used by
`extraction/extraction/control_law_extractor.py`.
"""

SYSTEM_PROMPT = (
    "You extract engineering CONTROL LAWS -- continuous/proportional control "
    "relationships -- from a set of observations drawn from one document. A "
    "control law is DISTINCT from a behavior: a behavior is a discrete IF/THEN "
    "interlock ('IF level > 8m THEN close valve'); a control law is a continuous "
    "functional relationship between a measured/error signal and a controlled "
    "output ('fan speed shall be proportional to the CO2 excess above setpoint', "
    "'valve opening = Kp * level error, with Kp = 0.5'). Do NOT extract a "
    "control law for a discrete threshold interlock -- that belongs to behavior "
    "extraction instead.\n\n"
    "Only extract a control law when the document states BOTH which property "
    "is controlled and which property drives it. Only populate a gain "
    "(gain_p/gain_i/gain_d) or a setpoint when the document states an actual "
    "number for it -- never invent a plausible-sounding gain or setpoint value. "
    "If the document only says 'proportional control shall be used' with no "
    "number given, extract the control law with law_type=PROPORTIONAL and leave "
    "gain_p null -- do not guess a value merely to fill the field.\n\n"
    "law_type is PROPORTIONAL for a pure P law, PI if an integral term is "
    "explicitly mentioned (e.g. 'proportional-integral control', 'steady-state "
    "error shall be eliminated via integral action'), PID if a derivative term "
    "is also explicitly mentioned, or LINEAR for a stated linear relationship "
    "that isn't described in P/I/D terms at all. Every control law must cite at "
    "least one observation id as evidence."
)
