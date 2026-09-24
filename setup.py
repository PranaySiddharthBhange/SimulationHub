"""One-time environment setup for this repo (Windows and Linux).

    python setup.py

Three phases, in order:
  1. SCAN -- checks every prerequisite `run.py` needs. Nothing is
     installed yet.
  2. CHOOSE -- prints what is already present (skipped) and what is
     missing, each with an approximate download/install size, and asks
     you (in the terminal -- no GUI) which of the missing ones to
     install. Dependencies are resolved automatically: selecting
     something that needs another missing piece pulls that piece in too,
     with a note explaining why.
  3. INSTALL -- installs only what you selected, in dependency order.
     Nothing already present is ever touched or reinstalled.

Components checked, in dependency order:
  1. OpenModelica compiler (omc)          -- winget on Windows, apt on Linux
  2. Real SysML v2 parser (conda env      -- installs Miniconda first if
     'sysml')                                conda itself is missing
  3. Node.js / npm                        -- winget on Windows, apt on Linux
  4. Docker                               -- winget/Docker Desktop on
                                              Windows, get.docker.com on Linux
  5. SysML v2 viewer (SysON, via           -- needs Docker; runs
     `docker compose up -d`)                  `docker compose up -d` in
                                                sysml_setup/
  6. Frontend npm packages (React etc.)   -- frontend/node_modules
  7. This repo's own Python environment   -- .venv + `pip install -e .[dev]`
  8. .env                                 -- copied from .env.example


PATH: whenever this script installs something whose own installer does
not reliably put it on PATH within the SAME session, it locates the
actual install directory and adds it both to this process's own
`os.environ["PATH"]` (so later steps in this same run can find it
immediately) and to your PERSISTENT PATH -- the current user's
`Environment\\Path` registry value on Windows, `~/.bashrc` and
`~/.profile` on Linux -- so future terminals have it too.

Size estimates are approximate (actual sizes vary by version/platform)
and exist only to help you decide what to install, not as a precise
disk-usage guarantee.
"""

from __future__ import annotations

import argparse
import glob
import os
import platform
import shutil
import subprocess
import tempfile
import venv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent
ROOT = REPO_ROOT / "pipeline"  # everything this script sets up (.venv, frontend/, .env, run.py) lives here
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
HAVE_APT = IS_LINUX and shutil.which("apt-get") is not None


# ---------------------------------------------------------------------------
# Small output/utility helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[setup] {msg}", flush=True)


def ok(msg: str) -> None:
    print(f"    [ok] {msg}", flush=True)


def skip(msg: str) -> None:
    print(f"    [already present] {msg}", flush=True)


def installing(msg: str) -> None:
    print(f"    [installing] {msg}", flush=True)


def manual(msg: str) -> None:
    print(f"    [ACTION NEEDED] {msg}", flush=True)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def find_first_existing(patterns: list[str]) -> Path | None:
    """First existing file matched by any of these glob patterns (env vars
    like %LOCALAPPDATA% / ~ are expanded first). Patterns are tried in
    order; the first one with any match wins."""
    for pattern in patterns:
        expanded = os.path.expandvars(os.path.expanduser(pattern))
        for match in sorted(glob.glob(expanded)):
            path = Path(match)
            if path.exists():
                return path
    return None


def sudo_prefix() -> list[str]:
    if os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    if have("sudo"):
        return ["sudo"]
    return []


def apt_install(packages: list[str], label: str) -> bool:
    if not HAVE_APT:
        return False
    installing(f"{label} (apt)")
    update = subprocess.run([*sudo_prefix(), "apt-get", "update"])
    if update.returncode != 0:
        return False
    result = subprocess.run([*sudo_prefix(), "apt-get", "install", "-y", *packages])
    return result.returncode == 0


