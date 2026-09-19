# Simulation platform

Read an engineering source packet, understand the complete problem, generate one
SysML v2 model, and generate and verify one executable Modelica model.

The implementation has been rebuilt around whole-problem reasoning. The previous
per-document extraction graphs, fixed entity mappings, domain catalogs, component
stubs, and multi-file code templates have been removed from the production path.
The removed source and tests are recoverable from `legacy-pipeline-backup.zip`.
Existing input datasets and old project results have been preserved.

## How it works

1. **Understand:** read the complete packet, including images, and produce an
   engineering brief. Resolve revisions, units, configuration, physics, initial
   conditions, command semantics, scenario duration, and acceptance criteria.
   Review that brief against the original sources.
2. **Model:** generate one `Model.sysml`; run the actual SysML v2 parser and a
   semantic review. A source-grounded correction can revise the brief.
3. **Simulate and verify:** generate one `Model.mo`; compile and simulate with
   OpenModelica for the specified experiment. Check actual trajectories against
   the acceptance criteria and reference data, then review source/model consistency.

Every reasoning call receives the original source packet. The engineering brief
is an interpretation that can be corrected, rather than an irreversible source
of truth. Normal small cases use six generation/review calls, plus any necessary
input-table expansion or bounded repairs.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the design and its limits.

The model request layer follows the official OpenAI guidance on
[structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
and [image inputs](https://developers.openai.com/api/docs/guides/images-vision):
the response envelope is typed while the engineering brief remains narrative,
and original visual evidence accompanies the text.

## Run

Use Python 3.11+ and install with `pip install -e ".[dev]"`. Copy `.env.example`
to `.env` and configure `OPENAI_API_KEY` locally. The existing `.env` is preserved;
its `STAGE_1_EXTRACTION_MODEL` and `STAGE_2/3_MAPPING_MODEL` names still work.
You also need OpenModelica and the SysML v2 Pilot Implementation Jupyter kernel.

```powershell
# A full packet; --docs also accepts a single file.
.\.venv\Scripts\python.exe -m simulation_platform.cli run `
  --project tank `
  --docs '.\test cases\tank_sysmlv2_full_dataset\tank_sysmlv2_full_dataset' `
  --reference '09_datasets/10_demo_run_900s.csv'

# Individual stages use the same functions as run.
.\.venv\Scripts\python.exe -m simulation_platform.cli index --project my_case --docs '.\my_documents'
.\.venv\Scripts\python.exe -m simulation_platform.cli inspect --project my_case
.\.venv\Scripts\python.exe -m simulation_platform.cli sysml --project my_case
.\.venv\Scripts\python.exe -m simulation_platform.cli simulate --project my_case
.\.venv\Scripts\python.exe -m simulation_platform.cli status --project my_case

# Inspect extraction without an API key or model calls.
.\.venv\Scripts\python.exe -m simulation_platform.cli sources --docs '.\my_documents'
```

`--problem` accepts a separate problem statement in any supported format.
`--reference` is optional and repeatable: these relative CSV/TSV paths are
designated as expected outputs and their values cannot be exposed to generation,
even if the model incorrectly calls them input schedules. Without this option,
the agent classifies tables from the packet; large tables initially expose their
column schema only. Use explicit holdouts for independent evaluation.

Completed project output:

```text
projects/my_case/
  understanding.md       Human-readable engineering interpretation
  Model.sysml            One textual SysML v2 model
  Model.mo               One self-contained executable Modelica model
  results.csv            Requested uniform logging grid
  report.json            Numerical checks, reference comparisons, review
  compiler.log           Actual compiler/simulation diagnostics
  .pipeline.json         Resume metadata, checks, mappings and revision history
```

Compiler build products live in temporary directories. The SysML file can be
opened/imported in a compatible SysML v2 tool for diagram rendering; this pipeline
does not produce a screenshot in place of a semantic model.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q

# No API calls: compile independent numerical reference models and compare
# against the supplied tank, IAQ and magnetic benchmark data.
.\.venv\Scripts\python.exe -m benchmarks.run --reference

# Once a key is configured: generate those three cases with the actual agent,
# then evaluate the results using fixed independent benchmark tolerances.
.\.venv\Scripts\python.exe -m benchmarks.run --generate `
  --agent-projects '.\projects' --output '.\validation\agent'
```

The independent reference models are test oracles in `benchmarks/reference_models`.
Production code never imports them or the case constants in `benchmarks/run.py`.
Reference-mode reports explicitly say `agent_generation_tested: false`.
Passing these checks validates the physical baselines and verification machinery;
it does **not** establish that the LLM generates correct models. Actual generation
has intentionally not been run during this offline development session.

All 56 documents across the four supplied datasets are covered by extraction
tests. Numerical reference tests cover the three simpler datasets. The evaporation
case has source-documented WaterNaCl medium/pump initialization issues and has not
been claimed as solved.

## Limits

Supported inputs include PDF (text and scanned/visual pages), images supported by
PyMuPDF, TXT/Markdown, XLSX/XLSM, DOCX with embedded images, EML, CSV/TSV, JSON,
XML, HTML, YAML, and textual Modelica/SysML/PlantUML. Legacy binary Office formats,
audio/video, encrypted files, and arbitrary proprietary formats need conversion.
Failures identify the exact unreadable file; they do not silently omit it.
Spreadsheet formulas retain cached values when present; formulas are not recalculated.

`MAX_CONTEXT_CHARS` defaults to 300,000. Larger packets fail explicitly rather than
losing context silently; split them by engineering scope or increase the limit
within the chosen model's capacity. Incomplete model responses fail explicitly.

Real parser/compiler checks are required for `READY`. Unresolved material choices
produce `NEEDS_CLARIFICATION`; noninteractive execution does not invent answers.
Generation and repairs share each stage's estimated spend cap. Token prices are
configurable estimates, not billing guarantees; one in-flight response may cross
an estimate. A new invocation has a new stage budget.
