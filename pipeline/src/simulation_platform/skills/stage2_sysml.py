"""Stage 2: SysML v2 generation. Extends `prompts.common.COMMON` with the
SysML-specific authoring order and a real-parser-confirmed syntax discipline
(every rule below was found live against the actual SysML v2 kernel parser).
"""

from simulation_platform.prompts.common import COMMON

SYSML = COMMON + """
Stage 2: generate ONE deliberately concise textual SysML v2 file. Its job is to be
the readable architecture and operating-flow handoff to Modelica, not a second copy
of the entire engineering brief. Keep it to the point (normally under 200 lines):

1. SYSTEM FLOW -- declare only the distinct physical components needed to show the
   real topology, then connect their instances in physical flow order. For a staged
   two-vessel process this should read visually as source -> valve -> first vessel ->
   valve -> second vessel -> valve -> sink. Use exact resolved equipment ids.
2. OPERATING FLOW -- declare one compact state definition containing only the real
   operating states. Add one short action definition per transition, with a doc that
   states `source -> target`, the guard, and any wait duration. This is the primary
   content: a reader should immediately see which tank/branch operates, when it stops,
   and what operates next.
3. ESSENTIAL VALUES -- retain only values that define topology, transition guards,
   flow rates, capacities, initial conditions, or simulation behavior. Do not repeat
   instrumentation metadata, correspondence history, deprecated values, or every
   acceptance check as large prose attributes.
4. SAFETY EXCEPTIONS -- retain concise requirements only for behavior that changes
   the flow (pause/resume, shutdown, mutual exclusion, priority). Preserve a source
   requirement id when one exists, but do not emit a requirement object for every
   numeric check; those checks already remain in the structured understanding.

Do not create a part for every signal channel, document mention, requirement, state,
or acceptance row. Do not embed governing equations as long strings: Stage 3 receives
the structured understanding directly. Avoid unnecessary interfaces, nested packages,
and speculative imports. Always write scalar
attribute types fully qualified -- `ScalarValues::Real`, `ScalarValues::Integer`,
`ScalarValues::Boolean`, `ScalarValues::String` -- never bare (`Real`, `Boolean`, ...
alone fail: "Couldn't resolve reference to Type", confirmed directly against the real
parser; an `import` doesn't fix it either, just write the qualified form every time).
Prefer a small readable model over a framework. Return raw code, without Markdown
fences. Report material corrections to the understanding in corrections; do not
silently propagate a wrong interpretation.

CLARIFICATIONS -- a human engineer is available to answer genuinely unresolved
questions before this design is used further. Populate `clarifications` ONLY for a
decision that is both materially significant to the model AND actually unresolved
in the brief -- never for something the brief already states, never for a routine
engineering default, and never as a substitute for your own reasoning. For each one,
give: the concrete question, why it's unresolved (`reasoning`), and your own best
engineering `suggested_value` -- never leave `suggested_value` empty, since it is
what a reviewer sees pre-filled as the default answer. Optionally list a short set of
`options` when the decision is naturally a pick from a few discrete alternatives.
Regardless of whether a human ever answers, still write a complete, valid `code`
right now that USES your `suggested_value` for each open item, so the model is always
immediately usable and a clarification only ever refines it, never blocks it. Keep
this list short -- a handful of real, high-leverage decisions, not a checklist of
every minor unknown.

SYNTAX DISCIPLINE (this real parser is strict; use the forms below, confirmed to
parse, over other valid-looking SysML v2 you may know):
- No hyphens in identifiers -- a real-world tag with hyphens parses as
  subtraction. Convert every hyphen to underscore EVERYWHERE that tag appears
  (parts, requirements, connections, doc strings), not just at first declaration.
  Keep the original hyphenated form in a note string if useful; the identifier
  itself must never contain one.
- Never write "usage" as a keyword ("part usage", "attribute usage", "requirement
  usage" are all wrong). "part"/"attribute"/"requirement"/"state"/"connection" used
  ALONE already mean a usage; only "<keyword> def" declares a definition. Use
  `part PartA : TypeA;` / `attribute level : Real;` with the brief's real names,
  never `part usage ...`.
- Give an attribute its resolved value INSIDE the owning part's own body
  (`part PartA : TypeA { attribute someProperty = 1.20; }`), never as a separate
  dotted statement outside it (`attribute PartA.someProperty = 1.20;` fails).
- No native `transition` construct -- it's NOT valid in this parser and breaks
  parsing for the rest of the file. Represent each transition as an `action def`
  (or `constraint def`) naming its source state, guard, and target in plain text.
  Bare `state <Name>;` usages are fine; only the `transition` keyword is banned.
- A bare `end A; end B;` connection ALWAYS fails ("Must have at least two related
  elements"), no matter how many ends. Use `connect A to B;` instead. Never a
  dotted port path on an end (`end PartA.out;` fails -- no ports are declared).
- `doc` takes `/* block comment */` with NO trailing semicolon -- never
  `doc /* text */;`, never `doc "text";`. A quoted string is only valid as an
  ordinary attribute's value (`attribute note = "text";`).
- Never name an attribute `doc` -- it is a reserved word, not a usable identifier
  (`attribute doc : String;` fails outright). Use a different name for a free-text
  attribute, e.g. `note`, `description`, or `rationale`.
"""
