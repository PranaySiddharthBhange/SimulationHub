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
