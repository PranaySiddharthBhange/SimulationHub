# Engineering Knowledge / Document Agent

Implementation of the Document Agent specified in
`../Agentic Engineering Spec/Document Agent.md`. Built with Python,
LangGraph, and Deep Agents.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on Linux/macOS
pip install -e ".[dev]"
cp .env.example .env            # then fill in OPENAI_API_KEY
```

## Running against a golden dataset

```bash
python scripts/ingest_project.py iaq_001 "IAQ Control System" \
    "../test cases/iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset"
```

This creates `projects/iaq_001/` and runs the full LangGraph ingestion
workflow (`workflows/ingestion_graph.py`): discovery → classification →
parsing → indexing → semantic extraction → entity resolution →
reconciliation → uncertainty detection → quality check → (HITL interrupt
if needed) → publish.

## What's verified right now, without an API key

Everything except semantic extraction (LLM step, Section 25 of the spec)
and the Deep Agent's own reasoning is deterministic and has been run
against **all four golden datasets** (IAQ, Magnetic Circuit, NaCl
Evaporation, Tank) in `tests/`:

```bash
pytest tests/ -v
```

- `test_deterministic_pipeline.py` — discovery, classification, and all 10
  deterministic parsers (PDF, DOCX, XLSX, CSV, JSON, EML, Markdown, TXT,
  Modelica, PlantUML) against every real file in every dataset. The only
  expected failure is the `.png` architecture diagrams, which require the
  vision-based `image_parser` (needs `OPENAI_API_KEY`).
- `test_ingestion_graph_boundary.py` — runs the *actual* LangGraph
  workflow (not just its functions) against every dataset, confirms every
  node up through `build_indexes` persists correctly to disk, and that the
  graph fails with a precise `ExtractionUnavailable` — not a confusing
  crash — exactly at the point where an LLM is genuinely required.
- `test_non_llm_components.py` — entity resolution (fuzzy merge +
  ambiguity/assumption detection), conflict detection and precedence
  resolution (including the "an approved decision email outranks a
  formal register entry" rule), unknown detection, and every JSON/JSONL
  persistence round-trip.
- `test_retrieval_and_indexes.py` — the four semantic indexes
  (entity/requirement/relationship/evidence) and the full retrieval API,
  both as plain Python and as the LangChain tools handed to the Deep Agent.

31/31 tests pass as of this build.

## Run logs

Every `ingest_project.py` run writes a local JSONL trail —
`projects/<id>/logs/run_<timestamp>_<id>.jsonl` — of every graph node,
tool call, and LLM call, via `observability/run_logger.py`. This is built
on LangChain's `BaseCallbackHandler` (no dedicated "LangGraph logging"
library exists — checked first, see `DECISIONS.md` D12), attached through
`config={"callbacks": [...]}`. Each line is one event:
`node_start`/`node_end`/`node_error`, `tool_start`/`tool_end`/`tool_error`,
`llm_start`/`llm_end`/`llm_error`.

## Extraction budget cap

Every `ingest_project.py` run is protected by `observability/budget_guard.py`
— an estimated-cost cap on LLM spend, $2 by default
(`ENGINEERING_AGENT_BUDGET_USD`), that stops the run *before* the next LLM
call once the cap is hit, rather than after the fact. Built on the same
callback mechanism as the run logger, with one thing confirmed empirically
before relying on it: `BaseCallbackHandler` swallows exceptions raised
inside its own hooks unless `raise_error = True` is set — without that, a
callback that "raises" to stop a run does nothing. Verified live with an
artificially tiny budget: the run stopped after exactly 2 LLM calls. The
per-token prices used for the estimate are a documented placeholder, not
real billing data (see the module docstring) — override via
`ENGINEERING_AGENT_PRICE_PER_1K_INPUT_USD` / `..._OUTPUT_USD` if you know
your account's actual rates.

## Verified end-to-end with a real key (2026-09-18)

Ran the full pipeline for real, one dataset at a time on purpose, to find
real bugs cheaply before touching any other agent or any other dataset.

**IAQ/CO2 (first run)** — found three bugs, all fixed the same day (see
`DECISIONS.md` D13-D14 and `AI-LOG.md` Cases 1-4): a nonexistent default
model name (`gpt-5.1-mini` → `gpt-5.4-mini`), a frozen-settings snapshot
that silently broke test isolation the moment a real key existed (now
reads `os.environ` live), and semantic extraction hallucinating entities
and nonsensical "behaviors" out of diagram/Modelica wiring (tightened the
extraction prompts; entities 143→110, behaviors 40→22, ambiguities 73→41).
After fixing: 14/14 files parsed including the PNG diagram via vision, a
real cross-document conflict correctly detected and left `OPEN`, and the
`EngineeringKnowledgeAgent` correctly cited real requirement/evidence ids
(including the DR-IAQ-05 design decision from the email thread) and
correctly reported the conflict as unresolved rather than picking a value.

**Tank / Two-Tank Controller (second run, different domain on purpose)** —
found two more real bugs specific to this dataset's conventions (see
`DECISIONS.md` D15-D16 and `AI-LOG.md` Case 5):
- Short instrument tag codes (`LT-101`, `TK-101`, `PLC-101`, `SRC-101`)
  inflated plain string-similarity to ~77-83/100 purely from a shared
  numeric suffix, producing 68+ false "same entity?" ambiguities between
  unrelated equipment classes. Fixed `resolution/entity_resolution.py` to
  compare tag prefixes separately from instance numbers.
- The conflict engine invented a false safety-interlock contradiction:
  two real requirements ("V2/V3 open together: prohibited" under
  `condition="normal auto operation"`, "...: allowed" under
  `condition="SHUT"`) were compared as competing claims because grouping
  ignored the `condition` field entirely. The Deep Agent, asked directly,
  gave a confident, well-cited, **wrong** answer. Fixed
  `reconciliation/conflict_engine.py` to group by `(subject, property,
  condition)`, not just `(subject, property)`.

After both fixes: 12/12 files parsed, ambiguities 125→44, conflicts 7→3
on a from-scratch re-run, completing unattended (no HITL pause) — and the
two conflicts that remain (a reference-run timing discrepancy) are real.

## What still needs `OPENAI_API_KEY` to verify

- The same pipeline on the remaining two golden datasets (Magnetic
  Circuit, NaCl Evaporation) — only IAQ and Tank have been run live so far.
- A HITL resume actually being answered — a run *has* now paused for
  real (see `DECISIONS.md` D16), but every run since has completed
  unattended, so `Command(resume=...)` remains wired but unexercised.

Re-run `python scripts/ingest_project.py ...` on any dataset for a full
end-to-end run, and use `agent.py` to ask investigation-mode questions
against the published knowledge.

## Known simplifications (called out honestly, not hidden)

- Retrieval is backed directly by the project's JSON/JSONL files rather
  than SQLite. Same API as the spec describes (`retrieval/tools.py`) —
  swapping in SQLite later doesn't change any caller.
- Entity resolution is pure string-similarity (`rapidfuzz`); it correctly
  merges near-duplicate spellings but does **not** resolve abbreviation
  expansions (e.g. "AHU-01" vs "Air Handling Unit 1") — that needs the
  LLM-assisted resolution path the spec calls out as a fallback.
- The Modelica and PlantUML parsers are pragmatic regex-based extractors,
  not full grammars/ASTs (explicitly noted as an acceptable simplification
  in `Document Agent.md`).
- Ambiguity/unknown detection currently covers what's mechanically
  checkable (missing numeric bounds, type-mismatched near-duplicate
  entities); free-text ambiguity detection (e.g. "the heating system"
  could mean three different things) is not yet implemented and would be
  another LLM-backed extractor, following the same pattern as
  `extraction/entity_extractor.py`.
- Conflict detection compares raw values and does not normalize units —
  confirmed on the real IAQ run: an outdoor CO2 value given as 300 ppm in
  one source and 0.0004557 kg/kg in another (the same physical value)
  gets flagged as an unresolved conflict rather than recognized as
  consistent. Correct, conservative behavior (never silently pick one),
  but not the ideal outcome — needs a unit-aware comparison in
  `reconciliation/conflict_engine.py`.
- Entity extraction runs independently per document with no shared
  type vocabulary carried between documents, so the same real-world thing
  can get a different guessed `type` in different documents and trigger a
  same-name-different-type ambiguity that a shared context would have
  avoided. Reduced substantially by the Case 4 prompt fix, not eliminated
  by it — a residual characteristic of the per-document batching design,
  not a bug.
- A handful of extracted requirements are still narrative/architectural
  statements with no real numeric bound (e.g. "system topology == provide
  outdoor air through the supply path") rather than true measurable
  constraints, despite the tightened prompt — reduced from roughly half
  of all extracted requirements to a small minority, not fully eliminated.
