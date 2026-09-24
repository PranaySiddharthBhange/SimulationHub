"""One-command launcher for the web UI.

    .venv/Scripts/python.exe run.py        (Windows)
    .venv/bin/python run.py                (macOS/Linux)

Loads the shared environment, starts Ollama, ensures the configured local
model is installed, starts the backend API and frontend dev server, waits
for every service to become ready, then opens the UI. An occupied port is
skipped so every launcher invocation owns its backend and frontend. Ctrl+C
stops every process it started.

Tree-kills child processes on shutdown rather than a plain .terminate() --
`npm run dev` spawns its own node/vite process, and a plain terminate()
here has repeatedly left that orphaned on Windows elsewhere in this
project (same class of bug as the `omc`/Ollama process leaks fixed in
`tools/modelica_validator.py`).
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import json
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173
OLLAMA_URL = "http://127.0.0.1:11434"
APPLICATION_MARKER = "hackathon-simulation-pipeline"
IS_WINDOWS = platform.system() == "Windows"
NEW_GROUP_FLAGS = subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0


def log(msg: str) -> None:
    print(f"[run] {msg}", flush=True)


def _reachable(url: str, timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status < 500
    except Exception:
        return False


def _read_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return json.load(response)
    except Exception:
        return {}


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def choose_port(host: str, preferred: int, marker_path: str, service: str) -> tuple[int, bool]:
    """Return a free port without stopping or reusing an existing process."""
    for port in range(preferred, preferred + 20):
        if not _port_in_use(host, port):
            return port, False
        marker = _read_json(f"http://{host}:{port}{marker_path}").get("application")
        if marker == APPLICATION_MARKER:
            log(f"{service} from another launcher is already on port {port} -- trying {port + 1}")
        else:
            log(f"port {port} is occupied by another process -- trying {port + 1}")
    raise RuntimeError(f"no free {service} port found in range {preferred}-{preferred + 19}")


def load_environment() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        env_path = ROOT / ".env"
        if env_path.exists():
            for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def check_prerequisites() -> None:
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except ImportError:
        log("ERROR: fastapi/uvicorn not installed in this Python environment.")
        log(f"Run this from the project's venv, or first: {sys.executable} -m pip install -e .")
        sys.exit(1)

    if shutil.which("ollama") is None and not _reachable(f"{OLLAMA_URL}/api/tags"):
        log("ERROR: Ollama is not installed or available on PATH.")
        log("Install it from https://ollama.com/download and run this launcher again.")
        sys.exit(1)
    if os.environ.get("OPENAI_API_KEY"):
        log("OpenAI API key: found -- Merge, Stage 2 and Stage 3 are ready.")
    else:
        log(
            "WARNING: OPENAI_API_KEY is not set in .env -- Merge/Stage 2/Stage 3 need it. "
            "Add it directly to local-simulation-agent/.env (never paste it in chat)."
        )

    if shutil.which("npm") is None:
        log("ERROR: npm not found on PATH -- install Node.js from https://nodejs.org first.")
        sys.exit(1)


def start_ollama() -> subprocess.Popen | None:
    tags_url = f"{OLLAMA_URL}/api/tags"
    if _reachable(tags_url):
        log("Ollama already running -- reusing it")
        return None

    executable = shutil.which("ollama")
    if executable is None:
        raise RuntimeError("Ollama is required but its executable was not found")

    log(f"starting Ollama on {OLLAMA_URL} ...")
    process = subprocess.Popen(
        [executable, "serve"], cwd=ROOT, creationflags=NEW_GROUP_FLAGS,
    )
    if not wait_until_up(tags_url, 30):
        kill_tree(process)
        raise RuntimeError("Ollama did not become ready within 30 seconds")
    log("Ollama is ready")
    return process


def ensure_local_model() -> None:
    model = os.environ.get("STAGE_1_EXTRACTION_MODEL", "gemma3:4b").strip()
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as response:
        payload = json.load(response)
    installed = {
        item.get("name") or item.get("model")
        for item in payload.get("models", [])
    }
    if model in installed or f"{model}:latest" in installed:
        log(f"local model ready: {model}")
        return

    executable = shutil.which("ollama")
    if executable is None:
        raise RuntimeError(f"local model {model} is missing and `ollama pull` is unavailable")
    log(f"local model {model} is missing -- downloading it now ...")
    subprocess.run([executable, "pull", model], cwd=ROOT, check=True)
    log(f"local model ready: {model}")


def wait_until_up(url: str, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _reachable(url):
            return True
        time.sleep(0.5)
    return False


def kill_tree(proc: subprocess.Popen) -> None:
    if IS_WINDOWS:
        # Run taskkill even when the direct parent has just exited. npm.cmd can
        # disappear before its node/vite child, and returning early here left
        # that child printing logs after run.py stopped.
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            if proc.poll() is None:
                proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def _windows_listening_pids(port: int) -> set[int]:
    """Return Windows PIDs currently listening on a TCP port."""
    if not IS_WINDOWS:
        return set()
    result = subprocess.run(
        ["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    pids: set[int] = set()
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 5 or fields[0].upper() != "TCP" or fields[3].upper() != "LISTENING":
            continue
        try:
            local_port = int(fields[1].rsplit(":", 1)[1])
            pid = int(fields[-1])
        except (ValueError, IndexError):
            continue
        if local_port == port:
            pids.add(pid)
    return pids


def ensure_service_stopped(service: str, host: str, port: int, marker_path: str | None) -> None:
    """Remove an orphaned child that still owns a launcher-managed port."""
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline and _port_in_use(host, port):
        time.sleep(0.2)
    if not _port_in_use(host, port):
        return

    # Backend/frontend ports are killed only when their marker proves that
    # they belong to this application. Ollama has no marker, but reaches this
    # path only when this launcher itself started it.
    if marker_path is not None:
        marker = _read_json(f"http://{host}:{port}{marker_path}").get("application")
        if marker != APPLICATION_MARKER:
            log(f"WARNING: {service} port {port} now belongs to another process; leaving it running")
            return
    if IS_WINDOWS:
        for pid in _windows_listening_pids(port):
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    if _port_in_use(host, port):
        log(f"WARNING: {service} is still listening on port {port}")


def start_backend() -> tuple[subprocess.Popen | None, int]:
    port, reusable = choose_port(BACKEND_HOST, BACKEND_PORT, "/api/health", "backend")
    if reusable:
        return None, port
    log(f"starting backend on http://{BACKEND_HOST}:{port} ...")
    backend_env = os.environ.copy()
    src_path = str(ROOT / "src")
    backend_env["PYTHONPATH"] = src_path + os.pathsep + backend_env.get("PYTHONPATH", "")
    # --reload watches src/ so an edit to a prompt, a contract or the pipeline
    # takes effect on the next stage run. Without it uvicorn imports everything
    # once at startup and holds it: edits to the Stage 3 and Stage 4 prompts
    # made while the UI was up were silently ignored, and the run that followed
    # looked like the prompt fix had failed rather than like stale code. The
    # watcher is scoped to src/ so a written artifact under projects/ -- every
    # stage writes several -- cannot restart the backend mid-run.
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "simulation_platform.api:app",
         "--host", BACKEND_HOST, "--port", str(port),
         "--reload", "--reload-dir", src_path],
        cwd=ROOT, env=backend_env, creationflags=NEW_GROUP_FLAGS,
    ), port


def start_frontend(backend_port: int) -> tuple[subprocess.Popen | None, int]:
    port, reusable = choose_port(
        FRONTEND_HOST, FRONTEND_PORT, "/runtime-marker.json", "frontend",
    )
    if reusable:
        return None, port

    if not (FRONTEND_DIR / "node_modules").exists():
        log("frontend/node_modules missing -- running `npm install` (this may take a minute)...")
        subprocess.run([shutil.which("npm"), "install"], cwd=FRONTEND_DIR, check=True)

    home_url = f"http://{FRONTEND_HOST}:{port}/"
    log(f"starting frontend on {home_url} ...")
    frontend_env = os.environ.copy()
    frontend_env["BACKEND_URL"] = f"http://{BACKEND_HOST}:{backend_port}"
    return subprocess.Popen(
        [shutil.which("npm"), "run", "dev", "--", "--host", FRONTEND_HOST,
         "--port", str(port), "--strictPort"],
        cwd=FRONTEND_DIR, env=frontend_env, creationflags=NEW_GROUP_FLAGS,
    ), port


def main() -> None:
    log(f"project root: {ROOT}")
    load_environment()
    check_prerequisites()

    started: list[subprocess.Popen] = []
    managed_services: list[tuple[str, subprocess.Popen, str, int, str | None]] = []

    try:
        ollama_process = start_ollama()
        if ollama_process is not None:
            started.append(ollama_process)
            managed_services.append(("Ollama", ollama_process, "127.0.0.1", 11434, None))
        ensure_local_model()

        backend, backend_port = start_backend()
        if backend is not None:
            started.append(backend)
            managed_services.append(("backend", backend, BACKEND_HOST, backend_port, "/api/health"))
        frontend, frontend_port = start_frontend(backend_port)
        if frontend is not None:
            started.append(frontend)
            managed_services.append(("frontend", frontend, FRONTEND_HOST, frontend_port, "/runtime-marker.json"))

        if not wait_until_up(f"http://{BACKEND_HOST}:{backend_port}/api/health", 30):
            raise RuntimeError("backend did not answer its health check within 30 seconds")
        if not wait_until_up(f"http://{FRONTEND_HOST}:{frontend_port}/", 60):
            raise RuntimeError("frontend did not become ready within 60 seconds")

        url = f"http://{FRONTEND_HOST}:{frontend_port}/"
        log(f"ready -- open {url}")
        try:
            webbrowser.open(url)
        except Exception:
            pass

        if started:
            log("press Ctrl+C to stop every service this launcher started")
            while True:
                for p in started:
                    if p.poll() is not None:
                        raise RuntimeError(f"a managed process exited unexpectedly with code {p.returncode}")
                time.sleep(1)
        else:
            log("all services were already running -- nothing for this launcher to manage; exiting.")
    except KeyboardInterrupt:
        log("stopping...")
    except Exception as exc:
        log(f"ERROR: {exc}")
        raise
    finally:
        for _, process, _, _, _ in reversed(managed_services):
            kill_tree(process)
        for service, _, host, port, marker_path in reversed(managed_services):
            ensure_service_stopped(service, host, port, marker_path)
        if started:
            log("stopped.")


if __name__ == "__main__":
    main()
