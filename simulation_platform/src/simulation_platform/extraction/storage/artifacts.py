"""Generic JSON artifact persistence for uncertainty/decisions/reports/versions.

`conflicts`/`ambiguities`/`unknowns`/`assumptions` were four separate files
under their own `uncertainty/` directory -- consolidated into one
`uncertainty.json` (four keys, one file) since none of them is ever large
enough on its own to need a separate file, and `new direction.txt` §6
explicitly asks to prefer a few meaningful artifacts over dozens of small
ones. `semantic_model.json` is renamed `project_knowledge.json`, matching
the vocabulary `new direction.txt` §7-8 uses for this exact artifact.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from simulation_platform.schemas import Ambiguity, Assumption, Conflict, Decision, SemanticModel, Unknown


def _dump(items: list[BaseModel]) -> list[dict]:
    return [item.model_dump() for item in items]


def _load(items: list[dict], model: type[BaseModel]) -> list:
    return [model.model_validate(item) for item in items]


def _uncertainty_path(project_dir: Path) -> Path:
    return project_dir / "workspace" / "extracted" / "uncertainty.json"


def _read_uncertainty(project_dir: Path) -> dict:
    path = _uncertainty_path(project_dir)
    if not path.exists():
        return {"conflicts": [], "ambiguities": [], "unknowns": [], "assumptions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_uncertainty(project_dir: Path, data: dict) -> None:
    path = _uncertainty_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def save_conflicts(project_dir: Path, conflicts: list[Conflict]) -> None:
    data = _read_uncertainty(project_dir)
    data["conflicts"] = _dump(conflicts)
    _write_uncertainty(project_dir, data)


def save_ambiguities(project_dir: Path, ambiguities: list[Ambiguity]) -> None:
    data = _read_uncertainty(project_dir)
    data["ambiguities"] = _dump(ambiguities)
    _write_uncertainty(project_dir, data)


def save_unknowns(project_dir: Path, unknowns: list[Unknown]) -> None:
    data = _read_uncertainty(project_dir)
    data["unknowns"] = _dump(unknowns)
    _write_uncertainty(project_dir, data)


def save_assumptions(project_dir: Path, assumptions: list[Assumption]) -> None:
    data = _read_uncertainty(project_dir)
    data["assumptions"] = _dump(assumptions)
    _write_uncertainty(project_dir, data)


def load_ambiguities(project_dir: Path) -> list[Ambiguity]:
    return _load(_read_uncertainty(project_dir).get("ambiguities", []), Ambiguity)


def save_decisions(project_dir: Path, decisions: list[Decision]) -> None:
    path = project_dir / "workspace" / "extracted" / "decisions.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_dump(decisions), indent=2, default=str), encoding="utf-8")


def load_decisions(project_dir: Path) -> list[Decision]:
    path = project_dir / "workspace" / "extracted" / "decisions.json"
    if not path.exists():
        return []
    return _load(json.loads(path.read_text(encoding="utf-8")), Decision)


def save_semantic_model(project_dir: Path, model: SemanticModel) -> None:
    path = project_dir / "workspace" / "extracted" / "project_knowledge.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_semantic_model(project_dir: Path) -> SemanticModel | None:
    path = project_dir / "workspace" / "extracted" / "project_knowledge.json"
    if not path.exists():
        return None
    return SemanticModel.model_validate_json(path.read_text(encoding="utf-8"))


def save_report(project_dir: Path, name: str, data: dict) -> None:
    path = project_dir / "workspace" / "reports" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def publish_version(project_dir: Path, version: str, reason: str, parent: str | None) -> None:
    versions_dir = project_dir / "workspace" / "versions"
    version_dir = versions_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "parent": parent,
        "reason": reason,
    }
    (version_dir / "version_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (versions_dir / "current.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
