# AI-LOG.md

## D1 — Installed required local software

- Installed OpenModelica 1.27.1 for local Modelica compilation.
- Installed the official SysML v2 Jupyter kernel in a dedicated Conda environment for local SysML syntax validation.
- Installed the supporting Python and Jupyter packages required to invoke both validators from the application later.

## A2  Initial AI-generated architecture

- **AI output:** AI proposed generating SysML and Modelica directly from the source documents in separate steps.
- **Problem:** Independent generation could produce different components, names, parameters, and connections in the two outputs.
- **Correction:** Added explicit agent contracts and required both generation stages to use the same resolved engineering information.
- **Reason:** SysML and Modelica must describe the same system, and compiler feedback must be traceable to the originating model decision.

## A3 Rejected benchmark-specific generation templates

- **AI output:** AI suggested implementing separate generation rules for the four supplied benchmark systems to reach working outputs quickly.
- **Why it was rejected:** The judges can provide an unseen specification, and case-name-specific rules would demonstrate memorization rather than a reusable modelling product.
- **Replacement:** Use evidence extraction, a typed intermediate representation, and generic component archetypes selected from evidenced roles and compatible interfaces.
- **Evidence:** The product requirements describe the supplied cases as calibration tests and explicitly prioritize generalization over case-specific handling.
- **Human judgment:** Keep the L1 tank case as the first vertical slice while ensuring the architecture does not branch on the benchmark name.

## A4 Rejected silent defaults for missing engineering data

- **AI output:** AI could complete incomplete specifications by inserting plausible standard values so generation could continue without interruption.
- **Why it was rejected:** A plausible value can change the physics, timing, or acceptance result while hiding that the source never supplied it.
- **Replacement:** Add a simulation-readiness check that classifies the model as `ready`, `needs_decision`, or `unsupported_or_conflicting`; material assumptions require a recorded user decision.
- **Evidence:** The hackathon requirements state that missing information must be surfaced or introduced as a stated assumption and that contradictions must not be resolved arbitrarily.
- **Human judgment:** A partial but traceable model is preferable to a complete-looking model built on invented parameters.

## A5 Corrected the proposed Modelica validation gate

- **AI output:** AI treated generated Modelica text and a successful lightweight model check as sufficient evidence that the model compiled.
- **Why it was corrected:** Syntax and `checkModel()` do not prove that OpenModelica can translate, build, initialize, and simulate the equation system.
- **Replacement:** Run the generated files through the real `omc` toolchain, build the model, execute a simulation, capture diagnostics, and return failures to a bounded repair loop.
- **Evidence:** The participant rules define Modelica compilation as a binary live gate, while the implementation plan requires a reproducible compiler command and saved output.
- **Human judgment:** Only the external compiler can declare compilation success; the AI may diagnose and repair failures but cannot waive the gate.

## Implementation corrections and rejected approaches

### A6 Corrected untraceable extraction

- **AI output:** AI proposed returning normalized facts without retaining the original page, sheet, row, or quoted evidence span.
- **Problem:** Reviewers could not distinguish an extracted statement from an AI inference.
- **Correction:** Every claim now carries source locators, quoted evidence, revision information, and approval status.
- **Evidence:** The implementation plan requires every generated element to trace to input evidence or a declared assumption.
- **Human judgment:** Provenance is mandatory even when the normalized value looks obvious.

### A7 Rejected global newest-value precedence

- **AI output:** AI suggested always selecting the latest timestamped value when documents disagree.
- **Problem:** A newer informal note can be less authoritative than an approved change or released requirement for a particular property.
- **Correction:** Resolve conflicts by applicability and authority for the affected property, while preserving superseded candidates.
- **Evidence:** The tank materials contain deliberate revisions and the implementation plan requires property-specific authority.
- **Human judgment:** Recency is evidence, not a universal precedence rule.

### A8 Rejected direct generation from raw documents

- **AI output:** AI suggested sending the document bundle directly to separate SysML and Modelica prompts.
- **Problem:** The two outputs could diverge in names, ports, parameters, topology, or state behavior.
- **Correction:** Finalized evidence-backed IR is generated first; both emitters consume that same IR and produce correspondence maps.
- **Evidence:** The product requirements warn that independent generation is the common source of silent divergence.
- **Human judgment:** The IR is the boundary where ambiguity is resolved before code generation.

