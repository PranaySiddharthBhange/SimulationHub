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

## How to read these notes

Each note begins with a `Subject:` line and a `Document kind:` line, then uses
only these headings: Entities, Relationships, Requirements, Behaviors,
Constraints, Physical relationships, Control laws, Scheduled commands. Within
them the extraction has ALREADY recorded what you would otherwise have to infer:

- A value appears under its entity as `- quantity: value unit [status]`, where
  the status is what that document claims for it -- current, approved, nominal,
  as_built, measured, observed, proposed, archived or superseded -- and
  `(supersedes/superseded: ...)` names what it replaces or is replaced by.
- `<REF [page N]>` or `<REF [sheet X]>` after an item is the document's own
  identifier for it and where in the document it was found. Carry a requirement
  id through into the `source` of any check derived from it.
- A missing status means the document genuinely did not say; treat it as
  unknown rather than assuming current.

Use these tags as given. Do not re-derive a value's standing from the prose
when the tag already states it, and do not overrule a tag because a different
note repeats the number more often.

## Which document wins

`Document kind` tells you how much weight a statement carries, and that is the
main tool for resolving a conflict. In descending authority: an approved or
released requirement specification and a formal test procedure or acceptance
criterion govern; an engineering register or datasheet supplies component data;
a design note or review minute records intent and decisions; correspondence
records discussion; an operator log or recorded dataset records what someone
observed on one occasion; a legacy model is prior art that may predate every
change record.

So a requirement and a test procedure agreeing outrank an operator's
observation that contradicts them, and the observation is then recorded as
conflicting evidence rather than as the resolved behaviour. Authority is not
absolute -- an explicit later change record beats an older approved value of
any kind -- but never resolve a conflict by counting how many notes repeat a
value.

## Recorded runs are evidence about the past, not requirements

A note whose kind is a dataset and whose facts are marked `[observed]`
describes one run that already happened. It is legitimate, and often decisive,
to use it to settle which documented value is the current one: if two notes
disagree over a setpoint and the recorded run reaches exactly one of them, say
so and resolve it, citing the run.

It is NOT a requirement and NOT a model input. Never copy an observed
trajectory into `checks` as though the model were required to reproduce it
sample by sample, never treat a recorded command column as the commanded
schedule, and never let observed values replace a stated requirement that
disagrees with them -- record that disagreement instead. Classify such a table
as `reference`, never as `input`.

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

Systems differ in kind, and the brief must describe the kind this one actually
is. Some are sequenced and command-driven; others are continuous, quasi-static
or purely algebraic, driven only by a prescribed input with no discrete states,
no operator commands and no actuators at all. Do not impose a sequential
control structure on a system whose notes do not contain one, and do not go
looking for commands, modes, interlocks or safety overrides that the notes
never mention.

Where the notes DO establish discrete behavior, write every state and
transition as a complete unit: entry trigger, state, output or actuator
command, guard, wait or duration, exit condition, next state, and command
priority. Preserve ordered procedures and phase-specific completion
conditions, along with any pause, resume, abort, reset, inhibit, priority,
mutual-exclusion or simultaneous-command rules the notes establish, using the
names the notes themselves use.

## Preserve continuous behavior and physical meaning

Include every evidence-grounded equation, conservation relationship,
proportional law, initial condition, boundary condition, and unit. Distinguish
continuous relationships from discrete control decisions. Do not complete an
incomplete equation or invent a missing parameter.

## Simulation, tables, and acceptance

Populate `simulation` from explicitly established start time, stop time,
interval, and tolerance values. Classify each table as `input`, `reference`,
or `supporting` only when the notes establish its role; do not treat a reference
trajectory as a model input. Preserve required reports, logged variables,
scheduled commands, experiment duration, and output windows.

### Declare the reported variables, then write checks against them

FIRST, in the narrative, declare the exact set of variable names the model will
report, one per reported quantity, with its unit and meaning. Prefer names the
notes already use for reported outputs; otherwise choose short, legal
identifiers and state them explicitly. This list is a contract: later stages
name their model outputs from it, and every check is written over it.

THEN write each acceptance criterion as an expression over those names.
`checks` is the only mechanically evaluable thing this brief produces -- a
result file is compared against it directly -- so an entry that reads as an
English sentence cannot be evaluated at all and is worthless. Confirmed live:
the same instruction produced a ratio of two reported variables against an
expected number on one dataset, and a plain English restatement of the
criterion on another. Only the first can ever be checked.

- Write a comparison, not a description: `quantity_a >= 0.80` rather than "the
  quantity reaches its stated limit".
- For a condition that must hold, make the expression Boolean and set
  `expected` to 1.0. Combine conditions with and/or/not, for example
  `not (output_a > 0.5 and output_b > 0.5)`.
- `kind` is `final` for the end of the run, `at` with `at_time` for a stated
  instant, and `always` for something that must hold throughout.
- CHECK THAT THINGS HAPPEN, not only that they never go wrong. A set made only
  of bounds and exclusions -- a value never exceeded, two outputs never active
  together -- is satisfied perfectly by a model that does nothing at all, and
  such a model has passed a real compiler and a real simulation before while
  producing no behaviour whatsoever. For every stated target, threshold,
  transition or completion condition, include a check that FAILS if it never
  occurs: the quantity actually reaching its setpoint, the sequence actually
  arriving in its final state, the stage actually starting. Pair each bound
  with the attainment it is meant to bound.
- Put the note filename and the requirement id from its `<REF ...>` tag into
  `source`, and make it the id of the requirement that actually states THIS
  criterion. Do not attach whichever id happened to be nearby: a criterion
  about a level limit does not cite the requirement that fixes the run
  duration. If no id covers it, name the note alone rather than a wrong id.
- Do not write two checks that assert the same thing. Each entry should be
  able to fail for a reason no other entry already covers.
- Use the tolerance the evidence states. When none is stated, set one the
  quantity's own precision justifies rather than demanding exact equality.
- A criterion you cannot express over the reported variables is one the later
  stages cannot verify: state it in the narrative instead, and do not invent a
  numeric check to stand in for it.

For every material unresolved decision, populate both `questions` with a short
question string and `clarifications` with one structured record. Each
clarification record must have a stable id, the full question, the evidence
behind the conflict, all evidence-supported options, and a suggested value.

A question is only admissible when the conflict it describes is actually
present in these notes. Every clarification must name the specific notes and
the specific competing values or statements it arose from, and every element it
mentions must be one the notes actually contain. Never raise a question about a
component, command, mode or behavior this system does not have -- asking which
actuator a purely algebraic system commands, or what its shutdown sequence is,
is a fabricated question even though it sounds like diligence. If the notes
leave nothing materially unresolved, return no questions at all rather than
manufacturing plausible ones.
Use the best-supported candidate as the suggestion when any note identifies it
as approved, effective, current, applicable, or the active acceptance value,
even when older evidence keeps the question open. Leave `suggested_value` empty
only when no candidate has stronger support than the others. Never invent an
option or a suggested value; preserve every supported alternative in `options`.

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
