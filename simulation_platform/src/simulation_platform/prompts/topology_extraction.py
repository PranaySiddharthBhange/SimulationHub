"""LLM system prompt for HOLISTIC topology extraction (Stage 1). Used by
`extraction/consolidation/topology_cross_check.py`.

Deliberately the ONE place in Stage 1 that breaks the "never send more than
one document's observations to a single LLM call" rule every other
extractor in this package follows (see `extraction/extraction/llm.py`) --
that rule is exactly why no per-document extraction pass can ever see a
connection or a duplicate spanning two different documents. This call is
kept narrow (topology only -- components and connections, nothing else)
specifically so seeing everything at once doesn't reintroduce the
large-single-call truncation risk a full "extract everything holistically"
call would.
"""

SYSTEM_PROMPT = """\
You are given EVERY observation from EVERY document in this project, all \
at once -- unlike the rest of this pipeline's extraction, which only ever \
sees one document at a time. Your ONLY job is to independently identify, \
from your own reading of this combined text, the real physical/logical \
COMPONENTS in this system and the CONNECTIONS between them. Do not \
extract requirements, behaviors, or control laws -- another, separate \
pass already handles those; this pass exists purely as an independent \
cross-check on system topology (what exists, and what's connected to \
what), so a second, differently-scoped reasoning pass can catch a gap \
the per-document extraction might have missed.

RULES
- A COMPONENT is a real physical or logical part a systems engineer would \
model as its own instance (a tank, valve, sensor, controller, actuator, \
zone, source, boundary) -- not a signal, gain, or wiring artifact.
- Use your own best-guess CANONICAL name for each component: prefer a \
formal tag/id if the text uses one (e.g. "TK-101"), otherwise a clear \
descriptive name. If the SAME real component is mentioned under several \
different names ACROSS different documents, list it ONCE, using whichever \
name is most formal/specific, and cite evidence from every document that \
mentions it.
- A CONNECTION is any real physical or signal link the text describes \
between two components (piped together, wired together, one feeding into \
or controlling another). If two different documents describe the SAME \
real connection (even under different component names), report it ONCE.
- Every component and connection must cite at least one bracketed [obs_id] \
as evidence -- never invent one that isn't grounded in the text.
- This is a best-effort independent re-derivation, not an authoritative \
source of truth -- when genuinely unsure whether something is a real \
component or just a signal/mention, leave it out rather than guessing.
"""
