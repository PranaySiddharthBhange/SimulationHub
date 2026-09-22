# DECISIONS.md

D1 | Installed OpenModelica and the SysML v2 validator locally | The project needed executable local validation before building the generation pipeline.

## Software installed

- **OpenModelica 1.27.1 (64-bit)** with the `omc.exe` command-line compiler and Modelica Standard Library.
- **Miniconda/Conda** for an isolated SysML environment.
- **Python 3.11, JupyterLab, Graphviz, Node.js, and `jupyter-sysml-kernel`** from Conda Forge.
- **`jupyter_client`** in the application Python environment so the program can start and communicate with the SysML kernel.

## Installation commands

OpenModelica:

```powershell
winget install OpenModelica.OpenModelica.Official
```

SysML v2 validator environment:

```powershell
conda create -n sysml python=3.11 jupyterlab graphviz nodejs jupyter-sysml-kernel -c conda-forge
```

## Installed locations

```text
C:\Program Files\OpenModelica1.27.1-64bit\bin\omc.exe
C:\Users\Pranay Bhange\miniconda3\envs\sysml\share\jupyter\kernels\sysml
```

## Verification commands

```powershell
& "C:\Program Files\OpenModelica1.27.1-64bit\bin\omc.exe" --version
conda run -n sysml jupyter kernelspec list
```

## D2 Specialized agent workflow

D2 | Split the workflow into Document, SysML, Modelica, and Compiler agents with explicit contracts | A single end-to-end agent mixed extraction, modelling, and validation, making errors difficult to trace and repair.

- The Document Agent interprets mixed engineering inputs.
- The SysML Agent generates the structural model.
- The Modelica Agent creates the executable model.
- The Compiler Agent validates generated Modelica.
- Agent contracts define the information exchanged between stages.

## Decisions from the implementation plan

D3 | Scoped the first end-to-end implementation to the L1 two-tank controller and kept L2 as a generalization probe | Attempting all four supplied domains would dilute the working vertical slice and threaten the hard compile-and-simulate gate.

D4 | Adopted an evidence-backed typed intermediate representation as the single source of truth for SysML and Modelica | Generating the two outputs independently could silently produce different components, parameters, connections, and behavior.

D5 | Added a simulation-readiness and user-approval gate before executable generation | Silently inventing missing parameters or resolving authoritative conflicts arbitrarily would produce an untrustworthy model even if it compiled.

D6 | Required deterministic emitters followed by the real SysML parser and OpenModelica build/simulation checks | Allowing the language model or lightweight syntax checks to declare success could release artifacts that looked valid but did not parse, compile, or simulate.

## Implementation agent code  and pipeline decisions

D7 | Accept one ZIP per run and account for every archive member before interpretation | An unconstrained directory scan could mix systems, hide unreadable files, or allow unsafe archive paths.

D8 | Preserve source locators, quoted evidence spans, hashes, and parser status for every extracted claim | A value without its originating page, sheet, row, or source file cannot be reviewed or defended.

D9 | Resolve competing engineering values by property-specific authority and keep superseded candidates visible | Choosing the newest or last-seen value globally could silently override an approved requirement or design decision.

D10 | Classify readiness as ready, needs_decision, or unsupported_or_conflicting before executable generation | A structural description can be useful for SysML while still lacking the parameters or physics needed for a trustworthy simulation.

D11 | Use stable IDs and a typed intermediate representation for parts, ports, connections, parameters, behavior, requirements, and evidence | Free-form text passed directly between agents makes correspondence and validation unreliable.

D12 | Generate SysML and Modelica deterministically from the finalized intermediate representation | Independent language-model generation can make the two artifacts disagree while both appear plausible.

D13 | Validate emitted SysML with a pinned parser and cross-check its inventory against the intermediate representation | File extensions and attractive formatting do not establish SysML syntax or semantic correctness.

D14 | Select reusable Modelica archetypes by evidenced role and compatible interfaces instead of branching on benchmark case names | Case-specific templates would solve calibration examples without demonstrating generalization to an unseen specification.