def winget_install(package_id: str, label: str) -> bool:
    if not IS_WINDOWS or not have("winget"):
        return False
    installing(f"{label} (winget)")
    result = subprocess.run(
        ["winget", "install", "-e", "--id", package_id,
         "--accept-source-agreements", "--accept-package-agreements"],
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# PATH management -- immediate (this process) and persistent (future shells)
# ---------------------------------------------------------------------------

def _path_entries() -> list[str]:
    return [p for p in os.environ.get("PATH", "").split(os.pathsep) if p]


def add_to_path(directory: Path, label: str) -> None:
    directory_str = str(directory)
    existing = _path_entries()
    already_current = any(
        os.path.normcase(os.path.normpath(p)) == os.path.normcase(os.path.normpath(directory_str))
        for p in existing
    )
    if not already_current:
        os.environ["PATH"] = directory_str + os.pathsep + os.environ.get("PATH", "")
        ok(f"added {directory_str} to PATH for this session")

    if IS_WINDOWS:
        _persist_path_windows(directory_str, label)
    else:
        _persist_path_posix(directory_str, label)


def _persist_path_windows(directory_str: str, label: str) -> None:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                             winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current, kind = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current, kind = "", winreg.REG_EXPAND_SZ
            entries = [p for p in current.split(";") if p]
            if any(os.path.normcase(os.path.normpath(p)) == os.path.normcase(os.path.normpath(directory_str))
                   for p in entries):
                return  # already persisted
            new_value = current + (";" if current and not current.endswith(";") else "") + directory_str
            winreg.SetValueEx(key, "Path", 0, kind, new_value)
        try:
            import ctypes
            HWND_BROADCAST, WM_SETTINGCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x1A, 0x0002
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, None,
            )
        except Exception:
            pass
        ok(f"persisted {directory_str} to your user PATH (registry) for {label} -- new terminals will have it")
    except Exception as exc:
        manual(f"Could not persist PATH for {label} automatically ({exc}). "
               f"Add this to your PATH manually: {directory_str}")


def _persist_path_posix(directory_str: str, label: str) -> None:
    export_line = f'export PATH="{directory_str}:$PATH"'
    marker = f"# added by setup.py for {label}"
    targets = [Path.home() / ".bashrc", Path.home() / ".profile"]
    touched = []
    for rc_path in targets:
        try:
            content = rc_path.read_text(encoding="utf-8") if rc_path.exists() else ""
            if directory_str in content:
                continue
            with rc_path.open("a", encoding="utf-8") as f:
                f.write(f"\n{marker}\n{export_line}\n")
            touched.append(str(rc_path))
        except Exception as exc:
            manual(f"Could not update {rc_path} automatically ({exc}). "
                   f"Add this line to your shell rc file manually: {export_line}")
    if touched:
        ok(f"persisted {directory_str} to {', '.join(touched)} for {label} -- new terminals will have it")


# ---------------------------------------------------------------------------
# Component model: one CHECK (present?) and one INSTALL per piece, run in
# two separate passes so nothing installs before the user has chosen.
# ---------------------------------------------------------------------------

results: dict[str, str] = {}


@dataclass
class Component:
    key: str
    label: str
    size_estimate: str
    check: Callable[[], bool]
    install: Callable[[], None]
    requires: list[str] = field(default_factory=list)


def find_docker_compose_cmd() -> list[str] | None:
    if have("docker"):
        probe = subprocess.run(["docker", "compose", "version"], capture_output=True)
        if probe.returncode == 0:
            return ["docker", "compose"]
    if have("docker-compose"):
        return ["docker-compose"]
    return None


def install_miniconda_linux() -> Path | None:
    installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    target_dir = Path.home() / "miniconda3"
    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "miniconda_installer.sh"
        installing(f"downloading Miniconda installer to {script_path}")
        fetch = subprocess.run(["curl", "-fsSL", "-o", str(script_path), installer_url])
        if fetch.returncode != 0:
            return None
        installing(f"running Miniconda installer (installing to {target_dir})")
        result = subprocess.run(["bash", str(script_path), "-b", "-p", str(target_dir)])
        if result.returncode != 0:
            return None
    conda_bin = target_dir / "bin" / "conda"
    subprocess.run([str(conda_bin), "init"])
    return conda_bin if conda_bin.exists() else None


