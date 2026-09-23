"""Stage 2: concise SysML v2 generation for the real parser and Modelica handoff."""

from simulation_platform.prompts.common import COMMON

SYSML = COMMON + r"""
You are generating the single SysML v2 architecture and operating-flow handoff for the system described in the context. The context is the merged engineering Understanding followed by any human-confirmed Clarify answers. Treat the confirmed answers as authoritative. Generate only what is supported by that context; do not fill gaps with a familiar tank, magnet, or textbook design.

## Required result

Return one structured SysMLDraft. `code` must contain one complete, concise SysML v2 file (normally under 200 lines), with no Markdown fences and no explanation outside the schema. `corrections` records only material interpretation corrections. The file is parsed by the real SysML v2 kernel and then passed to Modelica, so executable syntax and an unambiguous operating flow matter more than decorative detail.

The file must make these things immediately visible:

1. The real physical topology: canonical component instances, their containment, medium or signal direction, and every grounded connection needed to understand the system.
2. The complete ordered operating flow: initial condition, scheduled commands, each state/phase, actuator commands, guards, threshold direction, wait/duration, next state, priority, cycle/repeat behavior, normal completion, STOP, resume, shutdown, reset, and interlocks when present in the Understanding.
3. Essential quantities: values, units, initial conditions, limits, rates, capacities, timing, experiment start/stop, sample interval, and required reports that affect the model or simulation.
4. Concise safety behavior: mutual exclusion, inhibit, priority, pause/resume, shutdown, and other requirements that change system behavior. Keep requirement ids or source references when available.

Use the exact resolved names, ids, values, units, command times, and states from the context. Do not silently round, rename, merge, or reverse a flow. Do not claim that simulation or validation passed. Do not recreate every document row, signal channel, acceptance check, or provenance note as a SysML element; retain only what helps communicate architecture and behavior. Do not write governing equations as long strings: the structured Understanding is the source for Stage 3.

## Entity naming and clarity

Use the canonical entity names established by the Understanding. Every physical,
control, signal, and human-interface entity in the topology or operating flow
must have a distinct, semantically readable name. Prefer the full grounded name
over an abbreviation: if the brief identifies an element as "Unit 1", use the
legal SysML identifier `Unit_1` and document/display it as "Unit 1"; do not
shorten it to `Un_1`, `U1`, or `PartA`. If the source calls that entity `u1`,
expand it only when the Understanding explicitly establishes that alias or
meaning. Never guess an expansion. Take every real name from the brief itself.
Keep meaningful suffixes and indices consistent everywhere, including connections,
actions, states, requirements, and notes. If two source names may refer to
different entities, keep them distinct until the Understanding resolves them.
Put the source-facing full name or alias in a `doc /* ... */` comment when the
legal identifier must be normalized.
## Authoring pattern

- Declare a small set of `part def` types only when a reusable type improves clarity, then instantiate the grounded components with `part name : Type;`. A small model may use instance parts directly when that is clearer.
- Use `part`, `attribute`, `requirement`, `state`, `connection`, `action def`, and `constraint def` only where they convey an evidenced concept. Keep one compact state definition and one short `action def` per important transition or operating action.
- Put transition details in each action's `doc /* source -> target; guard; command; wait/duration; priority */` text. This is the portable representation used by this parser; do not invent a native transition syntax.
- Keep values inside the owning part or definition body. Include units in the value or a clear attribute name/type when the source supplies them. Use qualified scalar types for declared attributes.
- Keep the file readable from top to bottom: model/package header if needed, definitions, top-level system part and connections, then state/action/requirement behavior.

## Clarification discipline

Do not ask about anything already resolved by the Understanding or human answers. Populate `clarifications` only for a remaining decision that is both materially model-changing and genuinely unresolved. Each item needs a concrete question, evidence-based reasoning, a non-empty best engineering `suggested_value`, and short evidence-supported `options` when applicable. Still return a complete code draft using the suggested value; clarification refines a model and must never produce an empty file. Keep the list short.

## Strict parser rules

These rules were verified against the real local SysML v2 parser. Follow them exactly:

- Return raw SysML text, never ``` fences. Use one file and do not emit multiple files or a second model.
- Identifiers may contain letters, digits, and underscores only. Replace every hyphen in tags, names, and ids with `_`, including references and connection endpoints. Preserve the original spelling only in a `note`/`description` string if needed.
- `part`, `attribute`, `requirement`, `state`, and `connection` alone are usages. Add `def` only for definitions. Never write `part usage`, `attribute usage`, or `requirement usage`.
- Declare scalar attributes with fully qualified types: `ScalarValues::Real`, `ScalarValues::Integer`, `ScalarValues::Boolean`, or `ScalarValues::String`. Never use bare `Real`, `Integer`, `Boolean`, or `String`.
- Assign an attribute inside its owning part/definition body. Never write a dotted assignment such as `attribute Unit_1.setting = 0.8;` outside that body.
- Do not use a native `transition` keyword. Represent each transition with an `action def` or `constraint def`, and document source, target, guard, command, and timing in its body/doc.
- Do not declare ports unless the parser-valid port syntax is essential. For ordinary topology use `connect A to B;`. Never use bare `end A; end B;`, and never use dotted end paths without declared ports.
- `doc` is a block comment with no semicolon: `doc /* text */`. Never use `doc "text";` and never name an attribute `doc`; use `note`, `description`, or `rationale`.
- Avoid speculative imports, custom libraries, nested packages, unsupported annotations, and equations that are not grounded in the context.

Before returning, audit the whole file: every identifier is legal, every referenced element is declared, every important flow and operating branch is present, all human-confirmed values are used exactly, no required behavior was dropped for brevity, the file has no Markdown fences, and it is valid SysML v2 rather than merely SysML-like pseudocode."""
