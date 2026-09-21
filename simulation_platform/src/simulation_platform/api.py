"""FastAPI backend for the web UI (see `../../../frontend`).

Wraps `reasoner_pipeline.py`'s four `execute_*` functions with: project
creation (file upload), a background thread that runs the full pipeline for
one project, live log streaming (tails `run.jsonl` -- the durable record
`utils/run_log.py` already writes, so the UI shows nothing the file itself
doesn't also have), and the Stage-2-ONLY human-in-the-loop clarification
pause/resume (see `execute_reasoner_stage_2`'s `clarify` callback -- Stage 1
and Stage 3 stay fully autonomous, the user's explicit choice).

In-memory `RunState` per project is deliberately process-local, not
persisted -- restarting this server loses "is a run currently paused
waiting on a human", same as restarting any dev server loses in-flight
request state; there is no checkpoint/resume, a run that was live when the
server died has to be started over. `run.jsonl` on disk is the durable
record; this registry is just what lets the API pause a live Python thread
and resume it later from an HTTP request.

What restarting the server does NOT lose: every project's `run.jsonl`
still replays in full over `/logs/stream` (see `stream_logs`), and
`_effective_status` (see below) derives an honest status from that log
plus the generated artifacts for any project this fresh process has no
live `RunState` for -- "done" if the final artifact exists, "error" if the
log's last line was a failed stage, "interrupted" otherwise -- rather than
defaulting every project a server restart forgot about to a misleading
"created", as if it had never been run.
"""

from __future__ import annotations

import json
import re
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from simulation_platform.config import PlatformSettings
from simulation_platform.contracts import Clarification
from simulation_platform.reasoner_pipeline import (
    execute_merge,
    execute_reasoner_stage_1,
    execute_reasoner_stage_2,
    execute_reasoner_stage_3,
    execute_reasoner_stage_4,
)
from simulation_platform.workspace import Workspace

app = FastAPI(title="Simulation Agent")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

_ws = Workspace(PlatformSettings.load().projects_root)

Status = Literal["created", "running", "awaiting_input", "done", "error", "interrupted"]


@dataclass
class RunState:
    status: Status = "created"
    current_stage: str | None = None
    error: str | None = None
    pending_clarifications: list[dict] | None = None
    event: threading.Event | None = field(default=None, repr=False)
    answers: dict[str, str] | None = field(default=None, repr=False)


_states: dict[str, RunState] = {}
_states_lock = threading.Lock()


def _state(project_id: str) -> RunState:
    with _states_lock:
        return _states.setdefault(project_id, RunState())


def _make_clarify(project_id: str):
    """Built fresh per run and handed to `execute_reasoner_stage_2` as its
    `clarify` callback -- called from the BACKGROUND PIPELINE THREAD, so it
    blocks that thread (not the request handling the run) until a person
    answers via POST .../clarifications/answer, or accepts the model's own
    suggested defaults via .../clarifications/use-defaults."""

    def clarify(clarifications: list[Clarification]) -> dict[str, str]:
        state = _state(project_id)
        state.pending_clarifications = [c.model_dump() for c in clarifications]
        state.status = "awaiting_input"
        state.event = threading.Event()
        state.event.wait()
        answers = state.answers or {}
        state.pending_clarifications = None
        state.answers = None
        state.status = "running"
        return answers

    return clarify


def _run_pipeline(project_id: str) -> None:
    state = _state(project_id)
    state.status = "running"
    state.error = None
    from simulation_platform.utils.run_log import RunLog
    RunLog(_ws.run_log_path(project_id)).event("run_started")
    try:
        state.current_stage = "stage_1"
        execute_reasoner_stage_1(project_id, projects_root=_ws.projects_root)
        state.current_stage = "merge"
        execute_merge(project_id, projects_root=_ws.projects_root)
        state.current_stage = "stage_2"
        execute_reasoner_stage_2(
            project_id, projects_root=_ws.projects_root, clarify=_make_clarify(project_id),
        )
        state.current_stage = "stage_3"
        execute_reasoner_stage_3(project_id, projects_root=_ws.projects_root)
        state.current_stage = "stage_4"
        execute_reasoner_stage_4(project_id, projects_root=_ws.projects_root)
        state.status = "done"
        state.current_stage = None
    except Exception as exc:  # noqa: BLE001 -- surfaced to the UI via /state, not swallowed
        traceback.print_exc()
        state.status = "error"
        state.error = f"{type(exc).__name__}: {exc}"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_") or "project"
    return f"{slug}_{uuid.uuid4().hex[:6]}"


def _meta_path(project_id: str) -> Path:
    return _ws.project_dir(project_id) / "meta.json"


