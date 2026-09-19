"""State Machine synthesis -- composing a SET of already-extracted discrete
Behaviors into a coherent state-machine (states + ordered transitions),
distinct from `_render_behavior_equation`'s job of rendering ONE isolated
trigger/action pair. Recognizing that "wait 10s before opening V2" belongs
between a FILL and a TRANSFER state, in that order, is a narrative/
ordering question -- genuinely a better fit for LLM reasoning than
deterministic pattern-matching (see the turn that decided this).

Same safety discipline as everywhere else in this pipeline: the LLM
proposes states/transitions referencing only real behavior/requirement ids
and real declared variable/parameter names it was actually given -- it
never invents a state name or a Modelica identifier. The generator
independently re-verifies every reference (state names against the
target enum's REAL declared literals, ids against what was actually
extracted) before ever rendering a transition as real code; anything
unresolvable is dropped with a disclosed comment, never guessed.
"""

from __future__ import annotations

from pydantic import BaseModel


class StateTransition(BaseModel):
    from_state: str
    to_state: str

    # Gates this transition on an already-extracted Behavior's condition --
    # `condition_variable` must be a real variable/parameter name declared
    # in the SAME reused legacy class (e.g. "tank1Level"), never a guess;
    # the actual operator/threshold come from the behavior record itself,
    # not re-typed here (same "don't re-derive what's already known"
    # discipline as `trigger_variable` elsewhere in this pipeline).
    trigger_behavior_id: str | None = None
    condition_variable: str | None = None

    # OR gates this transition on a timed wait after entering `from_state`
    # -- `wait_parameter_id` is a real requirement/parameter id whose bound
    # value is the wait duration in seconds, never a fabricated number.
    wait_parameter_id: str | None = None

    reason: str = ""


class StateMachine(BaseModel):
    state_machine_id: str
    # The exact enum type name this state machine belongs to (e.g.
    # "StepState") -- matched against a never-assigned discrete variable's
    # own declared type; a state machine whose states don't exactly match
    # that type's real declared literals is rejected wholesale, not
    # partially guessed.
    target_type_hint: str
    states: list[str]
    initial_state: str
    transitions: list[StateTransition] = []
    reason: str = ""
