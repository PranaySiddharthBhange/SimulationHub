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