### A9 Corrected compiler success criteria

- **AI output:** AI treated a parser pass or `checkModel()` result as proof that Modelica was executable.
- **Problem:** Translation, initialization, equation balance, and simulation failures can appear only during build or simulation.
- **Correction:** Require `omc` build and simulation, capture the command and diagnostics, and run plausibility checks on the result.
- **Evidence:** The hackathon defines Modelica compilation as a live hard gate.
- **Human judgment:** Validation authority stays with the external compiler and solver.

### A10 Deferred broad CAD and image scope

- **AI output:** AI proposed implementing arbitrary CAD and image interpretation before the text-and-document path was complete.
- **Problem:** It would consume the available build time without improving the first compiling vertical slice.
- **Correction:** Start with ZIP intake for common engineering documents and report unsupported image or CAD inputs explicitly.
- **Evidence:** The implementation plan limits v1 while retaining an extension path for vision and CAD.
- **Human judgment:** A narrow path that compiles and explains its gaps is more valuable than a broad path that cannot be validated.

### A11  Separated graphical SysML review 

- **AI/tooling proposal:** Treat the SysON graphical service as the complete SysML validation mechanism.
- **Correction:** Keep SysON for local model review and navigation, while the official SysML v2 Jupyter kernel remains the parser and syntax-validation authority.
- **Reason:** Visual inspection can show a model, but it cannot replace deterministic parser diagnostics and repeatable automated validation.
- **Evidence:** `sysml_setup/docker-compose.yml` pins SysON v2026.9.0 with PostgreSQL 15, while the application validation path uses the local SysML kernel.

### A12 Over-specific system prompts

- **AI output:** The system prompts encode the supplied benchmark cases and their expected component names, topology, and behavior directly.
- **Problem:** The approach is too strict for unseen systems and encourages the model to reproduce test cases instead of reasoning from evidence.
- **Correction:** Move domain knowledge into reusable schemas, libraries, archetypes, and evidence-driven instructions; keep benchmark material as regression data only.
- **Evidence:** The generated design is not general enough to accept a different engineering problem.
- **Human judgment:** Generalization is a product requirement, not an optional extension.

### A13 Corrected isolated-agent execution

- **AI output:** The agents are specified as separate capabilities without a complete runtime pipeline connecting their inputs, outputs, approvals, and failures.
- **Problem:** A Document Agent result can be disconnected from SysML generation, and Modelica generation can proceed without the validated semantic result.
- **Correction:** Add an orchestrator with explicit stage contracts, shared run identifiers, readiness gates, and deterministic handoffs.
- **Evidence:** Individual agent artifacts exist, but there is no guaranteed end-to-end path from one ZIP input to one corresponding SysML and Modelica result.
- **Human judgment:** Agents are useful only when their outputs form one traceable execution.

### A14 Corrected compile-only confidence

- **AI output:** AI treats syntactically valid or compiling generated models as successful results.
- **Problem:** Some outputs are physically or behaviorally incorrect even when the files are accepted by a tool.
- **Correction:** Add requirement checks, state and interlock checks, conservation/invariant checks, trajectory plausibility checks, and result feedback before publishing.
- **Evidence:** Incorrect simulation results expose the gap between compilation and engineering correctness.
- **Human judgment:** Compilation is necessary, but result validation decides whether the generated model is trustworthy.

### A15 Whole-packet tank understanding

- **AI output:** The working platform reads the complete tank packet and produces one engineering brief covering revisions, units, balances, initial conditions, commands, timing, outputs, and acceptance criteria.
- **Why it exists:** Tank behavior is distributed across requirements, design notes, correspondence, datasets, and diagrams; isolated extraction loses the relationships between them.
- **Control:** The brief is reviewed against the original packet before model generation.

### A16 Evidence and traceability

- **AI output:** Interpreted values retain source filenames, page or row locators, quoted evidence, chronology, and hashes.
- **Why it exists:** A reviewer must be able to explain where every tank limit, wait, command priority, and physical assumption comes from.
- **Control:** Unlocated or unsupported claims remain visible instead of becoming silent model inputs.

### A17 Human-in-the-loop clarification

- **AI output:** The run returns `NEEDS_CLARIFICATION` when a material choice or conflicting tank requirement cannot be resolved from the packet.
- **Why it exists:** The system must not invent a fluid, setpoint, initial condition, or command priority to force generation to continue.
- **Control:** Noninteractive runs stop with the unresolved question and preserve the evidence needed for a human decision.

