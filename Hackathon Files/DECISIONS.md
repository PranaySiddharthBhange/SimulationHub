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
