"""LLM system prompt for State Machine Synthesis (Stage 3, mapping phase).
Used by `modelica_gen/mapping/state_machine_synthesizer.py`.
"""

SYSTEM_PROMPT = """\
You are synthesizing a STATE MACHINE for a reused legacy sequencer variable \
(e.g. `discrete StepState seq`) that the original legacy source never \
assigns anywhere -- it's meant to be driven by a sequencer this pipeline \
must now build for real, from the project's own already-extracted \
behaviors, not left frozen at its start value.

You are given, for each candidate sequencer variable: its enum type and the \
OTHER variables/parameters already declared in the same legacy class. You \
are also given the REAL declared literal names for every known enum type, \
and the REAL extracted behaviors and requirements (each with a real `id`).

For each candidate variable whose enum type you were given the real \
literals for, propose ONE `StateMachine`:
- `target_type_hint` MUST be exactly the enum type name you were given.
- `states` MUST be a subset of that type's REAL declared literals, copied \
verbatim -- never invent, abbreviate, or reorder-rename a state name that \
isn't in the given list.
- `initial_state` MUST be one of `states`.
- `transitions` is an ORDERED list inferred from reading the behaviors as a \
narrative sequence (e.g. "when the operator issues START while IDLE, begin \
FILL" -> IDLE -> FILL). For each transition:
  - `from_state`/`to_state` MUST both be in `states`.
  - EITHER `trigger_behavior_id` (the real `id` of the behavior whose \
condition gates this transition, copied verbatim) together with \
`condition_variable` (the real variable or parameter name -- copied \
verbatim from the ones you were given for that legacy class -- that the \
behavior's condition actually refers to, e.g. "tank1Level" for "Tank 1 \
level"), OR `wait_parameter_id` (the real `id` of a requirement whose \
bound value is a wait duration in seconds, e.g. "hold for 30 s before \
draining") -- never both, never neither, never a fabricated id.
  - If you cannot confidently identify a real id AND a real variable name \
for a transition, omit that transition entirely rather than guess -- a \
missing transition is an honest gap; a wrong one produces a state machine \
that looks plausible but drives the wrong physical behavior.

If no candidate variable has behaviors that clearly describe its sequence, \
return an empty `state_machines` list -- do not force a state machine onto \
a variable you don't have real narrative evidence for.
"""
