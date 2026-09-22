"""Real compile + simulation-readiness check via the locally installed
OpenModelica `omc` CLI.

Originally a thin stand-in for a separate, not-yet-built Compiler /
Simulation Agent, using only `checkModel()` (a structural/type check).
Folded that agent's real `simulate()`-driving capability in here instead
(see `DECISIONS.md`): a live debugging sequence (D42-D53) found, over and
over, that `checkModel()` passes cleanly on real-world data that a real
`simulate()` attempt then rejects outright -- missing mandatory parameter
defaults, under-determined equation systems, undriven control-signal
inputs, none of which `checkModel()`'s lighter analysis catches. Running
the real `simulate()` here means this agent catches that whole class of
gap itself, not a human re-running the model in OMEdit and pasting the
result back. Raises `CompilerUnavailable` when `omc` isn't installed, so
callers can skip this layer entirely rather than silently fake a result --
same discipline already established for the SysML Agent's real parser
(see `sysml-agent/validation/real_syntax_validator.py` and `DECISIONS.md`
D19/D21).

Verified empirically before writing this (see `DECISIONS.md` D21/D54):
- `omc script.mos` prints `true`/`false` per top-level statement.
- A broken input's syntax/semantic error surfaces as
  `[<path>.mo:<line>:<col>-<line>:<col>:writable] Error: <message>`.
- A structural error with no single source location (e.g. "Too few
  equations, under-determined system...") prints as a bare `Error:
  <message>` line, with no file/line prefix at all.
- Neither is a non-zero process exit code -- `omc`'s own exit code is not
  a reliable pass/fail signal; the printed output is parsed instead.
- `simulate(Class, startTime=..., stopTime=..., numberOfIntervals=...,
  tolerance=..., method="dassl")` prints the literal line "The simulation
  finished successfully." on real, full success (translation AND solving),
  the one reliable signal used here for PASSED.
"""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from simulation_platform.schemas import CompileError, CompileResult, CompileStatus, ErrorCategory

_ERROR_LINE = re.compile(r"\[(?P<file>[^\[\]]*\.mo):(?P<line>\d+):\d+-\d+:\d+:\w+\]\s*Error:\s*(?P<message>.*)")
# A structural error with no single source location (e.g. "Too few
# equations, under-determined system...") has no `[<file>:<line>...]`
# prefix at all -- found live (see DECISIONS.md D54) alongside every
# bracketed one, printed as a bare `Error: <message>` line. `.search()`,
# not an anchored `.match()` -- omc's own value-echoing wraps the whole
# `getErrorString()` return in a quoted string literal, so the actual
# first character on the line is a literal `"`, not `E`.
_BARE_ERROR_LINE = re.compile(r"Error:\s*(?P<message>.*)")
_VERSION_LINE = re.compile(r"v?([\d.]+)")

_CATEGORY_KEYWORDS: list[tuple[str, ErrorCategory]] = [
    ("mismatched input", ErrorCategory.SYNTAX_ERROR),
    ("no viable alternative", ErrorCategory.SYNTAX_ERROR),
    ("missing token", ErrorCategory.SYNTAX_ERROR),
    ("not found in scope", ErrorCategory.CLASS_NOT_FOUND),
    ("class not found", ErrorCategory.CLASS_NOT_FOUND),
    ("type mismatch", ErrorCategory.CONNECTOR_TYPE_MISMATCH),
    ("unconnected", ErrorCategory.CONNECTOR_UNCONNECTED),
    ("duplicate", ErrorCategory.DUPLICATE_DECLARATION),
    ("missing parameter", ErrorCategory.MISSING_PARAMETER),
    ("neither value nor start value", ErrorCategory.MISSING_PARAMETER),
    ("used without having been given a value", ErrorCategory.MISSING_PARAMETER),
    ("dimension", ErrorCategory.DIMENSION_MISMATCH),
    ("unit", ErrorCategory.UNIT_MISMATCH),
    ("over-determined", ErrorCategory.OVERDETERMINED_SYSTEM),
    ("overdetermined", ErrorCategory.OVERDETERMINED_SYSTEM),
    ("under-determined", ErrorCategory.UNDERDETERMINED_SYSTEM),
    ("underdetermined", ErrorCategory.UNDERDETERMINED_SYSTEM),
]