### A18 Budget and context constraints

- **AI output:** Each stage enforces a maximum context size and estimated spend cap, including bounded repair calls.
- **Why it exists:** Silent truncation can hide tank requirements, while unlimited retries make cost and behavior unpredictable.
- **Control:** Oversized packets and exhausted budgets fail explicitly and can be resumed with a new invocation.

### A19 Reference-data holdout

- **AI output:** Designated tank reference tables are withheld from generation and used only for independent comparison.
- **Why it exists:** Reusing expected trajectories would let the agent copy the answer instead of demonstrating correct physics.
- **Control:** Reports identify reference evaluation separately from agent generation.

### A20 Single-model generation

- **AI output:** The run emits one understandable `Model.sysml` and one self-contained `Model.mo` for the tank case.
- **Why it exists:** Fragmented files make correspondence, review, and behavior consistency difficult.
- **Control:** Both artifacts are generated from the reviewed problem interpretation and are cross-checked against each other.

### A21 Deterministic validation gates

- **AI output:** The actual SysML parser and semantic checks run before OpenModelica compilation, initialization, and simulation.
- **Why it exists:** Attractive text or a parser-only pass cannot establish that the tank model is executable.
- **Control:** Missing outputs, parser failures, translation errors, initialization failures, and incomplete simulations block `READY`.

### A22 Result-level verification

- **AI output:** Tank trajectories are checked for event timing, level limits, valve interlocks, STOP/START resume, SHUT priority, invariants, acceptance criteria, and reference tolerances.
- **Why it exists:** A model can compile while producing physically or behaviorally wrong results.
- **Control:** Raw event rows and the requested logging endpoints are checked before the report is published.

### A23 Upstream correction loop

- **AI output:** A source-grounded review correction reruns understanding and regenerates dependent SysML and Modelica artifacts.
- **Why it exists:** Keeping an old brief while repairing only downstream code can preserve the original tank mistake.
- **Control:** Previous interpretations and corrections remain in project state for auditability.

### A24 Bounded repair and escalation

- **AI output:** Automated repairs are limited, classified, and escalated when the tank failure remains unresolved.
- **Why it exists:** Unlimited edits can hide contradictory requirements or incorrect equations.
- **Control:** The run records the failure class and stops at a visible human decision point.

### A25 Reproducible resumable runs

- **AI output:** Settings, prompts, source and artifact hashes, checks, mappings, cache decisions, and revision history are stored with the tank project.
- **Why it exists:** A later run must be able to explain or invalidate an earlier result when evidence or configuration changes.
- **Control:** Changed or deleted inputs make dependent artifacts stale and trigger regeneration or revalidation.

### A26 Safe intake and explicit coverage

- **AI output:** The platform validates archive paths, accounts for every tank input member, and reports unsupported or unreadable files.
- **Why it exists:** Mixed projects, unsafe paths, and silent omissions can invalidate the engineering interpretation.
- **Control:** Unsupported formats and failed reads are surfaced with the exact file and reason.

### A27 Independent benchmark oracles

- **AI output:** Separate reference models and fixed tolerances evaluate the tank verifier without being imported by production generation code.
- **Why it exists:** An independent oracle tests numerical machinery without leaking the expected answer into the agent.
- **Control:** Offline reference reports clearly distinguish physical baseline checks from generated-model claims.

### A28 CLI-based operation

- **AI output:** The tank workflow is available through a CLI for full execution and separate `index`, `inspect`, `sysml`, `simulate`, `status`, and `sources` commands.
- **Why it exists:** Repeatable command invocation supports automation, stage-by-stage debugging, resumable runs, and reviewable validation records.
- **Control:** Each command uses the same project state and artifacts, so a run can be inspected or resumed without relying on a graphical interface.

### A29 Generalized architecture and local extraction

- **Architectural finding:** The implementation is still too specific to the tank system and the rigid contract layer makes the pipeline too restrictive for new engineering problems.
- **Decision:** Generalize the pipeline around reusable evidence, reasoning, and validation capabilities; remove the strict contract from the runtime handoff path so valid variations are not rejected prematurely.
- **Cost finding:** Sending document extraction to OpenAI for every source file creates excessive cost before engineering reasoning begins.
- **Implementation change:** Run only document extraction on a local Gemma 4B-class model. Keep later interpretation, model generation, review, and validation stages available for higher-capability reasoning where needed.
- **Expected effect:** Lower extraction cost, broader problem coverage, and fewer false failures caused by tank-specific contracts.

