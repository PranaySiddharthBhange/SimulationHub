"""One-command launcher for the web UI.

    .venv/Scripts/python.exe run.py        (Windows)
    .venv/bin/python run.py                (macOS/Linux)

Checks Ollama (Stage 1) and OPENAI_API_KEY (merge/Stage 2/Stage 3) are in
place, starts the backend API and the frontend dev server (or reuses them
if already running), waits for both to answer, then prints and opens the
URL. Ctrl+C stops everything this script started.

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
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
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


def check_prerequisites() -> None:
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except ImportError:
        log("ERROR: fastapi/uvicorn not installed in this Python environment.")
        log(f"Run this from the project's venv, or first: {sys.executable} -m pip install -e .")
        sys.exit(1)

    try:
        import ollama
        ollama.Client().list()
        log("Ollama: running -- Stage 1 (document understanding) is ready.")
    except Exception:
        log(
            "WARNING: Ollama isn't reachable at http://localhost:11434 -- Stage 1 needs it. "
            "Start it with `ollama serve`, or install it from https://ollama.com/download. "
            "The UI will still come up; Stage 1 will fail until Ollama is running."
        )

    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except Exception:
        pass
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


def wait_until_up(url: str, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _reachable(url):
            return True
        time.sleep(0.5)
    return False


def kill_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            proc.terminate()


def start_backend() -> subprocess.Popen | None:
    health_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/health"
    if _reachable(health_url):
        log(f"backend already running on port {BACKEND_PORT} -- reusing it")
        return None
    log(f"starting backend on http://{BACKEND_HOST}:{BACKEND_PORT} ...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "simulation_platform.api:app",
         "--host", BACKEND_HOST, "--port", str(BACKEND_PORT)],
        cwd=ROOT, creationflags=NEW_GROUP_FLAGS,
    )


def start_frontend() -> subprocess.Popen | None:
    home_url = f"http://localhost:{FRONTEND_PORT}/"
    if _reachable(home_url):
        log(f"frontend already running on port {FRONTEND_PORT} -- reusing it")
        return None

    if not (FRONTEND_DIR / "node_modules").exists():
        log("frontend/node_modules missing -- running `npm install` (this may take a minute)...")
        subprocess.run([shutil.which("npm"), "install"], cwd=FRONTEND_DIR, check=True)

    log(f"starting frontend on {home_url} ...")
    return subprocess.Popen(
        [shutil.which("npm"), "run", "dev", "--", "--port", str(FRONTEND_PORT), "--strictPort"],
        cwd=FRONTEND_DIR, creationflags=NEW_GROUP_FLAGS,
    )


def main() -> None:
    log(f"project root: {ROOT}")
    check_prerequisites()

    backend = start_backend()
    frontend = start_frontend()
    started = [p for p in (backend, frontend) if p is not None]

    try:
        if not wait_until_up(f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/health", 30):
            log("WARNING: backend did not answer a health check within 30s -- check its output above.")
        if not wait_until_up(f"http://localhost:{FRONTEND_PORT}/", 60):
            log("WARNING: frontend did not come up within 60s -- check its output above.")

        url = f"http://localhost:{FRONTEND_PORT}/"
        log(f"ready -- open {url}")
        try:
            webbrowser.open(url)
        except Exception:
            pass

        if started:
            log("press Ctrl+C to stop the server(s) this script started")
            while True:
                for p in started:
                    if p.poll() is not None:
                        log("a server process exited unexpectedly -- stopping.")
                        raise KeyboardInterrupt
                time.sleep(1)
        else:
            log("both servers were already running -- nothing for this script to stop; exiting.")
    except KeyboardInterrupt:
        log("stopping...")
    finally:
        for p in started:
            kill_tree(p)
        if started:
            log("stopped.")


if __name__ == "__main__":
    main()
