"""Persistence for one project's SysML generation. Mirrors `SysML V2 Agent.md`, Section 26.

    projects/<id>/sysml/
    ├── input/generation_contract.json
    ├── plan/generation_plan.json
    ├── generated/*.sysml
    ├── traceability/sysml_traceability.json
    ├── validation/sysml_validation_report.json
    └── versions/<version>/version_metadata.json, current.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from simulation_platform.schemas import (
    SysMLElementMapping,
    SysMLGenerationContract,
    SysMLGenerationPlan,
    SysMLManifest,
    SysMLTraceability,
    SysMLValidationResult,
)


def sysml_dir(project_dir: Path) -> Path:
    return project_dir / "sysml"


def save_contract(project_dir: Path, contract: SysMLGenerationContract) -> None:
    path = sysml_dir(project_dir) / "input" / "generation_contract.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contract.model_dump_json(indent=2), encoding="utf-8")


def load_contract(project_dir: Path) -> SysMLGenerationContract:
    path = sysml_dir(project_dir) / "input" / "generation_contract.json"
    return SysMLGenerationContract.model_validate_json(path.read_text(encoding="utf-8"))


def save_plan(project_dir: Path, plan: SysMLGenerationPlan) -> None:
    path = sysml_dir(project_dir) / "plan" / "generation_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")


def load_plan(project_dir: Path) -> SysMLGenerationPlan:
    path = sysml_dir(project_dir) / "plan" / "generation_plan.json"
    return SysMLGenerationPlan.model_validate_json(path.read_text(encoding="utf-8"))


def save_mappings(project_dir: Path, mappings: list[SysMLElementMapping]) -> None:
    path = sysml_dir(project_dir) / "plan" / "element_mappings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([m.model_dump() for m in mappings], indent=2), encoding="utf-8")


def load_mappings(project_dir: Path) -> list[SysMLElementMapping]:
    path = sysml_dir(project_dir) / "plan" / "element_mappings.json"
    if not path.exists():
        return []
    return [SysMLElementMapping.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]


def save_generated_files(project_dir: Path, files: dict[str, str]) -> None:
    generated_dir = sysml_dir(project_dir) / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in files.items():
        (generated_dir / filename).write_text(text, encoding="utf-8")


def load_generated_files(project_dir: Path) -> dict[str, str]:
    generated_dir = sysml_dir(project_dir) / "generated"
    if not generated_dir.exists():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(generated_dir.glob("*.sysml"))}


def save_traceability(project_dir: Path, traceability: SysMLTraceability) -> None:
    path = sysml_dir(project_dir) / "traceability" / "sysml_traceability.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(traceability.model_dump_json(indent=2), encoding="utf-8")


def save_validation_report(project_dir: Path, result: SysMLValidationResult) -> None:
    path = sysml_dir(project_dir) / "validation" / "sysml_validation_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def load_validation_report(project_dir: Path) -> SysMLValidationResult:
    path = sysml_dir(project_dir) / "validation" / "sysml_validation_report.json"
    return SysMLValidationResult.model_validate_json(path.read_text(encoding="utf-8"))


def save_manifest(project_dir: Path, manifest: SysMLManifest) -> None:
    path = sysml_dir(project_dir) / "generated" / "sysml_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def publish_version(project_dir: Path, version: str, parent: str | None) -> None:
    versions_dir = sysml_dir(project_dir) / "versions"
    version_dir = versions_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)
    metadata = {"sysml_version": version, "created_at": datetime.now(timezone.utc).isoformat(), "parent": parent}
    (version_dir / "version_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (versions_dir / "current.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
