"""ONE shared project workspace layout for the whole platform, used by all
three pipeline stages -- replaces three independently-invented per-stage
project roots. See ARCHITECTURE_REDESIGN_PLAN.md §5-7.

```
projects/<project_id>/
├── problem.md                  # optional -- a stated problem statement
├── documents/                  # raw input files
├── state.json                  # per-stage status + input hash, for resumability
├── sysml/                      # Stage 2 output (owned by sysml_gen/storage/sysml_store.py)
├── modelica/                   # Stage 3 output (owned by modelica_gen/storage/modelica_store.py)
└── workspace/
    ├── extracted/               # Stage 1 output (project_knowledge.json, indexes, evidence, uncertainty)
    └── system_model.json        # cross-stage resolved system model (see shared/system_model_builder.py)
```

This module owns only the *shared* top-level layout and the one path all
three stages get pointed at (`Workspace.project_dir`) -- each stage's own
existing storage module still owns the exact file names/subfolders it
writes inside that one project directory (e.g.
`workspace/extracted/project_knowledge.json` is written by
`extraction/storage/artifacts.py`, `sysml/...` by `sysml_store.py`,
`modelica/...` by `modelica_store.py`, not here) -- this avoids duplicating
logic that's already tested per new direction.txt §36 ("reuse working
components"). The "one shared project workspace" requirement (§5) is met
by `pipeline.py` resolving all three stages to the SAME `project_dir` for
one `project_id`, not by renaming any stage's existing subfolder.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel


def compute_hash(*paths: Path) -> str:
    """A deterministic fingerprint of every file under the given paths
    (files or directories) -- content-based, not mtime-based, so touching a
    file without changing it doesn't count as a change. Used for §31 stale-
    artifact detection: a stage's own recorded `input_hash` (in
    `state.json`) is compared against this, computed fresh, before deciding
    whether to skip a rerun."""

    digest = hashlib.sha256()
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file())
    for file_path in sorted(files):
        digest.update(str(file_path).encode("utf-8"))
        try:
            digest.update(file_path.read_bytes())
        except OSError:
            continue
    return digest.hexdigest()


class StageState(BaseModel):
    # not_started | in_progress | completed | failed -- "in_progress" is
    # written right before a stage's graph is invoked and overwritten right
    # after (by "completed"/"failed"); if the process crashes or is killed
    # mid-graph (e.g. a BudgetGuard cutoff), "in_progress" is the LAST thing
    # on disk, and a later call for the SAME input_hash resumes from the
    # graph's own persisted checkpoint instead of restarting from scratch
    # (see `pipeline.py`'s `_execute_graph_stage`).
    status: str = "not_started"
    input_hash: str | None = None
    completed_at: str | None = None


class ProjectState(BaseModel):
    project_id: str
    stage_1: StageState = StageState()
    stage_2: StageState = StageState()
    stage_3: StageState = StageState()


class Workspace:
    """Owns the shared, top-level layout for one project. Each stage's own
    storage module resolves its own file paths underneath the directories
    this class creates."""

    def __init__(self, projects_root: Path):
        self.projects_root = projects_root

    def project_dir(self, project_id: str) -> Path:
        return self.projects_root / project_id

    def documents_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "documents"

    def problem_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "problem.md"

    def extracted_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "workspace" / "extracted"

    def sysml_dir(self, project_id: str) -> Path:
        # Matches `sysml_gen/storage/sysml_store.py`'s own `sysml_dir()` --
        # not duplicated logic, just the same one-line convention so the
        # CLI/pipeline can point at it without importing that stage's
        # storage module for a single path.
        return self.project_dir(project_id) / "sysml"

    def modelica_dir(self, project_id: str) -> Path:
        # Matches `modelica_gen/storage/modelica_store.py`'s own `modelica_dir()`.
        return self.project_dir(project_id) / "modelica"

    def system_model_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "workspace" / "system_model.json"

    def checkpoint_db_path(self, project_id: str) -> Path:
        """One SQLite-backed LangGraph checkpoint database per project,
        shared across all three stages (each stage's own graph runs use a
        distinct `thread_id`, so they never collide in the same file) --
        see `pipeline.py`'s `_execute_graph_stage` for why this needs to be
        a real, cross-process-persistent file rather than the in-memory
        checkpointer LangGraph defaults to."""

        return self.project_dir(project_id) / "checkpoints.sqlite"

    def ensure_layout(self, project_id: str) -> None:
        for sub in (self.documents_dir(project_id), self.extracted_dir(project_id)):
            sub.mkdir(parents=True, exist_ok=True)

    # -- resumability state --------------------------------------------------

    def state_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "state.json"

    def load_state(self, project_id: str) -> ProjectState:
        path = self.state_path(project_id)
        if not path.exists():
            return ProjectState(project_id=project_id)
        return ProjectState.model_validate_json(path.read_text(encoding="utf-8"))

    def save_state(self, state: ProjectState) -> None:
        path = self.state_path(state.project_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")

    def mark_stage(self, project_id: str, stage: str, status: str, input_hash: str | None = None) -> ProjectState:
        """`stage` is one of "stage_1"/"stage_2"/"stage_3". Records status and,
        on success, a completion timestamp -- read by the CLI's `status`
        command and by each stage's own skip-if-unchanged check."""

        state = self.load_state(project_id)
        stage_state = StageState(
            status=status,
            input_hash=input_hash,
            completed_at=datetime.now(timezone.utc).isoformat() if status == "completed" else None,
        )
        setattr(state, stage, stage_state)
        self.save_state(state)
        return state
