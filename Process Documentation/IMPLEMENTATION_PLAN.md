# Implementation plan: specs to SysML v2 and executable Modelica

**Prepared:** 17 September 2026  
**Planning horizon:** 17–23 September 2026  
**Status:** Windows toolchain installed and smoke-tested; application implementation remains to be built  
**Execution:** local CLI on this Windows machine, using the user's OpenAI API key for inference; no SaaS interface required

## 1. What the problem asks us to build

The user uploads **one ZIP containing one system's problem statement and supporting files**. The agent reads the archive, determines whether the described system can be simulated with the available evidence and component models, asks for decisions on material gaps, then produces **one reviewable system model in several consistent forms**: a structured intermediate representation (IR), validated SysML v2 textual notation, a Modelica model that actually compiles and simulates where feasible, and an evidence record showing what was inferred, missing, or contradictory. A successful demo must work on a judge-supplied input, so the four supplied cases are calibration and regression data, not four templates to copy. The target user is a **systems engineer creating a first executable, reviewable model**. See the [product requirements document][prd], especially §§5–11, and the [participant briefing][briefing].

The decisive constraints are:

1. **Compilation is a hard gate.** Parsing Modelica text or running `checkModel` alone does not prove compilation. The generated model must pass an `omc` build, with the exact command recorded and runnable by judges.
2. **Engineering honesty is part of correctness.** Every part, port, connection, parameter, behavior, and equation must trace to evidence or to a declared modeling assumption. Conflicting revisions must be shown and resolved by authority, not by whichever value the language model saw last.
3. **The user controls simulation assumptions.** If required values or conditions are missing, the agent proposes defensible defaults with their source and effect, then asks the user to accept them or provide values. Approval is recorded before those defaults enter the executable model. A contradiction or missing physical law cannot be repaired by an arbitrary “standard value.”

The PRD asks for a text input baseline, parts/ports/connections/attributes in the IR, SysML v2 textual output, compiling Modelica, one supplied case end to end, and an assumptions/missing-information log. Its targets are a structural draft in under 2 minutes and a compiling result for one case in under 10 minutes. The briefing additionally requires a repository, truthful daily `DECISIONS.md` entries, `AI-LOG.md` with at least two genuine AI overrides, a compile command, an eight-slide maximum deck, and a live demo. Do not manufacture historical decisions or AI failures.

## 2. Scope decision and why

**Primary end-to-end case: L1 two-tank controller.** It is small enough to finish in the available time but tests real reasoning: structure, command priority, interlocks, timed states, pause/resume, controlled shutdown, and a 900 s physical simulation. Its reference test has precise acceptance criteria. The [tank URS][tank-urs], [approved design review][tank-review], [control notes][tank-control], [engineering register][tank-register], and [TP-17][tank-test] expose deliberate conflicts that a credible product must handle.

**Generalization probe: an L2 room CO2 ZIP and a text-only variant.** Use the same archive intake, fact, IR, trace, and SysML pipeline on a distinct feedback system. If time permits, add a second Modelica archetype for a well-mixed room. The [IAQ requirements][iaq-urs] and [IAQ register][iaq-register] show why this is a useful probe: absolute versus relative ppm, a revised occupancy schedule, unit conversion, and a source sign convention. Keep the supplied L3 magnetic circuit and L4 evaporation plant as held-out architecture reviews; full physical support for them would dilute the L1 deliverable.

| Approach considered | Decision | Reason |
| --- | --- | --- |
| Ask an LLM to write complete SysML and Modelica independently | Reject | No enforceable consistency or reliable provenance; compile repair can silently change physics. |
| Hardcode the four provided systems | Reject | It will fail a judge-supplied spec and violates the PRD's product criterion. |
| Attempt full CAD and arbitrary image understanding before the core path works | Defer | ZIP intake is essential, but unsupported formats can be listed explicitly while common engineering files are read first. |
| ZIP → evidence-backed IR → readiness/approval → validated SysML → compiled Modelica | Adopt | Lets the agent interpret mixed evidence while code enforces syntax, units, topology, and output correspondence. |
| Start with L4 because it shows the most features | Reject for first slice | Its medium and pump-transition convergence issue is already documented in the supplied notes; it threatens the compile/simulate gate. |

