"""FastAPI backend for the web UI (see `../../../frontend`).

Wraps `reasoner_pipeline.py`'s four `execute_*` functions with: project
creation (file upload), a background thread that runs the full pipeline for
one project, live log streaming (tails `run.jsonl` -- the durable record
`utils/run_log.py` already writes, so the UI shows nothing the file itself
doesn't also have), and human-in-the-loop clarification pauses after Merge
and during SysML generation.

In-memory `RunState` per project is deliberately process-local, not
persisted -- restarting this server loses the live Python thread a run was
blocked on, same as restarting any dev server loses in-flight request
state; there is no general checkpoint/resume, a run that was live when the
server died has to be started over. `run.jsonl` on disk is the durable
record; this registry is what lets the API pause a live thread and resume
it later from an HTTP request.

The one deliberate exception is a clarification pause itself (see
`_make_clarify`): the question set survives a restart on disk, so
`_effective_status` can still report "awaiting_input" with no live
`RunState`, and the answer endpoints can still record an answer with no
live thread to wake -- straight into `clarified_answers.json` for a
Merge/Confirm pause, or as human notes folded into the next Design
attempt's context for a Stage 2 pause. Everything else about a run that
was live when the server died still has to be started over.

What restarting the server does NOT lose otherwise: every project's
`run.jsonl` still replays in full over `/logs/stream` (see `stream_logs`),
and `_effective_status` (see below) derives an honest status from that log
plus the generated artifacts for any project this fresh process has no
live `RunState` for -- "done" if the final artifact exists, "error" if the
log's last line was a failed stage, "interrupted" otherwise -- rather than
defaulting every project a server restart forgot about to a misleading
"created", as if it had never been run.
"""

from __future__ import annotations

import io
import json
import re
import shutil
import threading
import time
import traceback
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from simulation_platform.config import PlatformSettings
from simulation_platform.contracts import Clarification
from simulation_platform.reasoner_pipeline import (
    execute_clarify,
    execute_merge,
    execute_reasoner_stage_1,
    execute_reasoner_stage_2,
    execute_reasoner_stage_3_and_4,
)
from simulation_platform.workspace import Workspace

app = FastAPI(title="Simulation Agent")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

_ws = Workspace(PlatformSettings.load().projects_root)

Status = Literal["created", "stage1_ready", "ready", "running", "awaiting_input", "done", "error", "interrupted"]


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


def _pending_clarification_path(project_id: str) -> Path:
    return _ws.extracted_dir(project_id) / "pending_clarification.json"


def _make_clarify(project_id: str, stage: str):
    """Build a callback for a Merge/Confirm or Stage 2/Design clarification
    pause.

    The callback is called from the BACKGROUND PIPELINE THREAD, so it
    blocks that thread (not the request handling the run) until a person
    answers via POST .../clarifications/answer, or accepts suggested defaults
    via .../clarifications/use-defaults when defaults are available.

    The question set (and which stage raised it) is also written to disk for
    the duration of the pause. A server restart while a person is
    mid-decision used to just lose the pause outright (see the module
    docstring) -- now `_effective_status` can still report it from this
    file, and the answer endpoints can still record an answer with no live
    thread left to wake: straight into clarified_answers.json for a
    Merge/Confirm pause (the format `execute_clarify` itself reads back), or
    as human notes folded into the next Design attempt's context for a
    Stage 2 pause, since a fresh draft can raise a different question set
    with no stable id to resume against -- see `_take_stage2_human_notes`."""

    def clarify(clarifications: list[Clarification]) -> dict[str, str]:
        state = _state(project_id)
        state.pending_clarifications = [c.model_dump() for c in clarifications]
        state.status = "awaiting_input"
        state.event = threading.Event()
        _pending_clarification_path(project_id).write_text(
            json.dumps({"stage": stage, "clarifications": state.pending_clarifications}, indent=2),
            encoding="utf-8",
        )
        state.event.wait()
        answers = state.answers or {}
        state.pending_clarifications = None
        state.answers = None
        state.status = "running"
        _pending_clarification_path(project_id).unlink(missing_ok=True)
        return answers

    return clarify


