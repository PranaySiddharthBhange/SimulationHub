"""Real SysML v2 syntax validation via the official Eclipse SysML v2 Pilot
Implementation's Jupyter kernel (`jupyter-sysml-kernel`, installed via conda).

`validation/syntax_validator.py` is a best-effort regex checker (balanced
braces, legal identifiers) that runs everywhere with no dependencies. This
module is the real thing: it drives the actual ANTLR-based SysML v2 parser
and standard library. It is only available when that toolchain is
installed locally. When unavailable, callers should catch
`RealParserUnavailable` and fall back to the regex checker — this module
never silently skips validation, it raises instead.

Verified empirically before writing this (see `DECISIONS.md`):
- The conda-forge `jupyter-sysml-kernel` package bundles its own JVM
  (Azul Zulu OpenJDK) inside the conda environment — no separate system
  Java install is required for this mechanism specifically.
- `jupyter_client.KernelManager(kernel_name="sysml")` needs a
  `KernelSpecManager` pointed explicitly at the conda env's
  `share/jupyter/kernels` directory — the kernel is not registered
  anywhere jupyter_client searches by default from an unrelated Python venv.
- The kernel's `kernel.json` argv starts with the bare string `"java"`,
  resolved via the *calling process's* PATH at subprocess-launch time —
  not guaranteed to include Java (a venv activation doesn't add it).
  Replaced with an absolute path to the conda env's own
  `Library/bin/java.exe` to remove the dependency on ambient shell state.
- Syntax errors surface as `stream` messages on iopub with the literal
  prefix `"ERROR:"`, not as an execute-reply error — format:
  `ERROR:<message> (<internal file> line : <n> column : <n>)`. Confirmed
  against a deliberately broken snippet before trusting this format.
- The kernel loads the full local standard library (KerML + SysML +
  domain libraries) from files bundled in the conda env — no network
  access to the kernel's configured `ISYSML_API_BASE_PATH` is needed for
  parsing.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from simulation_platform.schemas import SyntaxIssue

_ERROR_LINE = re.compile(r"^ERROR:(.*?)\s*\([^()]*?\s+line\s*:\s*(\d+)\s+column\s*:\s*(\d+)\)\s*$")

_CANDIDATE_KERNEL_DIRS = [
    Path.home() / "miniconda3" / "envs" / "sysml" / "share" / "jupyter" / "kernels",
    Path.home() / "anaconda3" / "envs" / "sysml" / "share" / "jupyter" / "kernels",
    Path.home() / "miniconda3" / "share" / "jupyter" / "kernels",
]


class RealParserUnavailable(RuntimeError):
    """Raised when the SysML v2 pilot implementation's kernel can't be found or started."""


def find_kernel_dir() -> Path | None:
    override = os.environ.get("SYSML_AGENT_KERNEL_DIR")
    candidates = [Path(override)] if override else _CANDIDATE_KERNEL_DIRS
    for kernels_dir in candidates:
        if (kernels_dir / "sysml" / "kernel.json").exists():
            return kernels_dir
    return None


def _java_executable(kernels_dir: Path) -> Path:
    # kernels_dir = <conda_env_root>/share/jupyter/kernels — three levels
    # up (kernels -> jupyter -> share) lands back at the conda env root.
    conda_env_root = kernels_dir.parents[2]
    bundled = conda_env_root / "Library" / "bin" / "java.exe"
    if bundled.exists():
        return bundled

    system_java = shutil.which("java")
    if system_java:
        return Path(system_java)

    raise RealParserUnavailable(
        f"No java executable found (checked {bundled} and PATH). "
        "Install the SysML v2 Jupyter kernel via conda, or a system JDK."
    )


def _parse_error_line(raw: str, filename: str) -> SyntaxIssue:
    match = _ERROR_LINE.match(raw.strip())
    if not match:
        return SyntaxIssue(file=filename, line=None, message=raw.strip())
    message, line, _column = match.groups()
    return SyntaxIssue(file=filename, line=int(line), message=message.strip())


def validate_files_with_real_parser(files: dict[str, str], timeout: float = 60.0) -> list[SyntaxIssue]:
    """Runs every file's SysML text through the real parser in one kernel session.

    Raises `RealParserUnavailable` if the kernel can't be found or started —
    callers decide whether to fall back to the regex-based checker.
    """

    kernels_dir = find_kernel_dir()
    if kernels_dir is None:
        raise RealParserUnavailable(
            "No local SysML v2 Jupyter kernel found (checked "
            f"{[str(p) for p in _CANDIDATE_KERNEL_DIRS]} and $SYSML_AGENT_KERNEL_DIR). "
            "Set up via: conda create -n sysml python=3.11 jupyterlab graphviz nodejs "
            "jupyter-sysml-kernel -c conda-forge"
        )

    try:
        from jupyter_client import KernelManager
        from jupyter_client.kernelspec import KernelSpecManager
    except ImportError as exc:
        raise RealParserUnavailable("jupyter_client is not installed in this environment.") from exc

    java_exe = _java_executable(kernels_dir)
    ksm = KernelSpecManager(kernel_dirs=[str(kernels_dir)])
    km = KernelManager(kernel_name="sysml", kernel_spec_manager=ksm)
    km.kernel_spec.argv[0] = str(java_exe)

    issues: list[SyntaxIssue] = []
    try:
        km.start_kernel()
        kc = km.client()
        kc.start_channels()
        try:
            kc.wait_for_ready(timeout=timeout)
            for filename, text in files.items():
                kc.execute(text)
                while True:
                    msg = kc.get_iopub_msg(timeout=timeout)
                    msg_type = msg["msg_type"]
                    if msg_type == "stream":
                        for line in msg["content"]["text"].splitlines():
                            if line.startswith("ERROR:"):
                                issues.append(_parse_error_line(line, filename))
                    elif msg_type == "error":
                        content = msg["content"]
                        issues.append(
                            SyntaxIssue(
                                file=filename,
                                line=None,
                                message=f"{content.get('ename', 'Error')}: {content.get('evalue', '')}",
                            )
                        )
                    if msg_type == "status" and msg["content"]["execution_state"] == "idle":
                        break
        finally:
            kc.stop_channels()
    finally:
        km.shutdown_kernel(now=True)

    return issues
