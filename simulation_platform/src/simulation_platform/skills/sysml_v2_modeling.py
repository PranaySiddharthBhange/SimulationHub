"""Meta-skill: SysML v2 modeling conventions. Appended to Stage 2 (SysML
generation/reasoning) prompts. Distills real, live-found lessons from
building and debugging this pipeline against a real SysML v2 parser (the
Eclipse SysML v2 Pilot Implementation) -- see DECISIONS.md D19, D21, D30-D34
-- into forward-looking guidance, so a future run doesn't have to
rediscover the same syntax gotchas live.
"""

SKILL = """\
SKILL: SysML v2 modeling conventions (verified against the real Eclipse SysML v2 \
Pilot Implementation parser, not just the language spec).

CORE CONSTRUCTS AND WHEN TO USE THEM
- `part def X { ... }` / `part x : X;` -- a physical or logical system \
component. Use this for anything a systems engineer would draw as a box: \
tanks, valves, sensors, controllers, rooms, coils, cores.
- `requirement def X { attribute p : T; doc /* ... */ }` -- a measurable, \
bounded constraint on a property. There is no other valid construct for a \
requirement; do not represent one as a plain attribute on a part.
- `interface def X { end a : PortT; end b : PortT; }` -- a typed connection \
point between parts (signal, fluid, thermal, electrical, mechanical). \
Model the physical medium of the interface, not just "a wire" generically.
- `action def X { ... }` -- an if/then control rule or a discrete behavior \
step. `state def X { entry; exit; states s1, s2; transition s1 to s2; }` -- \
a real state machine, when the system has one (most sequenced/interlocked \
systems do).
- `constraint def X { ... }` -- a bounded-range invariant, distinct from a \
single-threshold requirement.
- `connect a to b;` -- a real structural connection. BOTH ENDPOINTS MUST BE \
PART-TYPED (declared via `part`/`part def`). Connecting to a `state def` or \
any non-part-typed element is not valid and the real parser will reject it \
as an unresolvable reference -- render it as a comment instead of guessing \
a resolution.

REAL SYNTAX GOTCHAS (found live against the real parser, not from reading the spec)
- A bare `Real` type reference is ambiguous across the many auto-loaded \
domain libraries the pilot implementation ships with. Use the fully \
qualified `ScalarValues::Real` for a numeric attribute type instead of a \
bare `Real` -- confirmed empirically as the one form that resolves cleanly \
across every tested case.
- Identifiers must be legal SysML names: letters, digits, underscore, no \
spaces, not starting with a digit. A property name derived from free \
engineering text (e.g. "wait time after Tank 1 reaches high level") must \
be sanitized into a legal identifier before being emitted -- never embed \
the raw phrase as an attribute name.
- Two different concepts (e.g. a requirement and a constraint both about \
the same real-world quantity) must never be given the identical \
(name, package) pair, even when they describe the same idea -- pick a \
distinct, still-descriptive name for each. Independently mapping many \
items in one large batch is a common way this collision slips through; \
track which (name, package) pairs are already claimed and check against \
them before picking a new one.
- Do not fabricate `connect()` topology for a relationship whose \
endpoints you can't confidently resolve to real parts -- a guessed \
connection that references a name the model never actually declared will \
fail the real parser outright (a dangling/unresolvable reference), which \
looks confidently correct until it's actually checked.

VALIDATION DISCIPLINE
Always validate against the REAL SysML v2 parser (the Eclipse Pilot \
Implementation's own grammar and standard library), not a hand-rolled \
regex or brace-counter -- a regex-based check can confirm balanced braces \
and legal-looking identifiers, but only the real parser can confirm the \
model actually resolves (every type reference exists, every `connect()` \
endpoint is real, every inherited feature is valid). Treat "the real \
parser accepts it" as the pass/fail gate before ever handing the model to \
the next stage.
"""