### A30 CLI-focused implementation scope

- **Decision:** Review and stage the backend, scripts, tests, configuration, and tank project through a CLI-focused boundary.
- **Excluded:** The frontend and scratch-pad material are omitted from this milestone; magnet and evaporation project folders are not included in the staged tank run.
- **Reason:** This keeps the milestone reproducible and narrow while preserving the complete tank workflow for review.

### A31 UI delivery for the running pipeline

- **AI output:** The pipeline now includes a UI for creating projects, viewing stage progress, reviewing artifacts, responding to clarification requests, and inspecting run logs.
- **Reason:** A visible workflow makes the generalized backend easier to operate and review than terminal output alone.
- **Boundary:** The UI calls the shared backend and does not reintroduce tank-specific extraction or validation logic.
- **Commit scope:** The older implementation documentation is removed as the architecture moves to the running UI-backed pipeline.

### A32 Per-project extraction backend selection

- **UI feature:** New project creation offers Local Gemma or Cloud GPT-5.4 for Stage 1.
- **Persistence:** The selected backend is stored in project metadata and passed to Stage 1 when the pipeline starts.
- **Behavior:** Local mode uses text-only Gemma and skips image-only files; cloud mode uses GPT-5.4 and can process visual evidence.
- **Reason:** Reviewers can choose the privacy and cost profile per project without changing global configuration.

### A33 Frontend delivery for the running pipeline

- **UI changes:** Added per-project Local Gemma or Cloud GPT-5.4 selection, individual stage run and re-run controls, live stage status, newest-first activity logs, expandable human-input answers, delayed stage model/cost details, a resizable log pane, separate Validation and Result views, one graph per result variable, and a full-screen graph viewer with zoom, pan, reset, and close controls.
- **Integration:** The frontend continues to use the shared API and SSE log stream; no separate frontend pipeline or tank-specific reasoning path was introduced.
- **Verification:** The frontend production build passes and lint completes with existing non-blocking React warnings.

### A34 Remaining pipeline implementation scope

- **Behavior included:** Dynamic service ports and reliable Ctrl+C cleanup, per-stage reruns, shared local/cloud extraction, accurate extraction of required durations and outputs, cloud cost records, five total generation attempts, connector preflight, individual simulation result graphs, and preserved human clarification flow.
- **Review artifacts:** The generated tank project folder remains available for inspection together with its source copy, run log, extracted understanding, SysML, Modelica bundle, compiler output, and result graphs.
- **Owner:** Pranay Bhange.

### A35 Modelica prompt and catalog verification

- **Review:** The Modelica prompt was audited against the implementation and Modelica language semantics.
- **Correction:** Removed the unsupported universal StopTime-margin rule and softened one-writer, `noEvent`, timer, and event-layout rules into conservative generated-controller guidance.
- **Catalog:** Added concrete tank and magnetic usage patterns showing connector directions, integrator/flow wiring, MMF source wiring, reluctance ports, branching, and grounding.
- **Repair policy:** The verified catalog is the initial baseline. A compiler-supported repair may use an installed alternative when the baseline class or usage is incompatible, while preserving behavior and recording the correction.

### A36 Modelica attempt preservation

- **Change:** Every Stage 3 draft is archived under `modelica/generated/attempts/attempt_NNN/` with its files and attempt manifest before preflight or OpenModelica validation. The active output directory keeps only the latest bundle used by Stage 4; reruns clear active outputs but never archived attempts.

## Live debugging log — Stage 3/4 validation-repair loop and generated-model defects

The entries below record real defects found by running the pipeline against the benchmark and test cases, each root-caused against the actual `omc` compiler output (not guessed), and the guardrail (static check and/or prompt rule) added so the same class of defect is caught before or during generation next time.

### A38 Behavioral validation could compile and run while still being wrong