D15 | Treat OpenModelica build and simulation as the Modelica release gate, with the exact command and diagnostics saved | A successful text parse or lightweight check does not prove translation, initialization, or numerical simulation.

D16 | Use bounded, classified repair loops and escalate unresolved engineering failures to a human decision | Unlimited retries can hide a wrong equation or contradiction and make the system appear more reliable than it is.

##  SysML review environment

D17 | Added a pinned SysON Docker Compose setup for graphical SysML review while keeping the Jupyter SysML kernel as the syntax-validation authority | A visual review environment helps inspect models, but a GUI alone does not provide the deterministic parser diagnostics required by the validation gate.

## Generalization and pipeline correction

D18 | Replace test-case-specific system prompts with domain-general instructions driven by evidence and reusable schemas | Prompts tuned to the supplied tank, magnetic, or evaporation cases overfit the calibration set and cannot reliably handle a new engineering problem.

D19 | Connect the Document, SysML, Modelica, and Compiler agents through one orchestrated pipeline with explicit handoff contracts | Separate agents without a shared execution path can each appear complete while their facts, names, topology, and parameters disagree.

D20 | Add result-level verification and feedback before publishing generated artifacts | A model can parse or compile and still produce incorrect physical behavior, so simulation outputs must be checked against requirements, invariants, and expected system behavior.

## Tank case working features

D21 | Use whole-packet engineering reasoning before generation | Tank behavior depends on revisions, units, command timing, initial conditions, and acceptance criteria that cannot be recovered safely from isolated document extraction.

D22 | Keep source evidence, locators, chronology, and hashes attached to interpreted facts | Human reviewers need to trace each tank parameter and behavior claim back to the exact source.

D23 | Require a human-in-the-loop decision when material choices remain unresolved | The platform must expose ambiguity through `NEEDS_CLARIFICATION` instead of inventing a tank medium, setpoint, or command priority.

D24 | Enforce context and spend budgets for each reasoning stage | Large packets and repeated repairs must fail or stop explicitly instead of silently truncating evidence or exceeding the run's cost boundary.

D25 | Hold out designated reference tables from generation and use them only for independent evaluation | The tank agent must demonstrate behavior against unseen trajectories rather than reproduce a supplied answer table.

D26 | Generate one complete SysML model and one complete Modelica model per tank run | Whole models keep structure, behavior, equations, and correspondence understandable and prevent drift across fragmented artifacts.

D27 | Run the real SysML parser and semantic review before attempting Modelica | A syntactically or semantically invalid system description should stop downstream generation.

D28 | Use OpenModelica compilation, initialization, and simulation as executable release gates | Text generation and parser success do not establish that the tank equations run correctly.

D29 | Check trajectories, event timing, invariants, acceptance criteria, and reference tolerances before declaring READY | A compiling tank model can still violate stop/resume, shutdown, level, or valve-interlock behavior.

D30 | Propagate source-grounded corrections upstream and regenerate dependent artifacts | A discovered error in the tank brief must revise SysML and Modelica together rather than leave stale downstream results.

D31 | Bound repair attempts and classify unresolved failures for human review | Repeated automated edits can mask a wrong equation or contradiction; the tank run needs a visible stopping point.

D32 | Record settings, prompts, upstream outputs, artifact hashes, checks, and revision history for resumable runs | Reproducibility and cache invalidation require knowing exactly which evidence and configuration produced each tank result.

D33 | Validate paths and input coverage and report unsupported files explicitly | The tank packet must not mix projects, traverse unsafe paths, or silently omit unreadable engineering evidence.

D34 | Keep independent benchmark models outside the production generator | Offline physical oracles provide an unbiased check of tank verification without leaking benchmark constants into generation.

D35 | Provide a CLI for full runs, individual stages, inspection, simulation, status, and source-only analysis | A command-line interface makes tank processing repeatable, scriptable, auditable, and usable in local or automated validation environments without depending on a GUI.

