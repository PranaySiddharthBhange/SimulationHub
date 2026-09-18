# SysML v2 Creator Agent

Implementation of the agent specified in
`../Agentic Engineering Spec/SysML V2 Agent.md`. Consumes the Document
Agent's published knowledge (via `storage/from_document_agent.py`, which
reads its `semantic_model.json` as plain JSON — no cross-package import)
and produces a SysML v2 model plus its traceability record.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[dev]"
cp .env.example .env   # then fill in OPENAI_API_KEY
```

### Optional: real SysML v2 syntax validation

Layer 1 syntax validation defaults to the real Eclipse SysML v2 Pilot
Implementation parser when it's installed locally, falling back
automatically to the regex-based checker when it isn't (see
`validation/real_syntax_validator.py` and `DECISIONS.md`). To install it:

```bash
winget install EclipseAdoptium.Temurin.21.JDK   # or any JDK >= 21
winget install Anaconda.Miniconda3
conda create -n sysml python=3.11 jupyterlab graphviz nodejs jupyter-sysml-kernel -c conda-forge
```

No config needed beyond that — `find_kernel_dir()` looks for the `sysml`
conda env's kernel directory automatically. Set
`SYSML_AGENT_USE_REAL_PARSER=false` to force the regex fallback (e.g. for
speed), or `SYSML_AGENT_KERNEL_DIR` to point at a non-default kernel
install location.

## Running

```bash
python scripts/generate_sysml.py iaq_001
```

Looks for `../document-agent/projects/iaq_001/semantic/semantic_model.json`
by default (override with a second argument). Runs the LangGraph workflow:
`build_generation_contract -> create_generation_plan (LLM) -> map_elements
(LLM) -> generate_sysml -> validate_generation -> publish_version`, with a
human-review interrupt on a validation failure.

## What's verified right now, without an API key

Everything except the model planner and the semantic mapper (both
genuinely need an LLM, per `SysML V2 Agent.md` Sections 6-7) is
deterministic and tested in `tests/` — 21/21 passing:

- `test_generation_and_validation.py` — the SysML text generator and all
  four deterministic validation layers (syntax, structural, requirement
  coverage, traceability), including two deliberately broken inputs
  (a dangling relationship reference, a mapping pointing at an
  undeclared package) to confirm the validators actually catch them.
- `test_storage_and_adapter.py` — every JSON round-trip, and the adapter
  that converts a Document Agent `semantic_model.json` into a
  `SysMLGenerationContract`.
- `test_graph_boundary.py` — runs the *actual* LangGraph workflow,
  confirms `build_generation_contract` persists correctly, and that the
  graph fails with a precise `LLMUnavailable` — not a crash — exactly at
  the planning stage.
- `test_run_logger.py` — the same local JSONL run-logging as the Document
  Agent (`observability/run_logger.py`, built on LangChain's
  `BaseCallbackHandler`), confirming it captures the deterministic node
  and the exact failing node's name on error.
- `test_budget_guard.py` — the same hard spending cap as the Document
  Agent (`observability/budget_guard.py`), plus a regression guard for the
  "`gpt-5.1-mini` doesn't exist" bug found live in the Document Agent (see
  below) — fixed here before this agent ever ran with a real key.
- `test_real_syntax_validator.py` — the real SysML v2 pilot parser
  integration (kernel start, valid input, and a deliberately broken input
  checked for the correct file *and* line number). Skips automatically
  when the local conda kernel isn't installed, so it never blocks a
  dependency-free run — but it *did* run and pass here, since the kernel
  is installed on this machine.

## Extraction budget cap

Same mechanism as the Document Agent: `observability/budget_guard.py`
caps estimated LLM spend at $2 by default (`SYSML_AGENT_BUDGET_USD`),
stopping the run before the next LLM call once hit. Built on
`BaseCallbackHandler` with `raise_error = True` set explicitly — without
that, LangChain silently swallows an exception raised inside a callback
and the guarded call would proceed anyway (verified empirically in the
Document Agent build; not re-verified against a live call here, but it's
the identical code).

## What needs `OPENAI_API_KEY` to verify

- `planning/model_planner.py` — decides packages/parts/requirements/etc.
  to represent, without writing SysML yet.
- `mapping/element_mapper.py` — maps each engineering concept to a SysML
  v2 construct (`part def`, `requirement def`, ...).
- `validation/semantic_validator.py` — Layer 5, "did the generated SysML
  preserve the contract's engineering meaning?"

Once a key is set, run `scripts/generate_sysml.py` against a project the
Document Agent has actually ingested with a key (so `semantic_model.json`
exists) for a full end-to-end run.

**Fixed pre-emptively, not yet live-verified in this agent:** the default
model for all three stages was `gpt-5.1-mini`, which doesn't exist for
this account (confirmed against `/v1/models` — only `gpt-5.1` does, no
mini variant). This exact bug was found live in the Document Agent (see
`DECISIONS.md`); fixed here to `gpt-5.4-mini` before this agent's LLM
stages were ever run for real, rather than waiting to hit it too.

## Verified end-to-end with a real key

Run against the Tank dataset (`tank_003` — 67 entities, 159 requirements,
73 behaviors, 73 constraints), the largest and messiest of the four
golden datasets. The first live run surfaced five real, independent bugs
in about twenty minutes of iteration — none reachable by the deterministic
test suite, since every hand-built fixture is necessarily cleaner than
real data in exactly the ways that mattered here (see `DECISIONS.md`
D29-D33 for each one: a single mapping call silently dropping whole
categories on a large contract, a dangling `connect()` to a non-part
mapping, a free-text property phrase embedded as a raw SysML identifier,
a namespace-ambiguous `Real` reference, and a within-category name
collision). After fixing all five, a clean re-run produced:

```
mappings_created: 372   (100% of entities + requirements + behaviors + constraints)
validation_status: PASSED   (0 syntax errors, 0 structural errors, 159/159 requirement coverage, 0 traceability errors)
Estimated LLM spend: $0.0496 over 5 calls
```

validated against the *real* SysML v2 pilot parser (`validation/
real_syntax_validator.py`), not the regex fallback.

## Known simplifications

- Real syntax validation (`validation/real_syntax_validator.py`) only runs
  when the local SysML v2 pilot kernel is installed. When it isn't,
  `validate_generation()` falls back to `validation/syntax_validator.py`,
  a regex-based checker that only catches what's checkable without that
  toolchain (balanced braces, legal identifiers) — not a substitute for
  the real parser, just a floor.
- Auto-repair (spec Section 19: classify a validation failure, LLM-repair,
  re-validate, bounded retries) is not wired in yet. A validation failure
  currently routes straight to a human-review interrupt instead of an
  automatic repair loop — see `DECISIONS.md` for the scope call behind
  this, matching the hackathon's push to get one path working end-to-end
  before generalizing further.
- Interfaces are not yet produced by the Document Agent as a distinct
  fact type, so `SysMLGenerationContract.interfaces` is always empty from
  the adapter today; interface generation (`Interfaces.sysml`) works from
  hand-built test fixtures but has no real upstream data yet.
