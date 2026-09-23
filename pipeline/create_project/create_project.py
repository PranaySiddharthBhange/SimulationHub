"""Create a project and run the pipeline's shared Stage 1 extraction."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
OLLAMA_URL = "http://127.0.0.1:11434/api/tags"


def progress(message: str) -> None:
    print(f"[create_project] {message}", flush=True)


def fail(message: str) -> int:
    print(json.dumps({"status": "error", "error": message}, indent=2))
    return 1


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    return "-".join(part for part in cleaned.split("-") if part) or "project"


def ollama_ready() -> bool:
    try:
        with urlopen(OLLAMA_URL, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def start_ollama() -> bool:
    progress(f"checking Ollama at {OLLAMA_URL}")
    if ollama_ready():
        progress("Ollama is already running")
        return True
    executable = shutil.which("ollama")
    if not executable:
        progress("Ollama executable was not found on PATH")
        return False
    progress("Ollama is not running; starting ollama serve")
    kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
              "stdin": subprocess.DEVNULL, "start_new_session": True}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    try:
        subprocess.Popen([executable, "serve"], **kwargs)
    except OSError:
        progress("failed to start ollama serve")
        return False
    for second in range(1, 21):
        time.sleep(1)
        if ollama_ready():
            progress("Ollama is ready")
            return True
        if second in {5, 10, 15}:
            progress(f"waiting for Ollama ({second}s)")
    progress("Ollama did not become ready within 20 seconds")
    return False


def copy_source(source: Path, destination: Path) -> list[str]:
    copied: list[str] = []
    if source.is_file():
        target = destination / source.name
        shutil.copy2(source, target)
        return [target.relative_to(destination).as_posix()]
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            copied.append(relative.as_posix())
    return sorted(copied)


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)

def run_stage1_extraction(project_id: str, projects_root: Path, backend: str) -> dict:
    """Invoke the exact Stage 1 implementation and prompt used by the UI pipeline."""
    src_root = projects_root.parent / "src"
    sys.path.insert(0, str(src_root)) if str(src_root) not in sys.path else None
    load_env_file(projects_root.parent / ".env")
    try:
        from simulation_platform.reasoner_pipeline import execute_reasoner_stage_1
    except ImportError as exc:
        raise RuntimeError(f"pipeline dependencies are unavailable: {exc}") from exc
    progress("running shared Stage 1 document extraction")
    result = execute_reasoner_stage_1(project_id, projects_root=projects_root, stage1_backend=backend)
    details = result.details
    progress(f"Stage 1 extraction completed for {details.get('documents_understood', 0)} document(s)")
    return details


def create_project(request_path: Path) -> dict:
    progress(f"reading request: {request_path}")
    try:
        request = json.loads(request_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid request JSON: {exc}") from exc
    if not isinstance(request, dict):
        raise ValueError("request JSON must be an object")
    name = str(request.get("name", "")).strip()
    source_value = str(request.get("source_path", "")).strip()
    mode = str(request.get("mode", "local")).strip().lower()
    if not name:
        raise ValueError("name is required")
    if not source_value:
        raise ValueError("source_path is required")
    if mode not in {"local", "cloud"}:
        raise ValueError("mode must be local or cloud")
    source = Path(source_value).expanduser().resolve()
    if not source.exists():
        raise ValueError(f"source_path does not exist: {source}")
    progress(f"validated project {name!r} in {mode} mode")
    ollama_status = "not_checked"
    if mode == "local":
        ollama_status = "ready" if start_ollama() else "unavailable"
        if ollama_status != "ready":
            raise RuntimeError("local mode requires Ollama; it was not running and could not be started")

    pipeline_root = Path(__file__).resolve().parents[1]
    projects_root = pipeline_root / "projects"
    project_id = f"{slugify(name)}-{uuid.uuid4().hex[:8]}"
    project_root = projects_root / project_id
    documents = project_root / "documents"
    documents.mkdir(parents=True, exist_ok=False)
    progress(f"copying source files into {documents}")
    copied = copy_source(source, documents)
    progress(f"copied {len(copied)} document(s)")
    manifest = {
        "project_id": project_id,
        "name": name,
        "mode": mode,
        "stage1_backend": "ollama" if mode == "local" else "openai",
        "source_path": str(source),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "created",
        "ollama_status": ollama_status,
        "document_count": len(copied),
        "documents": copied,
    }
    for filename in ("meta.json", "project_manifest.json"):
        (project_root / filename).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    try:
        manifest["extraction"] = run_stage1_extraction(project_id, projects_root, manifest["stage1_backend"])
        manifest["extraction_status"] = "completed"
        manifest["status"] = "stage1_ready"
    except Exception as exc:
        manifest["extraction_status"] = "failed"
        manifest["extraction_error"] = f"{type(exc).__name__}: {exc}"
        manifest["status"] = "extraction_failed"
        for filename in ("meta.json", "project_manifest.json"):
            (project_root / filename).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        raise
    for filename in ("meta.json", "project_manifest.json"):
        (project_root / filename).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    progress(f"project created and extracted: {project_root}")
    return {"status": "created", "project_dir": str(project_root), "manifest": manifest}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return fail("usage: create_project.py request.json")
    try:
        result = create_project(Path(argv[1]).resolve())
    except (ValueError, RuntimeError, OSError) as exc:
        return fail(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))