**Boundary:** v1 accepts one ZIP per run and reads plain text, PDF, DOCX, XLSX/CSV, email, and existing `.puml`/`.mo` files with file/page/sheet/row provenance. For image diagrams, use a vision/OCR pass only when available and cross-check its proposed facts against other records; otherwise list the image as unprocessed and request a description if it is essential. Native CAD interpretation, arbitrary physical domains, and a polished SaaS interface are later work. An unsupported physics pattern must produce a clear gap/question; a compiling structural shell must never be presented as a validated simulation.

## 3. What the supplied data actually says

These are the L1 facts the implementation should recover **from evidence**, without special-casing their tag names in code:

| Topic | Effective interpretation | Evidence and test implication |
| --- | --- | --- |
| Topology | Source → XV-101 → TK-101 → XV-102 → TK-102 → XV-103 → drain; two level sensors, three pushbuttons, one controller | Equipment and Interface Matrix in [tank register][tank-register]. The [partial architecture][tank-architecture] deliberately omits sensors, commands, and shutdown detail. |
| Tank and flow parameters | Areas 1.20 and 1.40 m²; flows 0.0060, 0.0045, 0.0050 m³/s; initial/low levels 0.05 m | Tank register, Equipment Schedule and Operating Parameters. Ideal Boolean flow switches are authorized by the [valve datasheet][tank-valve], despite physical stroke times. |
| Setpoint and waits | TK-101 high **0.80 m**; waits **10, 12, 8 s** | CR-004 in the register and [approved email][tank-email] supersede older 0.78 m and 10/10/10 s values in the [URS][tank-urs] and [legacy model][tank-legacy]. |
| STOP/START | STOP closes all valves and stores the interrupted state and remaining delay; START resumes it | [DR-02][tank-review] and [control notes][tank-control]. Do not restart a wait or restart the fill cycle. |
| SHUT | SHUT has priority over STOP and START; V1 stays closed; V2 and V3 are **commanded open together** until both tanks are at/below 0.05 m, then IDLE | DR-02 and control notes. The two-valve interlock has this one explicit exception. Distinguish an open command from actual flow when a tank is already at its retained heel. |
| Verification | START 20 s, STOP 220 s, START 280 s, STOP 650 s, SHUT 700 s; run to 900 s | [TP-17][tank-test] AC-01–AC-08 and [reference CSV][tank-trace]. State-boundary comparison allows ±2 s. |

The legacy `.mo` file is **evidence of an old modeling approach**, not a complete solution: it has obsolete numeric values, incomplete state transitions, and no finished SHUT handling. The reference CSV is a regression oracle, not a source that can override an approved design change.

For L2, record the distinct traps in regression fixtures: the approved limit is **1000 ppm absolute**, outdoor air is **300 ppm**, the current schedule peaks at **15 occupants**, current tuning is **Kp 6.0 with 3.5 ACH bias and integral disabled**, and negative `m_flow` is a Modelica source-port convention while physical supply flow is positive. These come from the [IAQ design review][iaq-review] and [IAQ register][iaq-register].

## 4. Product architecture

```text
One ZIP for one system
  → safe unpack, inventory, and extraction with source locations
  → atomic candidate facts + verbatim evidence spans
  → authority/conflict resolution + provisional typed IR
  → simulation-readiness check
  → targeted questions / user approval of sourced defaults
  → finalized, versioned IR (the single source of truth)
  → schema/topology/units/behavior validation
  → SysML v2 textual emitter → parser + cross-check → resolve new doubts
  → Modelica archetype emitter → omc build → simulation + plausibility checks
  → correspondence, assumptions, decisions, conflicts, results, summary
```

Use a small Python CLI. The CLI needs an interactive question step and a noninteractive mode that returns a machine-readable `needs_input` result rather than choosing defaults silently. Use the official OpenAI Python SDK behind an adapter with structured JSON output; read `OPENAI_API_KEY` from the environment. Use bounded calls: one extraction pass by source chunk, one reconciliation pass over candidate facts, and at most one constrained repair pass for a diagnosed failure. The AI proposes facts and classifications; it does not get to declare validation successful. Cache extraction by content hash to keep latency predictable.

