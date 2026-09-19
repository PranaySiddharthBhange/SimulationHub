"""Persistence for `source_manifest.json`. Mirrors `Document Agent.md`, Section 7."""

from __future__ import annotations

from pathlib import Path

from simulation_platform.schemas import SourceManifest


def manifest_path(project_dir: Path) -> Path:
    return project_dir / "source_manifest.json"


def save_source_manifest(project_dir: Path, manifest: SourceManifest) -> None:
    manifest_path(project_dir).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def load_source_manifest(project_dir: Path) -> SourceManifest:
    return SourceManifest.model_validate_json(manifest_path(project_dir).read_text(encoding="utf-8"))
