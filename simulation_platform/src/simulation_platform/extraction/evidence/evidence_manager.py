"""Evidence persistence. Mirrors `Document Agent.md`, Section 41."""

from __future__ import annotations

import json
from pathlib import Path

from simulation_platform.schemas import Evidence


def evidence_path(project_dir: Path) -> Path:
    return project_dir / "workspace" / "extracted" / "evidence.json"


def save_evidence(project_dir: Path, evidence: list[Evidence]) -> None:
    path = evidence_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([ev.model_dump() for ev in evidence], indent=2, default=str), encoding="utf-8")


def load_evidence(project_dir: Path) -> list[Evidence]:
    path = evidence_path(project_dir)
    if not path.exists():
        return []
    return [Evidence.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]