_CANDIDATE_INSTALL_GLOBS = [
    "C:/Program Files/OpenModelica*/bin/omc.exe",
]


class CompilerUnavailable(RuntimeError):
    """Raised when a local OpenModelica `omc` install can't be found."""


def find_omc_executable() -> Path:
    override = os.environ.get("MODELICA_AGENT_OMC_PATH")
    if override:
        return Path(override)

    for pattern in _CANDIDATE_INSTALL_GLOBS:
        root = Path(pattern).anchor
        rest = pattern[len(root):]
        for match in Path(root).glob(rest):
            if match.exists():
                return match

    import shutil

    system_omc = shutil.which("omc")
    if system_omc:
        return Path(system_omc)

    raise CompilerUnavailable(
        "No local OpenModelica install found (checked "
        f"{_CANDIDATE_INSTALL_GLOBS} and $MODELICA_AGENT_OMC_PATH, and PATH). "
        "Install via: winget install OpenModelica.OpenModelica.Official"
    )


def _classify(message: str) -> ErrorCategory:
    lower = message.lower()
    for keyword, category in _CATEGORY_KEYWORDS:
        if keyword in lower:
            return category
    return ErrorCategory.UNKNOWN


def _parse_errors_into(output: str, errors: list[CompileError]) -> None:
    for line in output.splitlines():
        bracketed = _ERROR_LINE.search(line)
        if bracketed is not None:
            message = bracketed.group("message").strip()
            errors.append(
                CompileError(
                    error_id=f"ERR-{len(errors) + 1:03d}",
                    severity="ERROR",
                    category=_classify(message),
                    file=Path(bracketed.group("file")).name,
                    line=int(bracketed.group("line")),
                    message=message,
                    raw=line.strip(),
                )
            )
            continue
        bare = _BARE_ERROR_LINE.search(line)
        if bare is not None:
            message = bare.group("message").strip()
            errors.append(
                CompileError(
                    error_id=f"ERR-{len(errors) + 1:03d}",
                    severity="ERROR",
                    category=_classify(message),
                    file="",
                    line=None,
                    message=message,
                    raw=line.strip(),
                )
            )


def _run_omc_script(omc_path: Path, script_name: str, workdir: Path, timeout: float) -> tuple[str, bool]:
    """Runs `omc <script_name>` and returns (combined_output, timed_out).

    Deliberately NOT `subprocess.run(..., capture_output=True, timeout=...)`
    -- found live: `omc simulate()` compiles the model to a native .exe and
    then waits on it *synchronously*, inheriting Python's stdout/stderr
    pipe handles into that grandchild process. When the simulation itself
    hangs (a genuinely long real run, or a pathological model), killing
    just the immediate `omc.exe` on timeout does NOT close those pipes --
    the grandchild still holds the write end open -- so `communicate()`'s
    read blocks forever waiting for an EOF that never comes, and Python's
    own `timeout=` never actually fires. Confirmed live: a run sat well
    past its 120s timeout for 13+ minutes with no error, no crash, no
    progress. Writing to real files instead of pipes sidesteps that
    entirely (a file handle isn't held open by an unrelated process the
    same way), and waiting on the process HANDLE (`Popen.wait`) rather than
    reading a pipe means the wait is immune to the same hang. On a genuine
    timeout, kills the WHOLE process tree (`taskkill /T /F`) -- not just
    the immediate child -- so the grandchild simulation .exe doesn't keep
    burning CPU as an orphan (the same leak class as `llama-server.exe`
    earlier this session)."""

    stdout_path = workdir / f"{script_name}.stdout.txt"
    stderr_path = workdir / f"{script_name}.stderr.txt"
    with stdout_path.open("w", encoding="utf-8") as out_f, stderr_path.open("w", encoding="utf-8") as err_f:
        proc = subprocess.Popen([str(omc_path), script_name], cwd=workdir, stdout=out_f, stderr=err_f)
        try:
            proc.wait(timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=10,
                )
            except Exception:  # noqa: BLE001 -- best-effort cleanup only
                pass
            try:
                proc.wait(timeout=10)
            except Exception:  # noqa: BLE001 -- already killed; don't block on cleanup
                pass

    output = (
        f"{stdout_path.read_text(encoding='utf-8', errors='replace') if stdout_path.exists() else ''}\n"
        f"{stderr_path.read_text(encoding='utf-8', errors='replace') if stderr_path.exists() else ''}"
    )
    return output, timed_out


