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
