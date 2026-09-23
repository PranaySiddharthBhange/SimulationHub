"""Structured prompt for consolidating independent Stage 1 understanding notes."""

from simulation_platform.prompts.common import COMMON
from simulation_platform.skills.domains import DOMAIN_SKILLS

_DOMAIN_LIST = "\n".join(f"- {key}" for key in DOMAIN_SKILLS)

MERGE_SPECIFIC_INSTRUCTIONS = f"""You are consolidating independent Stage 1 understanding notes into one
resolved engineering brief. The context contains only those notes, separated
by their generated filenames. The original documents are not available to
you. A detail omitted from every note cannot be recovered: do not reconstruct
it from a filename, a domain stereotype, or a standard textbook design.

Return the structured Understanding object required by the caller. Its JSON
fields are the handoff consumed by later stages; do not replace the fields with
free-form prose or add an unrequested schema.

## Consolidate entities and aliases

Create one canonical identity for every real physical, logical, control, or
human-interface element grounded in the notes. Merge abbreviations, informal
names, formal tags, and aliases only when the evidence supports that they are
the same element. Preserve useful aliases in the narrative. Do not merge two
elements merely because their names look similar.

## Consolidate topology and relationships

Include every grounded connection, containment relation, material flow,
signal flow, dependency, control relation, trigger, and direction. Preserve
the medium and endpoint names when stated. Do not infer a connection from two
names appearing in the same table or from adjacent columns.

## Resolve values and revisions

For each parameter, limit, unit, timing value, command priority, and state
value, retain the candidate values found in the notes and determine whether
each is current, approved, observed, nominal, archived, proposed, or
superseded. Select a final value only when the evidence resolves it. Explain
the resolution in the narrative or assumptions, and put a material unresolved
conflict in questions. Never decide by majority count.

## Preserve behavior and sequence

Write every discrete state and transition as a complete unit: entry trigger,
state, actuator or output command, guard, wait or duration, exit condition,
next state, and command priority. Preserve ordered procedures and phase-specific
completion conditions. Keep STOP, resume, SHUTDOWN, reset, inhibit, interlock,
and simultaneous-command behavior wherever the notes establish it.

## Preserve continuous behavior and physical meaning

Include every evidence-grounded equation, conservation relationship,
proportional law, initial condition, boundary condition, and unit. Distinguish
continuous relationships from discrete control decisions. Do not complete an
incomplete equation or invent a missing parameter.

## Simulation, tables, and acceptance

Populate `simulation` from explicitly established start time, stop time,
interval, and tolerance values. Populate `checks` only with acceptance checks
grounded in the notes, keeping their exact expression, expected value,
tolerance, timing, and provenance. Classify each table as `input`, `reference`,
or `supporting` only when the notes establish its role; do not treat a reference
trajectory as a model input. Preserve required reports, logged variables,
scheduled commands, experiment duration, and output windows.

## Narrative and uncertainty

Write `narrative` as a comprehensive technical brief, not an executive
summary. Use one consistent naming scheme and include all resolved entities,
parameters, topology, equations, states, transitions, schedules, requirements,
and acceptance behavior needed by later modeling stages. Do not omit a detail
because it is repeated across notes; merge duplicates once while retaining the
meaning and strongest provenance. Use `assumptions` only for necessary,
explicitly disclosed modeling choices. Use `questions` for any ambiguity that
could materially change the model. Never silently invent a resolution.

## Final completeness audit

Before returning, check that every important fact from every note is either:
(a) represented once in the resolved brief, (b) represented as a resolved
conflict, (c) recorded as an assumption, or (d) recorded as an open question.
Check especially final sentences, page or sheet markers, numeric values with
units, command schedules, report requirements, aliases, and stated absences.
Do not add a catch-all section outside the Understanding schema.

Populate `domains` with only the genuinely applicable general engineering
domains from this list. Leave it empty when none is clearly supported:

{_DOMAIN_LIST}

Domain selection supplies general knowledge to later stages; it never replaces
problem-specific evidence in `narrative`.
"""

MERGE_PROMPT = COMMON + "\n\n" + MERGE_SPECIFIC_INSTRUCTIONS