def find_conda_exe() -> Path | None:
    """Like find_first_existing, but also covers the common case where
    conda IS installed but simply is not on THIS process's PATH (a
    separate shell/installer added it to a profile this process never
    sourced) -- checked before ever concluding conda is missing."""
    if have("conda"):
        return Path(shutil.which("conda"))
    return find_first_existing([
        r"%USERPROFILE%\miniconda3\Scripts\conda.exe",
        r"%USERPROFILE%\anaconda3\Scripts\conda.exe",
        r"%LOCALAPPDATA%\miniconda3\Scripts\conda.exe",
        r"%LOCALAPPDATA%\Continuum\miniconda3\Scripts\conda.exe",
        r"C:\ProgramData\miniconda3\Scripts\conda.exe",
        r"C:\ProgramData\Anaconda3\Scripts\conda.exe",
        "~/miniconda3/bin/conda",
        "~/anaconda3/bin/conda",
        "/opt/conda/bin/conda",
    ])


def ensure_conda_available() -> Path | None:
    conda_exe = find_conda_exe()
    if conda_exe:
        add_to_path(conda_exe.parent, "conda")
        return conda_exe
    if IS_WINDOWS and winget_install("Anaconda.Miniconda3", "Miniconda (needed for the real SysML v2 parser)"):
        conda_exe = find_conda_exe()
        if conda_exe:
            add_to_path(conda_exe.parent, "Miniconda")
            add_to_path(conda_exe.parent.parent / "condabin", "Miniconda (condabin)")
            return conda_exe
        manual("Miniconda was installed but its location could not be found automatically -- open a NEW terminal and re-run this script.")
        return None
    if IS_LINUX and have("curl"):
        conda_bin = install_miniconda_linux()
        if conda_bin:
            add_to_path(conda_bin.parent, "Miniconda")
            return conda_bin
        return None
    manual("Install Miniconda from https://docs.conda.io/en/latest/miniconda.html, then re-run this script.")
    manual("Or create the env yourself once conda is available:")
    manual("  conda create -n sysml python=3.11 jupyterlab graphviz nodejs jupyter-sysml-kernel -c conda-forge")
    return None


def sysml_env_exists() -> bool:
    conda_exe = find_conda_exe()
    if conda_exe is None:
        return False
    env_list = subprocess.run([str(conda_exe), "env", "list"], capture_output=True, text=True).stdout
    return any(line.strip().split() and line.strip().split()[0] == "sysml" for line in env_list.splitlines())


# ---- check_* : True means "already present, nothing to do" --------------

def check_openmodelica() -> bool:
    return have("omc") or bool(find_first_existing([r"C:\Program Files\OpenModelica*\bin\omc.exe"]))


def check_sysml_kernel() -> bool:
    return sysml_env_exists()


def check_node() -> bool:
    return have("npm")


def check_docker() -> bool:
    return find_docker_compose_cmd() is not None