## Architecture change for generalization and extraction cost

D36 | Generalize the production pipeline beyond tank-specific assumptions | The current implementation embeds tank names, sequence assumptions, fixed interfaces, and case-specific expectations in prompts and mappings. A new engineering problem must instead define its own parts, physics, behaviors, interfaces, and acceptance checks while reusing the same evidence, reasoning, generation, and validation capabilities.

D37 | Remove the rigid tank-shaped contract from runtime handoffs | The existing contract rejects valid variations before the evidence is understood and forces unrelated systems into tank-specific fields. Keep typed structures only where they protect safety-critical handoffs, while allowing the problem-specific engineering brief and intermediate results to carry domain-appropriate content with traceable validation.

D38 | Run document extraction locally with a Gemma 4B-class model | Extraction reads every page, table, spreadsheet row, email, image, and legacy artifact, so sending this high-volume work to OpenAI creates unnecessary cost before engineering judgment begins. A local model handles document classification, text and table extraction, supported image transcription, and source locator capture.

D39 | Preserve extraction evidence and uncertainty when using the local model | Local extraction must retain original files, quoted spans, page or row locations, parser status, confidence, and unresolved extraction errors. This makes low-confidence or incomplete results visible for review instead of allowing an inexpensive extraction pass to become an untraceable source of model facts.

D40 | Reserve higher-cost reasoning calls for interpretation, generation, review, and repair | OpenAI remains available for whole-problem interpretation, conflict resolution, SysML and Modelica generation, semantic review, and bounded repair when stronger reasoning is needed. The split lowers recurring extraction cost while deterministic validators and human review protect against local extraction mistakes.

D41 | Keep the reviewed execution surface CLI-based and exclude the frontend from this implementation commit | A command-line entry point makes runs repeatable and reviewable, while the frontend adds a separate delivery surface that is outside this milestone. The commit should therefore carry the backend, CLI-oriented scripts, tests, configuration, and only the tank project data needed to reproduce the workflow.

## Generalized local extraction pipeline

D42 | Discover and read a complete engineering packet without domain-specific entity schemas | The intake layer must work for tanks, magnetic circuits, IAQ, evaporation, and unseen systems by preserving every supported file and relative source path before domain reasoning begins.

D43 | Provide format-aware extraction for PDF, scanned pages, images, spreadsheets, DOCX, email, CSV/TSV, structured text, Modelica, SysML, PlantUML, XML, HTML, and YAML | Each format carries different engineering evidence, so the pipeline preserves page text, visual pages, spreadsheet coordinates and cached formulas, document tables, email chronology, and source text instead of flattening everything into generic prose.

D44 | Use Ollama-served Gemma 4B-class local inference for document-level understanding | Local inference removes per-document API spend and keeps extraction available offline while the same packet, locators, and raw evidence remain available to later reasoning stages.

D45 | Batch large documents and enforce an explicit context limit without silent truncation | Local model context windows can truncate long observation sets or tables; bounded batches and explicit oversize failures preserve completeness and make the extraction boundary visible.

D46 | Keep extraction domain-neutral and defer entity naming, conflict arbitration, and engineering decisions | The extractor should report source-grounded observations and uncertainty; later problem-specific reasoning decides what constitutes a part, parameter, behavior, or requirement.

D47 | Preserve append-only run logs, parser failures, confidence, and unresolved extraction errors for every run | A generalized pipeline needs replayable evidence and human review when a local model is unavailable, a file is unreadable, or an extraction result is incomplete.

D48 | Hold out externally designated reference tables before local or remote reasoning | Expected trajectories and acceptance outputs must remain evaluation data so the generalized pipeline cannot learn or reproduce the answer during extraction.

D49 | Deliver the running pipeline with a UI around the shared backend workflow | The UI exposes project creation, stage progress, artifacts, clarification requests, and run logs to reviewers while the backend keeps the same evidence, local extraction, validation, and reproducibility controls. This is a presentation layer over the generalized pipeline, not a second domain-specific implementation.