- **Problem:** A full benchmark rerun found two defects that compiled and simulated cleanly but were behaviorally wrong: the NaCl controller's mode never advanced past its initial state, and the two-tank case's Tank 2 inflow was wired from Tank 1's *level* instead of the transfer valve's *flow*. Stage 3's own accept gate had no structural check for either, and Stage 3/Stage 4 only ever ran once each in sequence, so Stage 4's verdict never fed back into generation.
- **Fix:** Added blocking static checks `_connector_unit_mismatches` (flags a `connect()` between ports whose names imply different physical quantities) and `_parameter_alias_issues` (flags a reported variable aliasing a block's parameter instead of its output). Stage 3 no longer ships a bundle it has proven dead with just a warning — it now fails the stage. Added a Stage 3↔Stage 4 loop (`execute_reasoner_stage_3_and_4`) that feeds a failing verdict back into another generation attempt, carrying full round history, matching the history-carrying pattern already used by Stage 3's own compiler-repair loop and now also added to Stage 2's SysML repair loop.

### A39 Collapsed Build and Verify into one pipeline step

- **Change:** The pipeline now runs as 5 user-facing steps instead of 6 — "Build" means the full generate/validate/auto-repair loop from A38 (up to 5 rounds), and "Verify" no longer exists as a separately run step. Backend, frontend stage list, and per-step completion checks were updated to match.

### A40 Fixed a pre-existing, unrelated test failure

- A catalog test failure predating this work had two independent bugs: `Modelica.Blocks.Continuous.Integrator` was missing the `fluid_level_and_flow` domain tag its own documentation already called for, and the test itself asserted benchmark-specific filenames the catalog had deliberately generalized away from. Fixed both; full suite passes clean.

### A41–A42 Bounded the validation-repair loop's cost and made it keep the best round

- **Problem:** The outer Stage 3↔Stage 4 loop (A38) and Stage 3's own internal compiler-repair loop both retried up to 5 times, and the two bounds multiplied rather than added — worst case 25 generation calls for one Build run. The loop also always returned the *last* round's result even when an earlier round had scored better.
- **Fix:** Only the initial round keeps Stage 3's full repair budget; each outer fix round after a failed validation is capped at a single attempt (worst case cut from 25 to ~7 calls). Added round scoring (verdict, then acceptance checks passed, then fewest open issues) with a snapshot/restore mechanism so whichever round scored best — not necessarily the last — is what gets kept and returned.

### A43 A failing fix round could crash the whole Build step and lose a good earlier round

- **Problem:** A single-attempt fix round (A42) that failed to compile still wrote its broken files to the active output directory before raising, and that exception was not caught by the outer loop — it propagated out of the whole Build step, discarding an earlier good, already-snapshotted round.
- **Fix:** Wrapped fix-round generation in try/except; round 0 still re-raises (nothing to fall back to), but a fix round's failure is now logged and the round dropped from scoring while the loop continues. Best-round restore was also made unconditional, since the last scored round and the last written round can now differ.

### A44 Added two minimal single-file test cases

- Added a steady-state magnetic case and a single-tank-fill case, each deliberately simpler than the existing benchmark cases (no discrete controller, no multi-stage sequencing) so they exercise the pipeline's generation and validation path without triggering the sequencing-defect classes found in A38.

### A45 A test case's own design tripped the inertness guardrail, and exposed a real false positive

- **Problem:** The new steady-state magnetic case (A44) held every reported quantity constant from t=0, which is physically correct but indistinguishable from "the model is frozen" to the `_inert_variables` guardrail — Stage 3 correctly but unhelpfully exhausted all attempts and refused. Investigating also found the guardrail itself only flagged Tesla-suffixed variable names, not other equally-constant ones, because of an overbroad token match.
- **Fix:** Removed the overbroad match from `_inert_variables`. Redesigned the test case to ramp its input over the first 0.1 s so every reported quantity genuinely varies, resolving the false reject and making the case an actual test of simulated behavior rather than a static snapshot.

### A46 A double-initialized discrete variable surfaced as an unrelated C build error

- **Root cause, confirmed against the real compiler:** `TankController.mo` initialized 5 discrete variables both via `(start=..., fixed=true)` and again inside `when initial()` — two competing initial equations the prompt already prohibited, but the model did it anyway. OpenModelica doesn't report this as an initialization error; the over-determined system gets folded into a nonlinear iteration, and OMC's C generator unconditionally emits a `.nominal` field access for every iteration variable regardless of type, so the real failure surfaces attempts later as a C compile error naming a generated file, not the actual mistake or variable.
- **Fix:** Added a blocking static check, `_double_initialized_variable_issues`, that flags any variable both `fixed=true`-declared and reassigned inside `when initial()`, before a real compile is spent on it. Strengthened the Stage 3 prompt with the exact compiler symptom text so the LLM can self-diagnose a case the static check's regex misses.

### A47 A `sample()`-gated controller command cost a full extra scan period of latency

- **Root cause, confirmed against the real compiler:** Independent, externally-sourced operator commands (start/stop/shut buttons) were gated through `sample()` before `edge()`, per the (then-)existing prompt rule for all controller commands. This cost a full extra scan period beyond ordinary scan latency, failing acceptance checks written against exact command times.
- **Fix:** The prompt rule was rewritten, not just relaxed — it now distinguishes signals that create a same-instant dependency on the controller's own state (which genuinely need `sample()`-gating to avoid an algebraic loop) from independent external commands, which should be captured directly with `edge(rawSignal)`. Not mechanically detectable from the generated code alone, since it depends on the brief's timing tolerance; fixed at the prompt level with a regression test on the prompt text itself.

### A48 A JVM leak in the SysML kernel launcher was exhausting system memory

- **Root cause:** `jupyter_client`'s Windows kernel-shutdown path falls back to killing only the directly launched process (`os.killpg` doesn't exist on Windows), but the SysML kernel's java launcher spawns a separate worker JVM on Windows — so every real-parser call orphaned one `java.exe`, and roughly 130 had accumulated over the session, starving available RAM and causing every subsequent kernel launch to fail.
- **Fix:** Added an explicit process-tree kill (`taskkill /F /T` on Windows, PID-based on POSIX) run before `shutdown_kernel`, so descendants are swept even though the parent no longer exists to enumerate them afterward. Already-orphaned processes from before the fix needed a manual cleanup, left for the user to authorize separately.