def check_sysml_viewer() -> bool:
    compose_cmd = find_docker_compose_cmd()
    compose_dir = REPO_ROOT / "sysml_setup"
    if not compose_cmd or not (compose_dir / "docker-compose.yml").exists():
        return False
    # -a (all statuses), not just running: a container docker compose
    # already created but that is currently STOPPED still counts as
    # "already set up" -- `docker compose up -d` just restarts it, it does
    # not re-pull or re-create anything.
    result = subprocess.run(
        [*compose_cmd, "ps", "-a", "--services"],
        cwd=compose_dir, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return bool(result.stdout.strip())
    # Docker Desktop/daemon not currently running is a DIFFERENT situation
    # from "never set up" -- confirmed live: `docker compose ps` fails with
    # "failed to connect to the docker API ... is the daemon running?" even
    # though the images/containers already exist on disk. Treating that as
    # "missing" would offer to re-download everything for no reason, so
    # this is reported as present-but-unverified instead, with a note.
    if "daemon" in result.stderr.lower() or "pipe" in result.stderr.lower():
        print("    [warn] Docker is installed but its daemon is not running right now, "
              "so the SysML viewer's actual state can't be verified -- assuming it is "
              "already set up. Start Docker Desktop and re-run this script for a "
              "definitive check.")
        return True
    return False


def check_frontend_packages() -> bool:
    return (ROOT / "frontend" / "node_modules").exists()


def check_python_env() -> bool:
    venv_python = ROOT / ".venv" / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
    if not venv_python.exists():
        return False
    probe = subprocess.run(
        [str(venv_python), "-c",
         "import fastapi, uvicorn, pydantic, langchain, openai, pymupdf, "
         "docx, openpyxl, dotenv, jupyter_client"],
        capture_output=True,
    )
    return probe.returncode == 0


def check_env_file() -> bool:
    return (ROOT / ".env").exists()


# ---- install_* : only ever called for things check_* found missing AND
#      the user selected -------------------------------------------------

def install_openmodelica() -> None:
    log("OpenModelica compiler (omc)")
    if winget_install("OpenModelica.OpenModelica", "OpenModelica (this download is large, please be patient)"):
        omc_exe = find_first_existing([r"C:\Program Files\OpenModelica*\bin\omc.exe"])
        if omc_exe:
            add_to_path(omc_exe.parent, "OpenModelica")
            results["OpenModelica"] = "installed via winget, PATH updated"
        else:
            results["OpenModelica"] = "installed via winget -- open a NEW terminal for PATH to update"
        return
    if apt_install(["omc"], "OpenModelica (this download is large, please be patient)"):
        results["OpenModelica"] = "installed via apt"
        return
    if IS_LINUX:
        manual("apt does not have 'omc' on this system. Add OpenModelica's own repo and retry, following:")
        manual("  https://openmodelica.org/download/download-linux/")
    else:
        manual("Install OpenModelica from https://openmodelica.org/download/download-windows/, then re-run this script.")
    results["OpenModelica"] = "MISSING -- install manually"


def install_sysml_kernel() -> None:
    log("Real SysML v2 parser (conda env 'sysml')")
    conda_exe = ensure_conda_available()
    if conda_exe is None:
        results["SysML kernel"] = "MISSING -- conda not available, install manually"
        return
    conda_cmd = str(conda_exe)
    if sysml_env_exists():
        skip("conda env 'sysml' already exists")
        results["SysML kernel"] = "already present"
        return
    installing("conda env 'sysml' with the real SysML v2 Jupyter kernel (this can take several minutes)")
    result = subprocess.run([
        conda_cmd, "create", "-y", "-n", "sysml", "python=3.11", "jupyterlab",
        "graphviz", "nodejs", "jupyter-sysml-kernel", "-c", "conda-forge",
    ])
    results["SysML kernel"] = "created" if result.returncode == 0 else "CREATE FAILED -- see output above"


def install_node() -> None:
    log("Node.js / npm")
    if winget_install("OpenJS.NodeJS.LTS", "Node.js LTS"):
        node_exe = find_first_existing([
            r"C:\Program Files\nodejs\node.exe",
            r"C:\Program Files (x86)\nodejs\node.exe",
        ])
        if node_exe:
            add_to_path(node_exe.parent, "Node.js")
            results["Node.js/npm"] = "installed via winget, PATH updated"
        else:
            results["Node.js/npm"] = "installed via winget -- open a NEW terminal for PATH to update"
        return
    if apt_install(["nodejs", "npm"], "Node.js + npm"):
        results["Node.js/npm"] = "installed via apt"
        return
    manual("Install Node.js (LTS) from https://nodejs.org/, then re-run this script.")
    results["Node.js/npm"] = "MISSING -- install manually"


def install_docker() -> None:
    log("Docker")
    if IS_WINDOWS and winget_install("Docker.DockerDesktop", "Docker Desktop"):
        manual("Docker Desktop was just installed -- it needs to be launched at least once "
               "(first-run setup, possibly a sign-in and a restart) before 'docker compose' "
               "works. Start Docker Desktop, then re-run this script.")
        results["Docker"] = "installed via winget -- start Docker Desktop, then re-run this script"
        return
    if IS_LINUX and have("curl"):
        installing("Docker Engine (official get.docker.com script)")
        result = subprocess.run("curl -fsSL https://get.docker.com | sh", shell=True)
        if result.returncode == 0:
            manual("Docker installed -- you may need to log out and back in (or run "
                   "'newgrp docker') for group membership to take effect, then re-run this script.")
            results["Docker"] = "installed -- log out/in for group membership, then re-run this script"
        else:
            manual("Docker install script failed -- see output above.")
            results["Docker"] = "INSTALL FAILED -- see output above"
        return
    manual("Install Docker from https://docs.docker.com/get-docker/, then re-run this script.")
    results["Docker"] = "MISSING -- install manually"


def install_sysml_viewer() -> None:
    log("SysML v2 viewer (SysON, via docker compose up)")
    compose_cmd = find_docker_compose_cmd()
    if compose_cmd is None:
        manual("docker compose is not available yet -- install/start Docker first, then re-run this script.")
        results["SysML viewer"] = "SKIPPED -- no docker compose"
        return
    compose_dir = REPO_ROOT / "sysml_setup"
    if not (compose_dir / "docker-compose.yml").exists():
        manual(f"{compose_dir / 'docker-compose.yml'} not found -- cannot start the SysML viewer.")
        results["SysML viewer"] = "MISSING -- docker-compose.yml not found"
        return
    installing("docker compose up -d (SysON viewer + Postgres) -- first pull can take several minutes")
    result = subprocess.run([*compose_cmd, "up", "-d"], cwd=compose_dir)
    results["SysML viewer"] = "started -- open http://localhost:8080/" if result.returncode == 0 else "FAILED -- see output above"


def install_frontend_packages() -> None:
    log("Frontend npm packages")
    if not have("npm"):
        manual("Skipped -- npm not available. Install/select Node.js first, then re-run this script.")
        results["Frontend packages"] = "SKIPPED -- no npm"
        return
    installing("npm install (in frontend/)")
    npm = shutil.which("npm")
    result = subprocess.run([npm, "install"], cwd=ROOT / "frontend")
    results["Frontend packages"] = "installed" if result.returncode == 0 else "FAILED -- see output above"


def install_python_env() -> None:
    log("This repo's Python environment (.venv + dependencies)")
    venv_dir = ROOT / ".venv"
    venv_python = venv_dir / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
    if not venv_python.exists():
        installing("creating .venv")
        venv.EnvBuilder(with_pip=True).create(venv_dir)
    installing("pip install -e .[dev] (this repo's own package + pytest)")
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "--quiet"], check=True)
    result = subprocess.run([str(venv_python), "-m", "pip", "install", "-e", ".[dev]"], cwd=ROOT)
    results["Python environment"] = "installed" if result.returncode == 0 else "FAILED -- see output above"