def _parse_result_csv(path: Path) -> dict[str, dict[str, float]]:
    """Returns {variable_name: {"min", "max", "final"}} for every real-valued
    column in the OpenModelica CSV result file (the "time" column excluded).
    A summary, not the full time series -- enough for Result Validation's
    reasonableness checks (`shared/result_validation.py`) without turning
    this into a large intermediate artifact. A non-numeric cell is simply
    skipped for that row (OpenModelica's own CSV writer never emits one in
    practice, but this stays defensive rather than crashing a real run over
    a formatting surprise)."""

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if not header:
            return {}
        columns: dict[str, list[float]] = {name: [] for name in header}
        for row in reader:
            for name, raw in zip(header, row):
                try:
                    columns[name].append(float(raw))
                except ValueError:
                    continue

    summary: dict[str, dict[str, float]] = {}
    for name, values in columns.items():
        if name.lower() == "time" or not values:
            continue
        summary[name] = {"min": min(values), "max": max(values), "final": values[-1]}
    return summary


def _omc_version(omc_path: Path, timeout: float) -> str:
    try:
        proc = subprocess.run([str(omc_path), "--version"], capture_output=True, text=True, timeout=timeout)
        match = _VERSION_LINE.search(proc.stdout)
        if match:
            return match.group(1)
    except Exception:  # noqa: BLE001 -- version string is cosmetic, never block on it
        pass
    return "unknown"


