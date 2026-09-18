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