def install_env_file() -> None:
    log(".env")
    env_path = ROOT / ".env"
    env_example_path = ROOT / ".env.example"
    if not env_example_path.exists():
        manual(".env.example not found -- cannot create .env automatically.")
        results[".env"] = "MISSING -- .env.example not found"
        return
    shutil.copyfile(env_example_path, env_path)
    installing("created .env from .env.example")
    manual("Open .env and set OPENAI_API_KEY before running the pipeline.")
    results[".env"] = "created from .env.example -- NEEDS OPENAI_API_KEY"


COMPONENTS: list[Component] = [
    Component("openmodelica", "OpenModelica compiler (omc)", "~1.5 GB",
              check_openmodelica, install_openmodelica),
    Component("sysml_kernel", "Real SysML v2 parser (conda env 'sysml')", "~1-2 GB (Miniconda + env packages)",
              check_sysml_kernel, install_sysml_kernel),
    Component("node", "Node.js / npm", "~50-100 MB",
              check_node, install_node),
    Component("docker", "Docker", "~500 MB-1 GB",
              check_docker, install_docker),
    Component("sysml_viewer", "SysML v2 viewer (SysON, docker compose up)", "~500 MB-1 GB (container images)",
              check_sysml_viewer, install_sysml_viewer, requires=["docker"]),
    Component("frontend", "Frontend npm packages (React etc.)", "~250-400 MB",
              check_frontend_packages, install_frontend_packages, requires=["node"]),
    Component("python_env", "This repo's Python environment (.venv + deps)", "~400-600 MB",
              check_python_env, install_python_env),
    Component("env_file", ".env (copied from .env.example)", "<1 KB",
              check_env_file, install_env_file),
]


# ---------------------------------------------------------------------------
# Phase 1: scan
# ---------------------------------------------------------------------------