Suggested Python packages: `ingest/`, `evidence/`, `readiness/`, `ir/`, `validation/`, `emitters/sysml/`, `emitters/modelica/`, `tool_adapters/`, and `cli/`. Archive intake must reject path traversal, unsafe links, and unreasonable expansion size; it must report every extracted, skipped, or unreadable file. Keep the case fixtures and expected outputs under `examples/` or `tests/`; keep generated artifacts under `runs/<run-id>/`. The `run-id` should bind ZIP/input hashes, model/provider version, prompt version, IR schema version, generator version, validator versions, user assumption decisions, and elapsed time.

### 4.1 Evidence and authority

Represent each extracted assertion as `{subject, property, value, unit, source, locator, quotedSpan, revision, approvalStatus}`. Preserve all candidates, including superseded ones. Confirm the quoted span exists in the extracted source; otherwise mark the claim unsupported. Normalize aliases and units separately from extracting facts. Confidence can prioritize review but must **not** override an approved source.

Resolve by **applicability and authority for the specific property**, not global recency: approved change request for its affected fields; approved design-review decision for clarified behavior; active/released requirement; current equipment/interface data; then informal correspondence, legacy code, and observed traces as corroboration. A test procedure supplies stimulus and acceptance rules, not design authority. Where two applicable authoritative records still conflict, retain both, mark the affected IR field unresolved, and ask one targeted question before generating behavior that depends on it. Record the answer as a new evidence item.

### 4.2 Simulation-readiness and user decision gate

The agent checks the **provisional** model before producing an executable artifact. For each physical domain it needs: identifiable parts and connections; a supported equation/component archetype; units and parameters for those equations; initial conditions; boundary conditions; input or command schedule; and the outputs/acceptance criteria to verify. A structural description can support SysML while still being insufficient for a meaningful simulation. Report readiness as:

| Status | Meaning | Next action |
| --- | --- | --- |
| `ready` | Required facts and supported physics are present and consistent | Continue to SysML, compile, and simulate. |
| `needs_decision` | A bounded set of missing values or assumptions has defensible candidates | Show each candidate's value, unit, source/range, and likely effect; ask the user to approve defaults or supply values. Save the answer in the run record, then recompute readiness. |
| `unsupported_or_conflicting` | Physics is outside the supported archetypes, or authoritative evidence conflicts | Ask a specific question or offer a narrower model. Do not replace a physical law or conflict with arbitrary numbers. |

Batch related questions instead of interrupting for every field. For example: “Tank area and feed flow are missing. I can use these two documented library defaults for an illustrative run; approve them or provide measured values.” If the archive already contains approved values, use them without asking again. If SysML validation or engineering review reveals a new material doubt, update the IR from the user's answer and regenerate **both** outputs; never patch only the SysML or only the Modelica file. Human response time is shown as a waiting state and excluded from measured compute latency.

### 4.3 Minimal IR contract

The schema needs stable IDs and these typed collections:

- `sources` and `claims` with source locators and approval status.
- `parts` with kind, role, aliases, containment, physical versus simulation-only status, and source links.
- `ports` with owner, domain (fluid, signal, electrical, etc.), direction and quantity/unit.
- `connections` between existing compatible ports, with flow/signal semantics.
- `parameters` with canonical SI value, source value/unit, status, source links, and any competing candidates.
- `behavior` with states, transitions, event/guard, priority, timer policy and output actions.
- `equations` or a selected **documented archetype** with explicit assumptions; never free-floating Modelica text from the LLM.
- `requirements`, `verificationCases`, `assumptions`, `openQuestions`, and `elementMappings`.

Validate unique IDs, resolvable references, port compatibility, unit dimensions, duplicate/missing parameters, referenced guard signals, reachable states, output conflicts, and evidence for each generated element. Canonicalize order and names so two identical inputs yield the same topology and stable diffs. Permit `unknown` fields; do not replace them silently with plausible defaults.

### 4.4 Two deterministic emitters, one meaning

After readiness and assumption decisions, emit SysML v2 **textual** parts, ports, connections, attributes, state behavior, and requirement/verification links from the validated IR. Parse it, cross-check coverage and values against the IR and source ledger, and resolve material doubts with the user before generating Modelica. Use a deliberately small grammar subset first. The release gate is the pinned [official SysML v2 Pilot Implementation][sysml-pilot] parser and semantic validator, called from Python through the workspace-local Java 21 runtime and the small `ValidateSysML.java` wrapper. Its valid and invalid smoke cases passed with the bundled standard libraries loaded. OMG publishes the [SysML v2 specification][omg-sysml] and the [official release/examples][sysml-release]. A file extension and attractive formatting are not proof of valid SysML.

