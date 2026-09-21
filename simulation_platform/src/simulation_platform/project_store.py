"""Project creation and the runtime project folder.

Simplified twice now, both times by checking empirically which subdirs the
live pipeline actually writes to. First pass dropped the original 15-dir
layout (`source/`, `normalized/{documents,tables,datasets,diagrams,code}`,
`observations/`, `index/`, `semantic/`, `evidence/`, `uncertainty/`,
`decisions/`) down to `documents/` + `workspace/`. Second pass (this one)
dropped `workspace/versions/` and `workspace/reports/` too -- created on
every project by the FIRST simplification, but never once written to by
`reasoner_pipeline.py`, the pipeline actually in use. What's real:
`documents/` (raw input), `workspace/extracted/` (Stage 1 understanding
files + consolidated understanding), and -- created lazily by Stage 2/3
themselves, not here -- `sysml/generated/` and `modelica/generated/`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from simulation_platform.schemas import ProjectManifest, ProjectStatus

_SUBDIRS = [
    "documents",
    "workspace/extracted",
]


class ProjectStore:
    """Owns the on-disk layout for a single project."""

    def __init__(self, projects_root: Path):
        self.projects_root = projects_root

    def project_dir(self, project_id: str) -> Path:
        return self.projects_root / project_id

    def create_project(self, project_id: str, name: str, source_dir: Path, copy_source: bool = True) -> ProjectManifest:
        project_dir = self.project_dir(project_id)
        for sub in _SUBDIRS:
            (project_dir / sub).mkdir(parents=True, exist_ok=True)

        documents_dir = project_dir / "documents"
        if copy_source:
            for item in source_dir.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(source_dir)
                    dest = documents_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if not dest.exists():
                        shutil.copy2(item, dest)

        manifest = ProjectManifest(
            project_id=project_id,
            name=name,
            source_root=str(source_dir),
            status=ProjectStatus.CREATED,
        )
        self.save_manifest(manifest)
        return manifest

    def manifest_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "project_manifest.json"

    def save_manifest(self, manifest: ProjectManifest) -> None:
        path = self.manifest_path(manifest.project_id)
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

    def load_manifest(self, project_id: str) -> ProjectManifest:
        path = self.manifest_path(project_id)
        return ProjectManifest.model_validate_json(path.read_text(encoding="utf-8"))

    def source_original_dir(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "documents"