def scan() -> tuple[list[Component], list[Component]]:
    log("Scanning for what's already present (nothing is installed in this step) ...")
    present, missing = [], []
    for component in COMPONENTS:
        try:
            is_present = component.check()
        except Exception as exc:
            print(f"    [warn] could not check {component.label} ({exc}) -- treating as missing")
            is_present = False
        (present if is_present else missing).append(component)
        tag = "present" if is_present else "missing"
        print(f"    [{tag:>7}] {component.label}")
    return present, missing


# ---------------------------------------------------------------------------
# Phase 2: choose (terminal only, no GUI)
# ---------------------------------------------------------------------------

def choose(missing: list[Component]) -> list[Component]:
    print()
    print("==================== What's missing ====================")
    for i, component in enumerate(missing, start=1):
        extra = f"  (needs: {', '.join(component.requires)})" if component.requires else ""
        print(f"  [{i}] {component.label:<48} {component.size_estimate}{extra}")
    print("==========================================================")
    print()
    print("Choose what to install:")
    print("  - comma-separated numbers, e.g. 1,3,5")
    print("  - 'all' to install everything listed above")
    print("  - 'none' to skip installing and just exit")
    try:
        raw = input("> ").strip().lower()
    except (EOFError, OSError):
        print("(no interactive input available -- defaulting to 'none')")
        raw = "none"

    if raw in ("", "none", "n"):
        return []
    if raw in ("all", "a"):
        selected = list(missing)
    else:
        by_index = {i: c for i, c in enumerate(missing, start=1)}
        selected = []
        for token in raw.split(","):
            token = token.strip()
            if not token.isdigit() or int(token) not in by_index:
                print(f"    (ignoring unrecognized choice: '{token}')")
                continue
            selected.append(by_index[int(token)])

    # Pull in required-but-unselected prerequisites automatically.
    selected_keys = {c.key for c in selected}
    present_keys = {c.key for c in COMPONENTS if c not in missing}
    changed = True
    while changed:
        changed = False
        for component in list(selected):
            for req_key in component.requires:
                if req_key in present_keys or req_key in selected_keys:
                    continue
                req_component = next((c for c in missing if c.key == req_key), None)
                if req_component is None:
                    continue
                print(f"    (also selecting '{req_component.label}' -- required by '{component.label}')")
                selected.append(req_component)
                selected_keys.add(req_key)
                changed = True

    # Keep them in the same dependency-safe order COMPONENTS was defined in.
    order = {c.key: i for i, c in enumerate(COMPONENTS)}
    selected.sort(key=lambda c: order[c.key])
    return selected


# ---------------------------------------------------------------------------
# Phase 3: install only what was selected
# ---------------------------------------------------------------------------

def install_selected(selected: list[Component]) -> None:
    print()
    print(f"Installing {len(selected)} component(s) ...")
    for component in selected:
        component.install()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    if not IS_WINDOWS and not IS_LINUX:
        log(f"WARNING: this script only automates installs on Windows and Linux; "
            f"detected {platform.system()}. It will still scan and print "
            f"manual-install instructions for anything missing.")

    log(f"repo root: {ROOT}")
    log(f"platform: {platform.system()} {platform.release()}")
    print()

    present, missing = scan()

    for component in present:
        results[component.label] = "already present"

    if not missing:
        print()
        print("Everything required is already present -- nothing to install.")
    else:
        selected = choose(missing)
        skipped = [c for c in missing if c not in selected]
        for component in skipped:
            results[component.label] = "skipped by user"
        if selected:
            install_selected(selected)
        else:
            print("Nothing selected -- exiting without installing anything.")

    print()
    print("==================== Setup summary ====================")
    for key, value in results.items():
        print(f"  {key:<48} {value}")
    print("=========================================================")
    print()

    any_missing = any("MISSING" in v or "FAILED" in v for v in results.values())
    if any_missing:
        print("Some required tools still need attention -- see [ACTION NEEDED]/FAILED lines above.")
    else:
        launcher = "pipeline\\.venv\\Scripts\\python.exe pipeline\\run.py" if IS_WINDOWS else "pipeline/.venv/bin/python pipeline/run.py"
        print("Start the app with:")
        print(f"    {launcher}")


if __name__ == "__main__":
    main()