Only after SysML validation, generate Modelica from **generic model archetypes** selected by evidenced roles and compatible interfaces (for L1: constant-flow source, well-mixed/constant-area liquid storage, ideal on/off valve, level sensor, discrete sequencer). Parameterize by approved IR values and topology, never by `if (caseName == "two_tank")`. Keep the controller reusable and put the TP-17 button schedule in a separate test harness. If the physical equations required by a spec have no supported archetype or enough parameters, report the missing physics explicitly.

Maintain an `IR ID ↔ SysML qualified name ↔ Modelica name` map. Compare the exported part/port/connection/parameter/state inventories against the IR before release. For the stronger “Modelica derived from SysML” claim in the briefing, add a parser-backed SysML reimport or round-trip check after the first compiling slice; if that cannot be completed, describe the truthful architecture as two emitters from one semantic IR and show the correspondence map.

## 5. L1 physical and behavioral model to implement

For the ideal-flow benchmark, use positive physical flow rates `qFill`, `qTransfer`, and `qDrain`, with areas `A1`, `A2`:

```text
der(h1) = (qFill - qTransfer) / A1
der(h2) = (qTransfer - qDrain) / A2
```

Each flow is active only when its valve is commanded open **and** its upstream inventory permits flow. During SHUT, both V2 and V3 remain commanded open until both low-level conditions hold, but an upstream tank already at its 0.05 m heel must contribute zero flow. Check `h1,h2 ≥ 0.05 m` within numerical tolerance and preserve mass balance. Use the datasheet's authorized ideal Boolean-switch abstraction; retain its 0.8/0.6 s stroke times as equipment attributes, not invented simulation dynamics.

Controller states: `IDLE`, `FILL_T1`, `WAIT_AFTER_FILL`, `TRANSFER_T1_T2`, `WAIT_AFTER_TRANSFER`, `DRAIN_T2`, `WAIT_AFTER_DRAIN`, `PAUSED`, `SHUTDOWN`. Output commands are a function of state; priority is `SHUT > STOP > START`. On STOP, store the previous state and remaining timer; on START, restore them. In normal operation, V1/V2 and V2/V3 must never be simultaneously commanded open. SHUT is the permitted V2/V3 exception. Inputs are momentary events. Make threshold equality (`>=` high, `<=` low), startup behavior, event order, and simultaneous command priority explicit. Build this state controller as a tiny standalone Modelica spike before integrating the plant; Modelica event semantics are a project risk.

## 6. Validation and acceptance gates

| Gate | Automated check / artifact | Passing condition |
| --- | --- | --- |
| ZIP intake | Archive inventory and extraction log | Exactly one intended system is identified; every file is extracted, listed as unsupported, or reported unreadable; paths and expansion limits are safe. |
| Evidence | Claim ledger and conflict report | Every generated element has a source or declared assumption; superseded values remain visible but inactive. |
| Simulation readiness | Feasibility checklist, missing-input questions, and user decision record | Required physics, parameters, units, boundaries and initial conditions are supported or explicitly approved as assumptions before executable generation. |
| IR | Schema, referential, domain/unit and state checks | Zero invalid references or dimension errors; unresolved critical fields block physical generation. |
| SysML | Parse/validate the emitted `.sysml` with a pinned implementation and cross-check it with the evidence ledger | Zero parser/semantic errors for the supported subset; questions raised by the cross-check are answered and the IR regenerated. |
| Correspondence | Diff IR against both output inventories | No unaccounted part, port, connection, parameter, or state; numeric values agree. |
| Modelica compile | A `.mos` script runs `loadFile`, `checkModel`, **`buildModel`**, and `getErrorString`; capture exit status and messages | Build creates a simulation executable; no compiler errors. `checkModel` alone is insufficient. See [OpenModelica scripting API][om-scripting]. |
| L1 simulation | `simulate(..., stopTime=900, numberOfIntervals=900)` or equivalent and export trace | All [TP-17][tank-test] AC-01–AC-08 pass; state-boundary comparison uses its ±2 s allowance. |
| Plausibility | Numerical invariant checks and reference comparison | Nonnegative/residual levels, mass balance, valve interlocks, correct mode behavior; inspect trajectories against [reference CSV][tank-trace]. |
| Repeatability and resilience | Run the same text twice; paraphrase topology; inject contradictory or missing values | Equivalent topology on repeats; material ambiguity becomes a question; bad input fails clearly. |
| Live usability | Timed clean-machine run with progress messages | Structural draft target <2 min; full L1 target <10 min; command reproducible in README. |