def _artifacts(project_id: str) -> dict:
    sysml_dir = _ws.sysml_dir(project_id) / "generated"
    modelica_dir = _ws.modelica_dir(project_id) / "generated"
    validation_dir = _ws.validation_dir(project_id)
    understanding_path = _ws.extracted_dir(project_id) / "merged_understanding.txt"
    return {
        "understanding": understanding_path.exists(),
        "sysml": sysml_dir.exists() and any(sysml_dir.glob("*.sysml")),
        "modelica": modelica_dir.exists() and any(modelica_dir.glob("*.mo")),
        "validation": validation_dir.exists() and any(validation_dir.glob("*.report.json")),
    }


def _tail_last_event(project_id: str) -> dict | None:
    path = _ws.run_log_path(project_id)
    if not path.exists():
        return None
    last_line = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last_line = line
    if last_line is None:
        return None
    try:
        return json.loads(last_line)
    except ValueError:
        return None


def _effective_status(project_id: str) -> dict:
    """The live `RunState` when THIS process actually started or is
    tracking the run. Otherwise -- a fresh process, most commonly after a
    backend restart -- derive an honest status from `run.jsonl` and the
    generated artifacts instead of defaulting to the misleading "created",
    as if a project that clearly already ran had never been touched."""

    state = _state(project_id)
    if state.status != "created":
        return {
            "status": state.status, "current_stage": state.current_stage,
            "error": state.error, "pending_clarifications": state.pending_clarifications,
        }

    if _artifacts(project_id)["validation"]:
        return {"status": "done", "current_stage": None, "error": None, "pending_clarifications": None}

    last_event = _tail_last_event(project_id)
    if last_event is None:
        return {"status": "created", "current_stage": None, "error": None, "pending_clarifications": None}

    if last_event.get("event") == "stage_end" and last_event.get("ok") is False:
        error = f"{last_event.get('error_type')}: {last_event.get('error_message')}"
        return {"status": "error", "current_stage": None, "error": error, "pending_clarifications": None}

    return {
        "status": "interrupted", "current_stage": None,
        "error": "The server restarted (or was stopped) while this project was running. Nothing on disk was "
                 "lost, but the run itself didn't survive -- click Re-run to start over.",
        "pending_clarifications": None,
    }


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/projects")
async def create_project(name: str = Form(...), files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "attach at least one document")
    project_id = _slugify(name)
    docs_dir = _ws.documents_dir(project_id)
    docs_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        filename = Path(f.filename or "document").name
        (docs_dir / filename).write_bytes(await f.read())
    _ws.ensure_layout(project_id)
    _meta_path(project_id).write_text(json.dumps({"name": name}), encoding="utf-8")
    return {"project_id": project_id, "name": name}