### A49 Two silently-wrong-physics defects in the magnetic-circuit domain

- **Root cause 1 (compile failure):** `LeakageWithCoefficient`'s required `R_mUsefulTot` input was never connected by the generated bundle, an off-by-one-equation under-determined system every attempt.
- **Root cause 2 (silently wrong results, no compile error):** `FixedShape.Cuboid`'s `mu_rConst` parameter is dead — the class hardcodes nonlinear permeability internally — so every core segment silently used the wrong material and reluctance was off by ~1200x with no warning at any point.
- **Root cause 3:** the flux sensor was wired in parallel across a gap's terminals instead of in series, with an inverted sign convention.
- **Fix:** Switched all affected components to `ConstantReluctance` with closed-form parameters (matching the one benchmark case that already validated cleanly), corrected the sensor wiring and sign. Added a blocking static check, `_magnetic_fixed_shape_misuse_issues`, and rewrote the catalog's magnetic-circuit guidance with the verified mechanism for all three findings. Verified against the benchmark's known-correct reference values to under 0.01% error.

### A50 The A49 fix worked, and surfaced a third instance of the same pattern

- A fresh generation avoided both A49 defects (confirming the fix), but hit two new instances of the same underlying mistake under different component names: a custom flux-sensor wrapper wired in parallel across a gap's terminals, and an exciting coil itself shunted in parallel across a core segment instead of inserted in series.
- **Fix:** Generalized the static check (`_magnetic_port_parallel_short_issues`) to flag the connection *shape* itself — any two distinct components connected both `port_p<->port_p` and `port_n<->port_n` — rather than matching specific class or wrapper names, since that's what let the pattern recur. Confirmed zero false positives against legitimate parallel branches elsewhere in the repo.

### A51 A first-attempt live run surfaced a fourth defect: instance/class name collision

- A9/A50's checks both fired correctly against reintroduced defects, but the run still failed on a new issue: a component instance declared with the exact same name as its own class elsewhere in the bundle. The instance name shadows the class name, so the declaration compiles but a later reference that needs the class fails several lines away from the actual cause.
- **Fix:** Added a blocking static check, `_class_instance_name_collision_issues`, scoped to classes defined within the same bundle, plus a prompt rule to keep instance and class names visibly distinct.

### A52 An `edge()`-at-t0 trap silently shifted a whole batch cycle's start by 2505 s