`buildModel` and `simulate` are documented OpenModelica scripting operations; `buildModel` creates the executable, while `simulate` runs it. Capture the entire `.mos`, `.mo`, stdout/stderr, tool versions, and results in the run artifact. Do not claim any gate has passed until it has run on the actual machine.

Use focused adversarial checks beyond TP-17: STOP in each wait state and resume after a long pause; SHUT during fill, transfer, wait, and pause; START and STOP at the same time; a low-level tank during SHUT; unknown units; a missing area/flow; and two same-authority conflicting setpoints. These tests exercise the general rules, not memorized CSV timestamps.

## 7. Build order and dates

The briefing allows roughly 12–15 focused hours per person over the event and the repository is read cold. Keep a working vertical slice each day. Dates below assume work starts on **17 September**; record actual decisions/commits on their real dates only.

| Date | Work and checkpoint | Stop/go criterion |
| --- | --- | --- |
| **17 Sep** | Install the official Windows toolchain locally; compile and simulate a hand-written Modelica model; validate valid and invalid SysML files; create Git repo, README, honest `DECISIONS.md`/`AI-LOG.md`. | Working local `omc` build/simulation and SysML validation command. Toolchain failure becomes the top issue immediately. |
| **18 Sep** | Implement safe one-system ZIP intake, readers for the supplied common file types, source locators, claim schema, alias/unit normalization, and a small L1 fixture. | Every archive member is accounted for; extracted facts reproduce topology and current/superseded parameter candidates with exact citations. |
| **19 Sep** | Implement authority resolution, provisional IR, simulation-readiness check, batched questions/default approval, schema/topology/unit checks; test L1 conflicts and one L2 excerpt. | Effective 0.80/10/12/8 values and STOP/SHUT semantics are explicit; missing facts remain missing until the user accepts sourced assumptions or supplies values. |
| **20 Sep** | Implement deterministic SysML emitter, parser validation, evidence/IR cross-check, and ID/requirement mapping. | L1 structure and behavior parse; source-to-element report is inspectable; an answered doubt regenerates the IR and SysML. |
| **21 Sep** | Implement generic tank/valve archetypes and discrete controller, then Modelica compile loop. | Generated L1 `.mo` builds under `omc`; each failed build yields a logged diagnostic and bounded repair. |
| **22 Sep** | Run TP-17, compare CSV, fix physical/event issues, test held-out paraphrases and missing/conflicting specs. | AC-01–AC-08 pass and model plausibility checks pass; second run preserves topology. |
| **23 Sep** | Clean setup and demo, timed judge-style unknown ZIP run, 8-slide deck, architecture note, two real AI corrections, all generated outputs and commands; final commit before 23:59. | A teammate can reproduce compile and explain the evidence, controller, approved assumptions, and failed alternatives. |

If a four-person team is available, split primary ownership across (1) toolchain/Modelica, (2) IR/validation, (3) ingestion/evidence, and (4) SysML/demo/tests. Each person should review another area before the individual probes. Schedule one early domain-expert review and record an actual design change it caused; the briefing awards evidence of changed reasoning, not merely an interview.

## 8. Deliverables and demo flow

Repository deliverables: runnable CLI or local service with setup instructions; `DECISIONS.md`; `AI-LOG.md`; short architecture note; generated archive inventory, `system.ir.json`, `system.sysml`, `system.mo`, `compile.mos`, trace/assumptions/conflicts and user-decision records, and simulation output for L1; tests; and at most eight slides. Only add L2 generated files if its path actually passes validation. The README must state exact prerequisite versions and one command to run a judge-supplied ZIP through generation and compilation.

The live path should be: upload an unseen ZIP → show archive inventory and extracted facts → show simulation-readiness result → request approval of sourced defaults or missing values if needed → show resolved IR and source links → open parsed, cross-checked SysML → show the same IDs in Modelica → run `omc` build and simulation → show assumptions and verification. Progress should identify the current stage and elapsed time. Keep a prepared L1 replay as a backup demonstration artifact, but never present a prepared output as if it came from the unseen input.