def compile_files(
    execution_id: str,
    files: dict[str, str],
    entry_class: str,
    timeout: float = 120.0,
    start_time: float = 0.0,
    stop_time: float = 10.0,
    number_of_intervals: int = 10,
    tolerance: float = 1e-6,
    result_csv_path: Path | None = None,
    log_path: Path | None = None,
) -> CompileResult:
    """Raises `CompilerUnavailable` if `omc` can't be found. Never raises
    for a compile/simulation failure -- that's a normal
    `CompileResult(status=FAILED)`.

    Runs a real `simulate()`, not just `checkModel()` -- found live (see
    DECISIONS.md D42-D54): `checkModel()`'s lighter structural/type check
    passed cleanly on real-world data a real `simulate()` attempt then
    rejected outright, five separate times in a row, for reasons
    `checkModel()` never even attempts to catch (missing mandatory
    parameter defaults, under-determined equation systems, undriven
    control-signal inputs). The default scenario (10 s, 10 intervals) is
    deliberately short and cheap -- it only needs to be long enough for
    translation and one real solver step to surface these; it isn't meant
    to be a physically meaningful simulation window.
    """

    omc_path = find_omc_executable()

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", entry_class):
        raise ValueError("Invalid Modelica entry class")
    for filename in files:
        if Path(filename).name != filename or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\.mo", filename):
            raise ValueError(f"Unsafe Modelica filename: {filename}")

    with tempfile.TemporaryDirectory(prefix="modelica_agent_") as workdir_str:
        workdir = Path(workdir_str)
        # `package.mo` is excluded on purpose -- found live (see DECISIONS.md):
        # a file literally named "package.mo" carries special Modelica
        # semantics (the Modelica Language Specification's directory-package
        # convention), where the package it declares must match the name of
        # its *containing directory* -- not something a flat, ephemeral
        # compile-check workspace (an arbitrary temp dir) can ever satisfy.
        # Every real class still loads and checks fine as an independent
        # flat file; the package wrapper isn't needed for that.
        # Dict insertion order is the bundle's declared dependency order:
        # reusable components first and the connected entry model last. Sorting
        # alphabetically breaks valid multi-file bundles when a system file is
        # loaded before the component classes it instantiates.
        mo_filenames = [name for name in files if name.endswith(".mo") and name != "package.mo"]
        for filename in mo_filenames:
            (workdir / filename).write_text(files[filename], encoding="utf-8")

        # `getErrorString()` both reads *and clears* omc's accumulated error
        # buffer -- found live (see DECISIONS.md D54): capturing it only
        # once, after `simulate()`, lost a real load-time syntax error's
        # precise `[<file>:<line>...]` detail entirely, since `simulate()`'s
        # own internal processing had already cleared the buffer by then,
        # leaving only its own generic, locationless "Class ... not found"
        # fallback. Checking the load step in its own subprocess first
        # (mirroring the separate compile.mos/simulate.mos scripts the
        # standalone Compiler Agent design used) preserves that detail and
        # also skips a pointless `simulate()` attempt on input that never
        # even parsed.
        load_lines = ['loadModel(Modelica);'] + [f'loadFile("{name}");' for name in mo_filenames]
        load_lines.append("getErrorString();")
        (workdir / "load.mos").write_text("\n".join(load_lines) + "\n", encoding="utf-8")

        start = time.monotonic()
        output, load_timed_out = _run_omc_script(omc_path, "load.mos", workdir, timeout)
        errors: list[CompileError] = []
        if load_timed_out:
            errors.append(CompileError(
                error_id="ERR-002", severity="ERROR", category=ErrorCategory.UNKNOWN, file="",
                message=f"load step did not finish within {timeout:.0f}s (timed out)", raw=output,
            ))
        _parse_errors_into(output, errors)

        result_summary: dict[str, dict[str, float]] = {}
        if not errors:
            sim_lines = ['loadModel(Modelica);'] + [f'loadFile("{name}");' for name in mo_filenames]
            sim_lines.append(
                f"simulate({entry_class}, startTime={start_time}, stopTime={stop_time}, "
                f'numberOfIntervals={number_of_intervals}, tolerance={tolerance}, method="dassl", '
                f'outputFormat="csv");'
            )
            sim_lines.append("getErrorString();")
            (workdir / "simulate.mos").write_text("\n".join(sim_lines) + "\n", encoding="utf-8")

            output, sim_timed_out = _run_omc_script(omc_path, "simulate.mos", workdir, timeout)
            if sim_timed_out:
                # Best-effort belt-and-suspenders: `_run_omc_script` already
                # tree-kills `omc.exe` and everything under it on timeout,
                # but if the simulation .exe somehow detached from that tree
                # (observed live once), sweep for it by name too.
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", f"{entry_class}.exe"], capture_output=True, timeout=10,
                    )
                except Exception:  # noqa: BLE001 -- best-effort cleanup only
                    pass
                errors.append(CompileError(
                    error_id="ERR-002", severity="ERROR", category=ErrorCategory.UNKNOWN, file="",
                    message=f"simulate() did not finish within {timeout:.0f}s (timed out)", raw=output,
                ))
            _parse_errors_into(output, errors)

            # Real Result Validation (`new direction.txt` §22) needs the
            # actual simulated trajectory, not just a pass/fail string --
            # requesting csv output (native `omc` support, no extra
            # dependency) and summarizing it here (min/max/final per
            # variable, not the full time series) keeps this a small,
            # meaningful artifact rather than a raw dump of every timestep.
            result_csv = workdir / f"{entry_class}_res.csv"
            if not errors and result_csv.exists():
                result_summary = _parse_result_csv(result_csv)
                if result_csv_path is not None:
                    result_csv_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(result_csv, result_csv_path)

        duration = time.monotonic() - start

        status = CompileStatus.PASSED if ("The simulation finished successfully" in output and not errors) else CompileStatus.FAILED

        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(output, encoding="utf-8")
        if status == CompileStatus.FAILED and not errors:
            errors.append(CompileError(error_id="ERR-001", severity="ERROR", category=ErrorCategory.UNKNOWN,
                                       file="", message="Simulation did not finish successfully", raw=output))

        return CompileResult(
            execution_id=execution_id,
            status=status,
            backend="openmodelica",
            backend_version=_omc_version(omc_path, timeout),
            duration_seconds=duration,
            errors=errors,
            warnings=[],
            result_summary=result_summary,
        )
