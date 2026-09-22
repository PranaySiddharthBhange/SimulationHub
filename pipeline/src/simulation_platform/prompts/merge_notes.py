"""LLM system prompt for merging Stage 1's independently-written
per-document understanding notes into ONE coherent system understanding.
OpenAI-backed (see `reasoner_pipeline.py::execute_merge`) -- the
user's explicit choice: local models handle the cheap, high-volume
per-document reading, OpenAI handles this harder cross-document reasoning
step.

Also the ONE place `domains` gets classified (see `contracts.Understanding.
domains` and `skills/domains.py`): Merge is the first point in the pipeline
with a full, cross-document view of the whole system -- Stage 1 reads one
document/chunk at a time and could not classify reliably.
"""

from simulation_platform.skills.domains import DOMAIN_SKILLS

_DOMAIN_LIST = "\n".join(f"- {key}" for key in DOMAIN_SKILLS)

MERGE_PROMPT = f"""\
You are given a set of "working notes" written independently, one per \
document (or one per page-sized chunk of a large document), by another \
agent that read each document on its own without seeing the others. \
Because each note was written in isolation, the SAME real component may \
appear under different names in different notes (e.g. a casual nickname, \
an abbreviation, and a formal equipment tag/id could all refer to the \
SAME real thing). Numbers, units, and conditions may also be repeated, \
restated, or occasionally appear to conflict across notes written from \
different documents.

Your job is to read ALL of these notes together and produce ONE coherent, \
resolved understanding of the whole system:

- Resolve every instance of the same real component to ONE consistent \
name/id (prefer a formal tag/id over an informal nickname when both \
appear for the same real thing) -- never invent a new name that isn't \
grounded in the notes.
- Merge relationships/connections that describe the same real link, even \
if worded differently across notes.
- Reconcile apparent conflicts using the same original-evidence-is-
authoritative discipline an engineer would use: a later revision or an \
explicit correction wins over an earlier draft; when you genuinely can't \
tell which is right, say so explicitly rather than picking arbitrarily.
- An explicit statement that names a value and says it should NOT be used, \
is deprecated, or is superseded (e.g. "the archived source's values should \
not be used as configuration authority") IS a clear resolution of that \
conflict -- treat it as decisive, not as merely one \
more opinion to weigh. Do NOT resolve a conflict by counting how many \
notes repeat a value: the same stale value can appear in many places \
simply because it propagated to those documents BEFORE the correction was \
made -- repetition is not evidence of correctness, and a single explicit \
correction outweighs several passive repeats of the value it corrects.
- Determine what's actually needed to model and simulate this system: \
what components, what equations (from the physical laws/relationships \
described), what conditions/events, what initial/boundary values, what \
the acceptance criteria are.
- You are the ONE point in this pipeline with a full, cross-document view of \
the whole system -- Stage 1 wrote each note from a single document/chunk in \
isolation and could not check any of this. Actively use that full view: \
derive every equation you state from the real physical/logical relationships \
the notes describe (never state one that merely looks standard for the kind \
of system this appears to be), verify units are consistent wherever a value \
feeds an equation, and check that resolved components/values don't imply a \
contradiction (e.g. a stated capacity smaller than a stated initial content, \
a control law referencing a quantity nothing produces). Surface a genuine \
inconsistency you find as a `question` -- don't silently smooth it over, and \
don't invent the missing piece that would make it consistent.

Write the resolved system understanding as the `narrative` field -- \
prose, with clear structure, using ONLY the consistent, resolved naming \
you decided on. This narrative (plus `checks`/`assumptions`/`questions`/ \
`domains` below) is the ONLY thing Stage 2 and Stage 3 ever read about \
this system -- they never see the individual per-document notes you were \
given, only what you write here. Write it as a comprehensive, detailed \
technical description, not a condensed executive summary: include every \
real component and its resolved name, every resolved parameter with its \
value and unit, every connection/topology relationship, every equation, \
every discrete state and transition with its guard condition, every \
schedule entry, and every acceptance criterion the notes establish -- \
each one you have, not a representative sample. When you're unsure \
whether a real, grounded detail is worth including, include it: an \
omitted detail is one Stage 2/3 will never see and can never recover, \
while an extra sentence costs nothing. This does not license inventing \
anything ungrounded -- it means do not compress or drop a detail that IS \
actually established in the notes for the sake of brevity. Populate \
`simulation`, `checks`, `assumptions`, and `questions` from what the notes \
actually established. Flag anything genuinely ambiguous or unresolved as \
a `question` rather than guessing.

Populate `domains` with whichever of the following general engineering \
domains genuinely apply to this system (zero, one, or several -- a batch \
process that also evaporates a liquid is both, a simple single-domain \
system is one):

{_DOMAIN_LIST}

Pick only what the system actually is; leave `domains` empty rather than \
force-fitting one of these onto a system that doesn't clearly match any of \
them. This selects which general domain knowledge later stages get handed \
-- it is never a substitute for anything in the narrative itself.
"""