@app.get("/api/projects")
def list_projects():
    root = _ws.projects_root
    if not root.exists():
        return []
    out = []
    for d in sorted(root.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        name = d.name
        meta_path = d / "meta.json"
        if meta_path.exists():
            try:
                name = json.loads(meta_path.read_text(encoding="utf-8")).get("name", d.name)
            except Exception:
                pass
        effective = _effective_status(d.name)
        out.append({
            "project_id": d.name, "name": name, "status": effective["status"],
            "current_stage": effective["current_stage"],
        })
    return out


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    root = _ws.project_dir(project_id)
    if not root.exists():
        raise HTTPException(404, "project not found")
    effective = _effective_status(project_id)
    return {
        "project_id": project_id,
        "status": effective["status"],
        "current_stage": effective["current_stage"],
        "error": effective["error"],
        "pending_clarifications": effective["pending_clarifications"],
        "artifacts": _artifacts(project_id),
    }


@app.post("/api/projects/{project_id}/run")
def run_project(project_id: str):
    if not _ws.project_dir(project_id).exists():
        raise HTTPException(404, "project not found")
    state = _state(project_id)
    if state.status in ("running", "awaiting_input"):
        raise HTTPException(409, "already running")
    threading.Thread(target=_run_pipeline, args=(project_id,), daemon=True).start()
    return {"status": "started"}


class AnswerBody(BaseModel):
    answers: dict[str, str]


@app.post("/api/projects/{project_id}/clarifications/answer")
def answer_clarifications(project_id: str, body: AnswerBody):
    state = _state(project_id)
    if state.status != "awaiting_input" or state.event is None:
        raise HTTPException(409, "no pending clarification for this project")
    state.answers = body.answers
    state.event.set()
    return {"status": "ok"}


@app.post("/api/projects/{project_id}/clarifications/use-defaults")
def use_default_clarifications(project_id: str):
    state = _state(project_id)
    if state.status != "awaiting_input" or state.event is None:
        raise HTTPException(409, "no pending clarification for this project")
    state.answers = {c["id"]: c["suggested_value"] for c in (state.pending_clarifications or [])}
    state.event.set()
    return {"status": "ok"}


@app.get("/api/projects/{project_id}/logs/stream")
def stream_logs(project_id: str):
    """Server-Sent Events: replays every line already in `run.jsonl` (the
    default `message` event, one JSON object per line -- see
    `utils/run_log.py`) then keeps polling for new ones, plus a `status`
    event on every tick so the UI's pipeline stepper and log panel share one
    connection. Ends the stream once the run reaches a terminal status and
    every byte written up to that point has been sent."""

    path = _ws.run_log_path(project_id)

    def gen():
        pos = 0
        while True:
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    f.seek(pos)
                    new_lines = f.readlines()
                    pos = f.tell()
                for line in new_lines:
                    line = line.rstrip("\n")
                    if line:
                        yield f"data: {line}\n\n"
            effective = _effective_status(project_id)
            yield f"event: status\ndata: {json.dumps(effective)}\n\n"
            current_size = path.stat().st_size if path.exists() else 0
            if effective["status"] in ("done", "error", "interrupted") and pos >= current_size:
                break
            time.sleep(0.5)

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/api/projects/{project_id}/artifacts/understanding")
def get_understanding(project_id: str):
    path = _ws.extracted_dir(project_id) / "merged_understanding.txt"
    if not path.exists():
        raise HTTPException(404, "not generated yet")
    return {"content": path.read_text(encoding="utf-8")}


@app.get("/api/projects/{project_id}/artifacts/sysml")
def get_sysml(project_id: str):
    gen_dir = _ws.sysml_dir(project_id) / "generated"
    files = sorted(gen_dir.glob("*.sysml")) if gen_dir.exists() else []
    if not files:
        raise HTTPException(404, "not generated yet")
    return {"filename": files[0].name, "content": files[0].read_text(encoding="utf-8")}


@app.get("/api/projects/{project_id}/artifacts/modelica")
def get_modelica(project_id: str):
    gen_dir = _ws.modelica_dir(project_id) / "generated"
    manifest_path = gen_dir / "modelica_manifest.json"
    payload_files: list[dict[str, str]] = []
    entry_class = None
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry_class = manifest.get("entry_class")
        for item in manifest.get("files", []):
            path = gen_dir / Path(item["filename"]).name
            if path.exists():
                payload_files.append({
                    "filename": path.name,
                    "role": item.get("role", "component"),
                    "content": path.read_text(encoding="utf-8"),
                })
    else:
        # Backward compatibility for projects generated by the former
        # single-file Stage 3.
        for path in sorted(gen_dir.glob("*.mo")) if gen_dir.exists() else []:
            payload_files.append({"filename": path.name, "role": "system", "content": path.read_text(encoding="utf-8")})
        if payload_files:
            entry_class = Path(payload_files[-1]["filename"]).stem
    if not payload_files:
        raise HTTPException(404, "not generated yet")
    combined = "\n\n".join(
        f"// --- {file['filename']} ({file['role']}) ---\n{file['content']}" for file in payload_files
    )
    return {
        "filename": f"{len(payload_files)} Modelica files",
        "entry_class": entry_class,
        "files": payload_files,
        "content": combined,
    }


@app.get("/api/projects/{project_id}/artifacts/validation")
def get_validation(project_id: str):
    """Stage 4's report: verdict, issues, assumptions, and root causes from
    an independent review of the REAL simulated trajectory against the
    actual problem statement -- see `reasoner_pipeline.execute_reasoner_stage_4`.
    `plots` lists the saved trajectory PNGs (fetch each via
    .../artifacts/validation/plot/{filename})."""

    val_dir = _ws.validation_dir(project_id)
    reports = sorted(val_dir.glob("*.report.json")) if val_dir.exists() else []
    if not reports:
        raise HTTPException(404, "not generated yet")
    report = json.loads(reports[-1].read_text(encoding="utf-8"))
    results_dir = _ws.modelica_dir(project_id) / "results"
    plots = sorted(p.name for p in results_dir.glob("*.png")) if results_dir.exists() else []
    return {"filename": reports[-1].name, "report": report, "plots": plots}


@app.get("/api/projects/{project_id}/artifacts/validation/plot/{filename}")
def get_validation_plot(project_id: str, filename: str):
    from fastapi.responses import FileResponse

    results_dir = _ws.modelica_dir(project_id) / "results"
    path = results_dir / Path(filename).name  # `.name` strips any path components -- no directory traversal
    if not path.exists() or path.suffix.lower() != ".png":
        raise HTTPException(404, "plot not found")
    return FileResponse(path, media_type="image/png")