## 9. Current setup risks and first checks

- This folder currently has source packets and PDFs but **is not yet a Git repository**. Git is installed. Start version control before development because the briefing checks genuine daily commits.
- Node v24 and .NET 10 are available. Docker Desktop is installed and its Linux x86-64 engine responded during this review. `omc` and Java are not installed on the Windows host; they can run in containers. The [official OpenModelica image][openmodelica-docker] provides `omc`. The [official SysML pilot release][sysml-pilot-release] provides a Java/Jupyter kernel archive, but no ready-to-run file-validator Docker image was identified; build and smoke-test a small Java 21 image plus validation wrapper. Keep the [OpenSysML release][opensysml-release] available as a practical fallback if the wrapper takes too long.
- A parser may accept syntax while semantic references still fail. Save the validator's actual diagnostics and version. A `checkModel` pass may still fail to build; use the `buildModel` gate.
- The ideal constant-flow tank equations are a **declared benchmark simplification**, not a reusable hydraulic law for every plant. Domain archetypes need explicit applicability rules; otherwise return a gap instead of silently inventing physics.
- The supplied packet is synthetic and shareable. Keep any later external/customer plant files out of the repository unless permission and data handling are clear, consistent with PRD §5.3.

## 10. Local tools and libraries

This is implementable as a **local TypeScript CLI** with Docker for the external engineering tools. The agent loop can be ordinary application code with typed stages and explicit questions; no web frontend, database, vector store, or agent framework is needed for the first run. `node` v24.16.0, `npm.cmd`, Git, and a working Linux Docker engine are available here. In PowerShell, call **`npm.cmd`** because the `npm.ps1` script is blocked by this machine's execution policy. Keep the already-installed Node CLI on the host for the first integration slice; it can invoke Docker with argument arrays and mount each run directory into the validator and OpenModelica containers. No host Java or OpenModelica install is required.

| Need | Recommended dependency | Why |
| --- | --- | --- |
| ZIP inventory/extraction | [`yauzl`][yauzl] | Stream entries, validate names/sizes, retain original paths for source locators. Add your own total expanded-size and file-count limits. |
| PDF text | Existing `pdftotext.exe` at `C:\Program Files\Git\mingw64\bin\pdftotext.exe` | The supplied PDFs are text-readable. Invoke by argument array and extract page by page for citations. A scanned PDF requires an OCR/vision path and must be reported if unreadable. |
| DOCX | [`mammoth`][mammoth] + [`cheerio`][cheerio] | Convert paragraphs and tables to HTML, then retain section/table/row references. |
| XLSX | [`exceljs`][exceljs] | Read sheets, row numbers, cell addresses, and values. |
| CSV and email | [`csv-parse`][csv-parse] and [`mailparser`][mailparser] | Preserve CSV row locations and decode email headers/body. |
| IR and AI response validation | [`zod`][zod] | Define the typed IR once and reject malformed extracted facts before generation. |
| AI extraction/reconciliation | Official [`openai` JavaScript SDK][openai-quickstart] | Use the user's API key from `OPENAI_API_KEY`; the application runs locally and calls the OpenAI API for inference. |
| Development | `typescript`, `tsx`, `@types/node`, `@types/yauzl`, `@types/mailparser` | Compile/run the CLI and keep Node/parser code typed. |
| Modelica compile/simulate | Official [`openmodelica/openmodelica:v1.27.1-minimal`][openmodelica-docker] image | Provides command-line `omc`; invoke it through `docker run` from Node, bind-mount the run directory, then run `buildModel` and `simulate`. The image does not include Modelica libraries; keep the first model self-contained or provision and pin any needed library. |
| SysML v2 release validation | [Official SysML pilot 2026-08][sysml-pilot-release] artifact in a custom Java 21 container | The pilot provides the reference parser/validator code, but its downloadable Jupyter kernel is not already a file-validator CLI image. Package a small tested wrapper around the pilot's parser and diagnostics, pin the artifact hash, and run it against bind-mounted `.sysml` files. Java stays inside Docker. |
| SysML quick check / fallback | Pinned [OpenSysML v0.8.0 Windows release][opensysml-release] | Spawn `sysml.exe -strict -validate system.sysml` for immediate local feedback while the pilot container is being integrated. Its published [pilot comparison][opensysml-diff] is useful coverage evidence, not formal certification. |

