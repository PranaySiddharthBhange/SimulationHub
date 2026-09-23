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

- **Frontend files marked:** `pipeline/frontend/src/App.jsx`, `src/api.js`, `components/NewProjectModal.jsx`, `components/PipelineStepper.jsx`, `components/LogPanel.jsx`, `components/ArtifactViewer.jsx`, `components/StatusPill.jsx`, `vite.config.js`, and `public/runtime-marker.json`.
- **UI changes:** Added per-project Local Gemma or Cloud GPT-5.4 selection, individual stage run and re-run controls, live stage status, newest-first activity logs, expandable human-input answers, delayed stage model/cost details, a resizable log pane, separate Validation and Result views, one graph per result variable, and a full-screen graph viewer with zoom, pan, reset, and close controls.
- **Integration:** The frontend continues to use the shared API and SSE log stream; no separate frontend pipeline or tank-specific reasoning path was introduced.
- **Verification:** The frontend production build passes and lint completes with existing non-blocking React warnings.

### A34 Remaining pipeline implementation scope

- **Backend and launcher files:** `pipeline/run.py`, `pipeline/src/simulation_platform/api.py`, `config.py`, `reasoner.py`, `reasoner_pipeline.py`, `utils/local_models.py`, `skills/stage1_understanding.py`, and `skills/stage3_modelica.py`.
- **CLI and test files:** `pipeline/create_project/`, `pipeline/test_cases/human_input_smoke/`, and `pipeline/test_cases/stage1_smoke/`.
- **Behavior included:** Dynamic service ports and reliable Ctrl+C cleanup, per-stage reruns, shared local/cloud extraction, accurate extraction of required durations and outputs, cloud cost records, five total generation attempts, connector preflight, individual simulation result graphs, and preserved human clarification flow.
- **Review artifacts:** The generated tank project folder remains available for inspection together with its source copy, run log, extracted understanding, SysML, Modelica bundle, compiler output, and result graphs.
- **Owner:** Pranay Bhange.

### A35 Modelica prompt and catalog verification

- **Review:** The Modelica prompt was audited against the implementation and Modelica language semantics.
- **Correction:** Removed the unsupported universal StopTime-margin rule and softened one-writer, `noEvent`, timer, and event-layout rules into conservative generated-controller guidance.
- **Catalog:** Added concrete tank and magnetic usage patterns showing connector directions, integrator/flow wiring, MMF source wiring, reluctance ports, branching, and grounding.
- **Repair policy:** The verified catalog is the initial baseline. A compiler-supported repair may use an installed alternative when the baseline class or usage is incompatible, while preserving behavior and recording the correction.

### A36 Modelica attempt preservation

- **Change:** Every Stage 3 draft is archived under `modelica/generated/attempts/attempt_NNN/` with its files and attempt manifest before preflight or OpenModelica validation.
- **Active output:** The latest bundle continues to populate the active generated directory and manifest used by Stage 4.
- **Reruns:** Stage reruns clear only active Modelica files/results; archived failed and superseded attempts remain available for review.
- **Verification:** Python compilation, prompt import, catalog construction, and diff checks pass.

### A37 Sampled controller scan, and the latency it costs

- **Change:** A discrete sequence controller is now modelled as the sampled device it physically is. The operator commands and measurements are latched on a scan period and one-shot edges are derived from the latched values (`startSample = sample(0, scanPeriod) and startButton; startPulse = edge(startSample);`). Added to the `batch_sequential_process` domain skill as general knowledge and to the Stage 3 prompt as the concrete form.
- **Reason:** This is the structural remedy for the recurring OpenModelica failure `Purely discrete algebraic loops cannot be solved by iterative processes`. Within one scan every discrete value is computed from the previous scan's latched values, so the discrete equations are well-ordered by construction instead of depending on one another in the same instant. It removes that failure class at its root rather than detecting it afterwards.
- **Trade-off — latency:** Sampling costs response time. With a 0.1 s scan, a STOP command arriving at 220.0 s takes effect at 220.1 s. Stage 4 flagged this against the brief's "exact event times" requirement. That is a genuine physical consequence of modelling a scanned controller, not a defect, but it is a real trade-off against the loop-elimination benefit.
- **Guidance added:** Size the scan period against the timing tolerance the acceptance checks demand, not merely against the stated durations — a check requiring an action at an exact instant is failed by a scan that responds one period later. Where the brief demands exact event instants, capture the operator command edges as real events and clock only the internal sequencing, or make the period small enough that the latency falls inside the stated tolerance.
- **Related changes in the same port:** `reinit` is permitted again in one specific shape (its own `when` in an equation section containing nothing but the `reinit`, with the mode dispatcher kept in a separate `algorithm` section, paired with a conditional-rate timer); an earlier blanket ban on it was too broad. `Modelica.Blocks.Sources.RadioButtonSource` is recorded as the component for momentary operator commands, including that `reset` takes a Boolean array and so must list each other button's `.on` output rather than the component instances. Library typed quantities (`Modelica.Units.SI.*`) are preferred over `Real x(unit="m")`.
- **Provenance and generalization:** The technique was taken from the predecessor `local-simulation-agent` tank controller. Only the technique was carried over, stated as general controller knowledge; the predecessor's benchmark-specific prompt rules (a domain-keyed "hard tank controller rule", a quoted tank failure history, and a final overriding tank rule) were deliberately not carried over, consistent with A3. Inspection of that predecessor's own result CSV shows its tank model ignores the STOP at 220 s and never resumes at 280 s, so its reliability came from prompt-level memorization rather than a more correct model.
- **Verification:** Live Stage 3 run passed the real compiler on the second attempt; the generated controller adopted the sampled scan and the SI quantities. All eight TP17 acceptance criteria were checked directly against the result CSV rather than from the Stage 4 narrative, and the state trace follows the specified sequence including the pause at 220 s, the resume at 280 s, and the 8 s inter-cycle restart.