def _record_clarify_answers_from_disk(project_id: str, stage: str, clarifications: list[dict], answers: dict[str, str]) -> None:
    """Recovery path for the answer endpoints when the pause was inherited
    from disk after a restart (no live thread to wake -- see `_make_clarify`).
    Records the answer durably enough that the relevant stage won't just
    pause and ask the same thing again the next time it runs."""
    if stage == "clarify":
        from simulation_platform.reasoner_pipeline import _answers_record

        clarification_objs = [Clarification(**item) for item in clarifications]
        answers_path = _ws.extracted_dir(project_id) / "clarified_answers.json"
        answers_path.write_text(
            json.dumps(_answers_record(clarification_objs, answers), indent=2) + "\n", encoding="utf-8",
        )
    elif stage == "stage_2":
        from simulation_platform.reasoner_pipeline import _stage2_human_notes_path
        from simulation_platform.utils.run_log import RunLog

        notes = [
            {"question": c.get("question", ""), "answer": answers.get(c["id"], c.get("suggested_value", ""))}
            for c in clarifications
        ]
        _stage2_human_notes_path(_ws, project_id).write_text(json.dumps(notes, indent=2), encoding="utf-8")
        RunLog(_ws.run_log_path(project_id)).event("clarification_answered", stage=2, answers=answers)
    _pending_clarification_path(project_id).unlink(missing_ok=True)


def _run_pipeline(project_id: str) -> None:
    state = _state(project_id)
    state.status = "running"
    state.error = None
    from simulation_platform.utils.run_log import RunLog
    RunLog(_ws.run_log_path(project_id)).event("run_started")
    try:
        meta = {}
        if _meta_path(project_id).exists():
            meta = json.loads(_meta_path(project_id).read_text(encoding="utf-8"))
        stage1_backend = meta.get("stage1_backend", "ollama")
        notes_dir = _ws.extracted_dir(project_id) / "understanding"
        stage1_ready = (
            meta.get("extraction_status") == "completed"
            and notes_dir.exists()
            and any(notes_dir.glob("*.txt"))
        )
        if stage1_ready:
            RunLog(_ws.run_log_path(project_id)).event(
                "stage_skipped", stage="stage_1", reason="completed by create_project script",
            )
        else:
            state.current_stage = "stage_1"
            execute_reasoner_stage_1(
                project_id, projects_root=_ws.projects_root, stage1_backend=stage1_backend,
            )
        state.current_stage = "merge"
        execute_merge(project_id, projects_root=_ws.projects_root)
        state.current_stage = "clarify"
        execute_clarify(
            project_id, projects_root=_ws.projects_root,
            clarify=_make_clarify(project_id, "clarify"),
        )
        state.current_stage = "stage_2"
        execute_reasoner_stage_2(
            project_id, projects_root=_ws.projects_root, clarify=_make_clarify(project_id, "stage_2"),
        )
        state.current_stage = "stage_3"
        # Generate + independently validate, looping the two together when
        # validation finds the result behaviorally wrong -- see
        # `execute_reasoner_stage_3_and_4`'s own docstring for why this is
        # not just Stage 3 followed by Stage 4.
        execute_reasoner_stage_3_and_4(project_id, projects_root=_ws.projects_root)
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