Start a project and lock the JavaScript dependencies with:

```powershell
npm.cmd init -y
npm.cmd install openai yauzl mammoth cheerio exceljs csv-parse mailparser zod
npm.cmd install -D typescript tsx @types/node @types/yauzl @types/mailparser
```

Use Node's built-in `fs`, `crypto`, and `child_process` for files, hashes, and external tools. Treat `.txt`, `.md`, `.json`, `.puml`, and `.mo` as text; no special package is needed. Keep `OPENAI_API_KEY` in the environment rather than in source files or the submitted ZIP. Extraction and `omc` run locally; excerpts or images submitted to the OpenAI API are processed remotely, so use the supplied synthetic/shareable packets. The local machine's GPU is not a constraint for API inference. The [official OpenAI quickstart][openai-quickstart] documents the JavaScript SDK and environment variable setup.

The immediate setup check is: `docker info`, `docker run --rm openmodelica/openmodelica:v1.27.1-minimal omc --version`, and `node --version`. Then create a minimal `.mo`, run `loadFile`, `buildModel`, and `simulate` through a `.mos` file inside the OpenModelica container, with the output directory mounted so results survive container exit. Build the pinned pilot validator image and require one valid and one invalid `.sysml` smoke case before it becomes a release gate. The Docker engine is working, but these tool images were not pulled or smoke-tested during this review. Validation does not establish requirement truth or simulation correctness; keep separate IR, requirement, and simulation checks.

## Source and tooling references

[prd]: <CCTech Millinium_Hackathon_PRD_System_Modelling_V1.2.pdf>
[briefing]: <AI-in-Engineering-Hackathon-Participant-Briefing (1).pdf>
[tank-urs]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/01_requirements/01_customer_URS.pdf
[tank-register]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/02_engineering_data/02_engineering_data_register.xlsx
[tank-architecture]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/03_architecture_diagrams/11_partial_legacy_architecture.puml
[tank-control]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/04_design_notes/04_control_logic_design_notes.docx
[tank-review]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/04_design_notes/06_design_review_minutes.md
[tank-email]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/05_correspondence/05_controls_email_thread.eml
[tank-legacy]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/06_legacy_code/07_legacy_tank_demo.mo
[tank-valve]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/07_datasheets/08_valve_datasheet.pdf
[tank-test]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/08_commissioning/09_test_procedure_TP17.pdf
[tank-trace]: sysml_problem_statement/tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset/09_datasets/10_demo_run_900s.csv
[iaq-urs]: sysml_problem_statement/iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset/01_requirements/01_owner_iaq_requirements.pdf
[iaq-register]: sysml_problem_statement/iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset/02_engineering_data/02_iaq_engineering_register.xlsx
[iaq-review]: sysml_problem_statement/iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset/04_design_notes/06_iaq_design_review_minutes.md
[omg-sysml]: https://www.omg.org/spec/SysML/2.0/About-SysML
[sysml-release]: https://github.com/Systems-Modeling/SysML-v2-Release
[sysml-pilot]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation
[sysml-pilot-release]: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/releases/tag/2026-08
[opensysml]: https://github.com/Open-MBEE/OpenSysML
[opensysml-release]: https://github.com/Open-MBEE/OpenSysML/releases/tag/v0.8.0
[opensysml-cli]: https://opensysml.org/guide/03-command-line/
[opensysml-diff]: https://opensysml.org/project/pilot-differential/
[om-scripting]: https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/scripting_api.html
[openmodelica-windows]: https://openmodelica.org/download/download-windows/
[openmodelica-docker]: https://openmodelica.org/download/docker/
[yauzl]: https://github.com/thejoshwolfe/yauzl/blob/master/README.md
[mammoth]: https://github.com/mwilliamson/mammoth.js/blob/master/README.md
[cheerio]: https://cheerio.js.org/docs/intro
[exceljs]: https://github.com/exceljs/exceljs
[csv-parse]: https://csv.js.org/parse/
[mailparser]: https://nodemailer.com/extras/mailparser
[zod]: https://zod.dev/basics
[openai-quickstart]: https://developers.openai.com/api/docs/quickstart