- **Root cause, confirmed against the real compiler in an isolated minimal model:** a controller's start signal was driven by a `BooleanTable` whose first pulse landed exactly at t=0. `edge()` never sees that transition, because `pre()` already equals the signal's own value at the very first instant — so the controller only started on the table's *second*, later pulse, cascading into 8 of 15 failing acceptance checks that were otherwise unrelated to any wiring defect.
- **Fix:** Added a blocking static check, `_edge_at_t0_table_issues`, that traces a zero-starting table's output through `connect()` to any `edge()` call reading it, and a matching prompt rule. Confirmed zero false positives, including against a near-identical table pattern elsewhere that correctly starts after t=0.

### A53 An unguarded ratio numerator produced a "temperature below absolute zero" assertion

- **Root cause, confirmed against the real compiler with `-d=initialization`:** a tank's energy state was floored only on its *denominator* when computing temperature; an "empty" tank initialized with a literal `levelStart = 0.0` made the numerator evaluate to exactly zero too, so the tank's own temperature-positivity assertion tripped at t=0. The compiler's generic assert message named only the shared class, not the specific instance or reason, so 3 of 5 repair attempts failed identically before the model happened to self-correct.
- **Fix:** Added a blocking static check, `_unguarded_ratio_numerator_issues`, generalized to any strictly-positive-asserted variable computed as a ratio whose numerator's own start value isn't floored, plus a prompt rule extending the existing guarded-ratio guidance to numerators, not just denominators.

### A54–A55 Real `Modelica.Fluid` API mistakes the catalog itself was steering the model into

- With the repair-attempt budget tightened at the user's request, two fresh runs hard-failed rather than self-correcting, surfacing three distinct real API mistakes: a hallucinated `PumpCharacteristics` function name, a `ClosedVolume` missing its required `portsData`, and a `PrescribedPump` with no `flowCharacteristic` redeclare at all (silently inheriting an uncallable partial default).
- **Root cause:** the `fluid_level_and_flow` catalog entry recommended real `Modelica.Fluid` components without documenting the curve-data `PrescribedPump` requires or that `portsData` applies to every vessel type, not just `OpenTank`.
- **Fix:** Added three blocking static checks (`_pump_characteristic_hallucination_issues`, `_fluid_vessel_missing_ports_data_issues`, `_prescribed_pump_missing_characteristic_issues`) and rewrote the catalog entry with the verified function list, curve-data requirement, and an explicit instruction to use the signal-flow alternative whenever the brief states no pressure/head curve. The user then restored the default repair-attempt budget after two tightened-budget runs each hard-failed on a genuine, previously-unknown defect.

### A56 A disguised division-by-zero the repair loop couldn't see past

- **Problem:** 3 of 5 repair attempts in one round produced byte-identical output — the compiler's runtime division-by-zero message wasn't specific enough to change anything.
- **Root cause, confirmed by recompiling the isolated bundle:** an `if flowSum > 0 then .../flowSum else 0` guard looked safe but wasn't — OpenModelica compiles an `if` on a non-smooth, boolean-driven expression inside a continuous equation into an event-triggered relation, so the cached condition can still read the previous instant's value at the exact tick the divisor reaches zero.
- **Fix:** Added a blocking static check, `_if_guarded_flow_division_issues`, matching this specific "guard expression identical to divisor expression" shape regardless of naming, converting a late runtime crash into an immediate static rejection on attempt 1. Also found the identical pattern in an older, already-`invalid` project, confirming it's a recurring shape, not a one-off.

### A57 A deeper `Modelica.Fluid` defect class: a C-build crash from implicit network solving

- **Root cause, confirmed by recompiling in isolation:** a plant built from many `Modelica.Fluid` vessels and Boolean-gated valves forces OpenModelica to solve the whole pressure/flow network as one implicit nonlinear system, folding a valve's Boolean `open` state into that system as an iteration variable — the same `.nominal`-field-on-a-non-real-type C-generator bug as A46, but triggered by the network's own implicit solve rather than a source-level double-initialization. Not mechanically checkable from the source text; whether a given topology triggers it depends on OMC's own solver internals.
- **Fix:** Rescoped the `fluid_level_and_flow` catalog entry's "Fluid is the form to use" guidance to simple, few-vessel, single-path plants, and steered multi-branch batch-sequential processes toward the signal-flow alternative instead — every generation across this project that used real `Modelica.Fluid` for a multi-branch process hit a distinct, confirmed compiler defect, while every signal-flow generation for the same shape compiled. Logged as `D69` in `DECISIONS.md`.
