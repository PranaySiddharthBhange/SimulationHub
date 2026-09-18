"""Generic JSON artifact persistence for uncertainty/decisions/reports/versions.

Mirrors `Document Agent.md`, Sections 34-39, 42, and 57.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from engineering_agent.schemas import Ambiguity, Assumption, Conflict, Decision, SemanticModel, Unknown


def _write_list(path: Path, items: list[BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([item.model_dump() for item in items], indent=2, default=str), encoding="utf-8")


def _read_list(path: Path, model: type[BaseModel]) -> list:
    if not path.exists():
        return []
    return [model.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]


def save_conflicts(project_dir: Path, conflicts: list[Conflict]) -> None:
    _write_list(project_dir / "uncertainty" / "conflicts.json", conflicts)


def save_ambiguities(project_dir: Path, ambiguities: list[Ambiguity]) -> None:
    _write_list(project_dir / "uncertainty" / "ambiguities.json", ambiguities)


def save_unknowns(project_dir: Path, unknowns: list[Unknown]) -> None:
    _write_list(project_dir / "uncertainty" / "unknowns.json", unknowns)


def save_assumptions(project_dir: Path, assumptions: list[Assumption]) -> None:
    _write_list(project_dir / "uncertainty" / "assumptions.json", assumptions)


def load_ambiguities(project_dir: Path) -> list[Ambiguity]:
    return _read_list(project_dir / "uncertainty" / "ambiguities.json", Ambiguity)


def save_decisions(project_dir: Path, decisions: list[Decision]) -> None:
    _write_list(project_dir / "decisions" / "user_decisions.json", decisions)


def load_decisions(project_dir: Path) -> list[Decision]:
    return _read_list(project_dir / "decisions" / "user_decisions.json", Decision)


def save_semantic_model(project_dir: Path, model: SemanticModel) -> None:
    path = project_dir / "semantic" / "semantic_model.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_semantic_model(project_dir: Path) -> SemanticModel | None:
    path = project_dir / "semantic" / "semantic_model.json"
    if not path.exists():
        return None
    return SemanticModel.model_validate_json(path.read_text(encoding="utf-8"))


def save_report(project_dir: Path, name: str, data: dict) -> None:
    path = project_dir / "reports" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def publish_version(project_dir: Path, version: str, reason: str, parent: str | None) -> None:
    versions_dir = project_dir / "versions"
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