def _read_meta(project_id: str) -> dict:
    path = _meta_path(project_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_meta(project_id: str, meta: dict) -> None:
    _meta_path(project_id).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def _artifacts(project_id: str) -> dict:
    sysml_dir = _ws.sysml_dir(project_id) / "generated"
    modelica_dir = _ws.modelica_dir(project_id) / "generated"
    validation_dir = _ws.validation_dir(project_id)
    results_dir = _ws.modelica_dir(project_id) / "results"
    understanding_path = _ws.extracted_dir(project_id) / "merged_understanding.md"
    clarified_path = _ws.extracted_dir(project_id) / "clarified_answers.json"
    diagram_path = _ws.extracted_dir(project_id) / "system_flow.mmd"
    notes_dir = _ws.extracted_dir(project_id) / "understanding"
    extraction = notes_dir.exists() and any(notes_dir.glob("*.txt"))
    return {
        "extraction": extraction,
        "understanding": understanding_path.exists() or extraction,
        "merged_understanding": understanding_path.exists(),
        "clarified": clarified_path.exists(),
        "diagram": diagram_path.exists(),
        "sysml": sysml_dir.exists() and any(sysml_dir.glob("*.sysml")),
        "modelica": modelica_dir.exists() and any(modelica_dir.glob("*.mo")),
        "validation": validation_dir.exists() and any(validation_dir.glob("*.report.json")),
        "result": results_dir.exists() and any(results_dir.glob("*.png")),
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
    if last_event is not None and last_event.get("event") == "stage_end" and last_event.get("ok") is False:
        error = f"{last_event.get('error_type')}: {last_event.get('error_message')}"
        return {"status": "error", "current_stage": None, "error": error, "pending_clarifications": None}

    # A clarification pause survives a server restart: `_make_clarify` writes
    # the exact question set (and which stage raised it) here the moment it
    # starts waiting on a human, and removes it the moment it's answered
    # (live or via the recovery path in the answer endpoints below) -- so if
    # it's still here, this project is genuinely still waiting, no live
    # thread required to say so.
    pending_path = _pending_clarification_path(project_id)
    if pending_path.exists():
        try:
            pending = json.loads(pending_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pending = None
        if pending and pending.get("clarifications"):
            return {
                "status": "awaiting_input", "current_stage": pending.get("stage", "clarify"),
                "error": None, "pending_clarifications": pending["clarifications"],
            }

    meta = _read_meta(project_id)
    stage1_finished = (
        last_event is not None
        and last_event.get("event") == "stage_end"
        and str(last_event.get("name", "")).startswith("Stage 1:")
        and last_event.get("ok") is True
    )
    if (
        meta.get("extraction_status") == "completed"
        and _artifacts(project_id)["extraction"]
        and stage1_finished
    ):
        return {
            "status": "stage1_ready", "current_stage": None,
            "error": None, "pending_clarifications": None,
        }

    artifacts = _artifacts(project_id)
    if artifacts["merged_understanding"] or artifacts["sysml"] or artifacts["modelica"]:
        return {"status": "ready", "current_stage": None, "error": None, "pending_clarifications": None}

    if last_event is None:
        return {"status": "created", "current_stage": None, "error": None, "pending_clarifications": None}

    return {
        "status": "interrupted", "current_stage": None,
        "error": "The server restarted (or was stopped) while this project was running. Nothing on disk was "
                 "lost, but the run itself didn't survive -- click Re-run to start over.",
        "pending_clarifications": None,
    }


@app.get("/api/health")
def health():
    return {"ok": True, "application": "hackathon-simulation-pipeline"}


def _extract_zip_documents(data: bytes, docs_dir: Path) -> int:
    """Unzip an uploaded archive's member files straight into a project's
    documents directory, flattened (no subfolders) so every member lands
    next to a plain uploaded file the same way. Returns how many files were
    written.

    Flattening also closes zip-slip: a member's own path (`../../etc/passwd`)
    is discarded entirely in favour of just its final path segment, so a
    crafted archive can never write outside `docs_dir`. Directory entries and
    macOS's own `__MACOSX/`/`.DS_Store` junk are skipped; anything else is
    written regardless of extension -- the same as a plain (non-zip) upload,
    which is unfiltered too, so `sources.read_source` remains the one place
    that rejects an unsupported format, at ingestion time.
    """
    written = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            member_name = Path(info.filename).name
            if not member_name or member_name == ".DS_Store" or "__MACOSX" in info.filename:
                continue
            (docs_dir / member_name).write_bytes(archive.read(info))
            written += 1
    return written


@app.post("/api/projects")
async def create_project(name: str = Form(...), stage1_backend: str = Form("ollama"), files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "attach at least one document")
    if stage1_backend not in {"ollama", "openai"}:
        raise HTTPException(400, "stage1_backend must be ollama or openai")
    project_id = _slugify(name)
    docs_dir = _ws.documents_dir(project_id)
    docs_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        filename = Path(f.filename or "document").name
        data = await f.read()
        if filename.lower().endswith(".zip"):
            try:
                _extract_zip_documents(data, docs_dir)
            except zipfile.BadZipFile:
                raise HTTPException(400, f"'{filename}' is not a valid zip archive")
        else:
            (docs_dir / filename).write_bytes(data)
    if not any(docs_dir.iterdir()):
        raise HTTPException(400, "no documents found -- the attached zip archive(s) were empty")
    _ws.ensure_layout(project_id)
    _meta_path(project_id).write_text(json.dumps({"name": name, "stage1_backend": stage1_backend}), encoding="utf-8")
    return {"project_id": project_id, "name": name}


def _project_domain(project_id: str) -> str | None:
    path = _ws.extracted_dir(project_id) / "merged_understanding.json"
    if not path.exists():
        return None
    try:
        domains = json.loads(path.read_text(encoding="utf-8")).get("domains") or []
    except Exception:
        return None
    return domains[0].replace("_", " ").title() if domains else None


def _project_document_count(project_id: str) -> int:
    docs_dir = _ws.documents_dir(project_id)
    if not docs_dir.exists():
        return 0
    # Uploaded documents can land inside a nested folder (e.g. an extracted
    # dataset archive), not only directly under documents_dir, so count
    # recursively rather than just the top level.
    return sum(1 for p in docs_dir.rglob("*") if p.is_file())


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
        # Newest file anywhere under the project (the run log if the pipeline
        # has run, meta.json otherwise) stands in for "last updated" -- there
        # is no explicit timestamp field on a project.
        newest_mtime = max((p.stat().st_mtime for p in d.rglob("*") if p.is_file()), default=d.stat().st_mtime)
        out.append({
            "project_id": d.name, "name": name, "status": effective["status"],
            "current_stage": effective["current_stage"],
            "updated_at": datetime.fromtimestamp(newest_mtime, tz=timezone.utc).isoformat(),
            "domain": _project_domain(d.name),
            "document_count": _project_document_count(d.name),
        })
    return out


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    root = _ws.project_dir(project_id)
    if not root.exists():
        raise HTTPException(404, "project not found")
    effective = _effective_status(project_id)
    meta = _read_meta(project_id)
    return {
        "project_id": project_id,
        "name": meta.get("name", project_id),
        "stage1_backend": meta.get("stage1_backend", "ollama"),
        "status": effective["status"],
        "current_stage": effective["current_stage"],
        "error": effective["error"],
        "pending_clarifications": effective["pending_clarifications"],
        "artifacts": _artifacts(project_id),
    }


class RunBody(BaseModel):
    stage1_backend: Literal["ollama", "openai"] | None = None


class StageRunBody(BaseModel):
    stage1_backend: Literal["ollama", "openai"] | None = None


@app.post("/api/projects/{project_id}/run")
def run_project(project_id: str, body: RunBody | None = None):
    if not _ws.project_dir(project_id).exists():
        raise HTTPException(404, "project not found")
    state = _state(project_id)
    if state.status in ("running", "awaiting_input"):
        raise HTTPException(409, "already running")
    if body is not None and body.stage1_backend is not None:
        meta = _read_meta(project_id)
        meta["stage1_backend"] = body.stage1_backend
        _write_meta(project_id, meta)
    state.status = "running"
    state.current_stage = None
    state.error = None
    threading.Thread(target=_run_pipeline, args=(project_id,), daemon=True).start()
    return {"status": "started"}


def _require_stage_input(project_id: str, stage: str) -> None:
    artifacts = _artifacts(project_id)
    if stage == "stage_1":
        if not any(_ws.documents_dir(project_id).rglob("*")):
            raise HTTPException(400, "Stage 1 requires source documents")
    elif stage == "merge" and not artifacts["extraction"]:
        raise HTTPException(400, "Merge requires completed Stage 1 extraction")
    elif stage == "clarify" and not artifacts["merged_understanding"]:
        raise HTTPException(400, "Clarify requires a merged understanding")
    elif stage == "stage_2" and not artifacts["merged_understanding"]:
        raise HTTPException(400, "SysML generation requires a merged understanding")
    elif stage == "stage_2" and not artifacts["clarified"]:
        raise HTTPException(400, "SysML generation requires completed Clarify")
    elif stage == "stage_3" and not artifacts["sysml"]:
        raise HTTPException(400, "Modelica generation requires SysML output")


def _remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _clear_modelica_active_outputs(project_root: Path) -> None:
    """Remove only the active Modelica result, preserving archived drafts."""
    generated = project_root / "modelica" / "generated"
    if generated.exists():
        for path in generated.glob("*.mo"):
            path.unlink()
        manifest = generated / "modelica_manifest.json"
        if manifest.exists():
            manifest.unlink()
        results = project_root / "modelica" / "results"
        if results.exists():
            shutil.rmtree(results)

def _prepare_stage_rerun(project_id: str, stage: str) -> None:
    from simulation_platform.reasoner_pipeline import _stage2_human_notes_path

    extracted = _ws.extracted_dir(project_id)
    project_root = _ws.project_dir(project_id)
    if stage == "stage_1":
        _remove(extracted / "understanding")
        _remove(extracted / "merged_understanding.json")
        _remove(extracted / "merged_understanding.md")
        _remove(extracted / "clarified_answers.json")
        _remove(_pending_clarification_path(project_id))
        _remove(_stage2_human_notes_path(_ws, project_id))
        _remove(extracted / "system_flow.mmd")
        _remove(project_root / "sysml")
        _clear_modelica_active_outputs(project_root)
        _remove(project_root / "validation")
    elif stage == "merge":
        _remove(extracted / "merged_understanding.json")
        _remove(extracted / "merged_understanding.md")
        _remove(extracted / "clarified_answers.json")
        _remove(_pending_clarification_path(project_id))
        _remove(_stage2_human_notes_path(_ws, project_id))
        _remove(extracted / "system_flow.mmd")
        _remove(project_root / "sysml")
        _clear_modelica_active_outputs(project_root)
        _remove(project_root / "validation")
    elif stage == "clarify":
        _remove(extracted / "clarified_answers.json")
        _remove(_pending_clarification_path(project_id))
        _remove(extracted / "system_flow.mmd")
        _remove(project_root / "sysml")
        _clear_modelica_active_outputs(project_root)
        _remove(project_root / "validation")
    elif stage == "stage_2":
        _remove(_pending_clarification_path(project_id))
        _remove(project_root / "sysml")
        _clear_modelica_active_outputs(project_root)
        _remove(project_root / "validation")
    elif stage == "stage_3":
        # "Build" now runs generation + validation together (see
        # execute_reasoner_stage_3_and_4), so a rerun clears both.
        _clear_modelica_active_outputs(project_root)
        _remove(project_root / "validation")


def _run_single_stage(project_id: str, stage: str, stage1_backend: str | None) -> None:
    state = _state(project_id)
    state.status = "running"
    state.current_stage = stage
    state.error = None
    try:
        _prepare_stage_rerun(project_id, stage)
        if stage == "stage_1":
            backend = stage1_backend or _read_meta(project_id).get("stage1_backend", "ollama")
            execute_reasoner_stage_1(project_id, projects_root=_ws.projects_root, stage1_backend=backend)
            meta = _read_meta(project_id)
            meta.update({"stage1_backend": backend, "extraction_status": "completed", "status": "stage1_ready"})
            _write_meta(project_id, meta)
        elif stage == "merge":
            execute_merge(project_id, projects_root=_ws.projects_root)
        elif stage == "clarify":
            execute_clarify(
                project_id, projects_root=_ws.projects_root,
                clarify=_make_clarify(project_id, "clarify"),
            )
        elif stage == "stage_2":
            execute_reasoner_stage_2(
                project_id, projects_root=_ws.projects_root, clarify=_make_clarify(project_id, "stage_2"),
            )
        elif stage == "stage_3":
            # "Build" runs generation + validation together, with the
            # behavioral repair loop between them -- see
            # execute_reasoner_stage_3_and_4's own docstring.
            execute_reasoner_stage_3_and_4(project_id, projects_root=_ws.projects_root)
        state.status = "created"
        state.current_stage = None
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        state.status = "error"
        state.error = f"{type(exc).__name__}: {exc}"


@app.post("/api/projects/{project_id}/stages/{stage}/run")
def run_stage(project_id: str, stage: str, body: StageRunBody | None = None):
    if not _ws.project_dir(project_id).exists():
        raise HTTPException(404, "project not found")
    if stage not in {"stage_1", "merge", "clarify", "stage_2", "stage_3"}:
        raise HTTPException(404, "unknown pipeline stage")
    state = _state(project_id)
    if state.status in ("running", "awaiting_input"):
        raise HTTPException(409, "another stage is already running")
    _require_stage_input(project_id, stage)
    backend = body.stage1_backend if body is not None else None
    state.status = "running"
    state.current_stage = stage
    state.error = None
    threading.Thread(target=_run_single_stage, args=(project_id, stage, backend), daemon=True).start()
    return {"status": "started", "stage": stage}


class AnswerBody(BaseModel):
    answers: dict[str, str]


@app.post("/api/projects/{project_id}/clarifications/answer")
def answer_clarifications(project_id: str, body: AnswerBody):
    state = _state(project_id)
    if state.status == "awaiting_input" and state.event is not None:
        state.answers = body.answers
        state.event.set()
        return {"status": "ok"}
    # No live thread (e.g. the server restarted while this project was
    # waiting) -- the question set and which stage raised it survive on
    # disk, so the answer can still be recorded. See `_make_clarify`.
    pending_path = _pending_clarification_path(project_id)
    if pending_path.exists():
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
        _record_clarify_answers_from_disk(
            project_id, pending.get("stage", "clarify"), pending.get("clarifications", []), body.answers,
        )
        return {"status": "ok"}
    raise HTTPException(409, "no pending clarification for this project")


@app.post("/api/projects/{project_id}/clarifications/use-defaults")
def use_default_clarifications(project_id: str):
    state = _state(project_id)
    live = state.status == "awaiting_input" and state.event is not None
    pending_path = _pending_clarification_path(project_id)
    stage = "clarify"
    if live:
        clarifications = state.pending_clarifications or []
    elif pending_path.exists():
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
        stage = pending.get("stage", "clarify")
        clarifications = pending.get("clarifications", [])
    else:
        raise HTTPException(409, "no pending clarification for this project")
    if any(not str(c.get("suggested_value", "")).strip() for c in clarifications):
        raise HTTPException(409, "this clarification stage requires explicit answers")
    answers = {c["id"]: c["suggested_value"] for c in clarifications}
    if live:
        state.answers = answers
        state.event.set()
    else:
        _record_clarify_answers_from_disk(project_id, stage, clarifications, answers)
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
            if effective["status"] in ("stage1_ready", "ready", "done", "error", "interrupted") and pos >= current_size:
                break
            time.sleep(0.5)

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/api/projects/{project_id}/artifacts/understanding")
def get_understanding(project_id: str):
    path = _ws.extracted_dir(project_id) / "merged_understanding.md"
    if path.exists():
        return {"content": path.read_text(encoding="utf-8")}
    notes_dir = _ws.extracted_dir(project_id) / "understanding"
    notes = sorted(notes_dir.glob("*.txt")) if notes_dir.exists() else []
    if not notes:
        raise HTTPException(404, "not generated yet")
    content = "\n\n".join(
        f"--- {note.name} ---\n{note.read_text(encoding='utf-8')}" for note in notes
    )
    return {"content": content}


@app.get("/api/projects/{project_id}/artifacts/sysml")
def get_sysml(project_id: str):
    gen_dir = _ws.sysml_dir(project_id) / "generated"
    files = sorted(gen_dir.glob("*.sysml")) if gen_dir.exists() else []
    if not files:
        raise HTTPException(404, "not generated yet")
    return {"filename": files[0].name, "content": files[0].read_text(encoding="utf-8")}


@app.get("/api/projects/{project_id}/artifacts/diagram")
def get_diagram(project_id: str):
    path = _ws.extracted_dir(project_id) / "system_flow.mmd"
    if not path.exists():
        raise HTTPException(404, "not generated yet")
    return {"filename": path.name, "content": path.read_text(encoding="utf-8")}


@app.get("/api/projects/{project_id}/artifacts/clarified")
def get_clarifications(project_id: str):
    """Every question Confirm raised and what was answered -- see
    `reasoner_pipeline._answers_record` for how `decisions` is built."""

    path = _ws.extracted_dir(project_id) / "clarified_answers.json"
    if not path.exists():
        raise HTTPException(404, "not generated yet")
    record = json.loads(path.read_text(encoding="utf-8"))
    return {"filename": path.name, "decisions": record.get("decisions", [])}


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
    Simulation plots are exposed separately by the result artifact."""

    val_dir = _ws.validation_dir(project_id)
    reports = sorted(val_dir.glob("*.report.json")) if val_dir.exists() else []
    if not reports:
        raise HTTPException(404, "not generated yet")
    report = json.loads(reports[-1].read_text(encoding="utf-8"))
    return {"filename": reports[-1].name, "report": report}


@app.get("/api/projects/{project_id}/artifacts/result")
def get_result(project_id: str):
    results_dir = _ws.modelica_dir(project_id) / "results"
    plots = sorted(p.name for p in results_dir.glob("*.png")) if results_dir.exists() else []
    if not plots:
        raise HTTPException(404, "no result graphs generated yet")
    return {
        "filename": f"{len(plots)} individual result graphs",
        "plots": [
            {
                "filename": filename,
                "label": re.sub(r"^.*?\.trajectory\.\d+\.", "", Path(filename).stem).replace("_", " "),
            }
            for filename in plots
        ],
    }


@app.get("/api/projects/{project_id}/artifacts/result/plot/{filename}")
def get_result_plot(project_id: str, filename: str):
    from fastapi.responses import FileResponse

    results_dir = _ws.modelica_dir(project_id) / "results"
    path = results_dir / Path(filename).name  # `.name` strips any path components -- no directory traversal
    if not path.exists() or path.suffix.lower() != ".png":
        raise HTTPException(404, "plot not found")
    return FileResponse(path, media_type="image/png")


# --- Project file browser -------------------------------------------------
# The generated project folder is the reviewable record of a run: the source
# documents, the per-document notes, the merged brief, the SysML, the Modelica
# bundle with every archived repair attempt, the result CSV and the plots.
# These endpoints expose that tree read-only so a reviewer can inspect and
# download it from the UI instead of going to the filesystem.

# Anything larger than this is streamed as a download only, never inlined into
# a JSON preview -- a result CSV can be hundreds of thousands of rows.
_PREVIEW_MAX_BYTES = 256 * 1024
_TEXT_SUFFIXES = {
    ".txt", ".md", ".json", ".jsonl", ".mo", ".mos", ".sysml", ".mmd", ".csv",
    ".puml", ".eml", ".py", ".yaml", ".yml", ".xml", ".log", ".cfg", ".ini",
}


def _project_root(project_id: str) -> Path:
    root = _ws.project_dir(project_id)
    if not root.exists():
        raise HTTPException(404, "project not found")
    return root.resolve()


def _safe_member(project_id: str, relative_path: str) -> Path:
    """Resolve `relative_path` inside the project folder, or refuse.

    Resolving BOTH sides and checking containment is what makes this safe:
    a relative path can escape with `..`, an absolute path can point anywhere,
    and on Windows a symlink or a drive-qualified path can do the same. The
    check is on the resolved result, so none of those get through.
    """

    root = _project_root(project_id)
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise HTTPException(400, "path escapes the project folder")
    if not candidate.exists():
        raise HTTPException(404, "file not found")
    return candidate


def _describe(path: Path, root: Path) -> dict:
    stat = path.stat()
    return {
        "name": path.name,
        "path": path.relative_to(root).as_posix(),
        "type": "dir" if path.is_dir() else "file",
        "size": None if path.is_dir() else stat.st_size,
        "modified": stat.st_mtime,
        "previewable": path.is_file()
        and path.suffix.lower() in _TEXT_SUFFIXES
        and stat.st_size <= _PREVIEW_MAX_BYTES,
    }


@app.get("/api/projects/{project_id}/files")
def list_project_files(project_id: str, path: str = ""):
    """One directory level, folders first. `path` is relative to the project."""

    root = _project_root(project_id)
    target = _safe_member(project_id, path) if path else root
    if not target.is_dir():
        raise HTTPException(400, "not a directory")
    entries = [_describe(child, root) for child in target.iterdir()]
    entries.sort(key=lambda e: (e["type"] != "dir", e["name"].lower()))
    return {
        "project_id": project_id,
        "path": target.relative_to(root).as_posix() if target != root else "",
        "entries": entries,
    }


@app.get("/api/projects/{project_id}/files/preview")
def preview_project_file(project_id: str, path: str):
    """Inline text for the viewer. Binary and oversized files are download-only."""

    target = _safe_member(project_id, path)
    if not target.is_file():
        raise HTTPException(400, "not a file")
    size = target.stat().st_size
    if target.suffix.lower() not in _TEXT_SUFFIXES:
        raise HTTPException(415, "binary file -- download it instead")
    if size > _PREVIEW_MAX_BYTES:
        raise HTTPException(413, f"file is {size} bytes -- too large to preview, download it instead")
    return {
        "path": target.relative_to(_project_root(project_id)).as_posix(),
        "name": target.name,
        "size": size,
        "content": target.read_text(encoding="utf-8", errors="replace"),
    }


@app.get("/api/projects/{project_id}/files/download")
def download_project_file(project_id: str, path: str):
    from fastapi.responses import FileResponse

    target = _safe_member(project_id, path)
    if not target.is_file():
        raise HTTPException(400, "not a file")
    return FileResponse(target, filename=target.name, media_type="application/octet-stream")


@app.get("/api/projects/{project_id}/files/archive")
def download_project_archive(project_id: str, path: str = ""):
    """Zip the project folder, or one subfolder of it, and stream it back.

    Built in memory rather than written beside the project, so a download never
    leaves a stray artifact inside the folder it is archiving.
    """

    root = _project_root(project_id)
    target = _safe_member(project_id, path) if path else root
    if not target.is_dir():
        raise HTTPException(400, "not a directory")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(target.rglob("*")):
            if item.is_file():
                archive.write(item, item.relative_to(target).as_posix())
    buffer.seek(0)
    label = target.name if target != root else project_id
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{label}.zip"'},
    )
