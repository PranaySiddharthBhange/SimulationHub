"""The on-disk project layout `reasoner_pipeline.py` reads/writes.

```
projects/<project_id>/
├── documents/                  # raw input files, copied in by ProjectStore
├── run.jsonl                   # structured, append-only run log (see utils/run_log.py)
├── workspace/extracted/        # Stage 1 output + merged understanding
├── sysml/generated/            # Stage 2 output
├── modelica/generated/         # Stage 3 ordered .mo bundle + modelica_manifest.json
├── modelica/results/           # Stage 4: real re-simulation CSV/summary/plots
└── validation/                 # Stage 4: the independent review report
```

Trimmed from an earlier, larger version that also tracked per-stage
resumability state (`state.json`, input-hash skip-if-unchanged) and a
LangGraph checkpoint database -- both belonged to the old structured,
graph-based pipeline this fork replaced; traced live usage and found
`reasoner_pipeline.py` never reads or writes either.
"""

from __future__ import annotations

from pathlib import Path


class Workspace:
    """Owns the shared, top-level layout for one project."""

    def __init__(self, projects_root: Path):
        self.projects_root = projects_root

    def project_dir(self, project_id: str) -> Path:
        return self.projects_root / project_id

    def documents_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "documents"

    def extracted_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "workspace" / "extracted"

    def sysml_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "sysml"

    def modelica_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "modelica"

    def validation_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "validation"

    def run_log_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "run.jsonl"

    def ensure_layout(self, project_id: str) -> None:
        for sub in (self.documents_dir(project_id), self.extracted_dir(project_id)):
            sub.mkdir(parents=True, exist_ok=True)
