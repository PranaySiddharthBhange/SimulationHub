"""Persistence for one project's Modelica generation. Mirrors
`Modelica Agent.md`, Section 32:

    projects/<id>/modelica/
    ├── input/modelica_generation_contract.json
    ├── analysis/legacy_comparison.json
    ├── plan/modelica_generation_plan.json, modelica_mappings.json
    ├── generated/*.mo, package.mo, package.order, modelica_manifest.json
    ├── traceability/modelica_traceability.json
    ├── validation/modelica_validation_report.json
    └── versions/<version>/version_metadata.json, current.json

One combined validation report file, not five separate per-layer files --
same consolidation already made in the SysML Agent's `validator.py`
(one orchestrator, one `ModelicaValidationResult` covering every layer).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from simulation_platform.schemas import (
    CompileResult,
    LegacyComparison,
    ModelicaGenerationContract,
    ModelicaGenerationPlan,
    ModelicaManifest,
    ModelicaMapping,
    ModelicaTraceability,
    ModelicaValidationResult,
    StateMachine,
)


def modelica_dir(project_dir: Path) -> Path:
    return project_dir / "modelica"


def save_contract(project_dir: Path, contract: ModelicaGenerationContract) -> None:
    path = modelica_dir(project_dir) / "input" / "modelica_generation_contract.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contract.model_dump_json(indent=2), encoding="utf-8")


def load_contract(project_dir: Path) -> ModelicaGenerationContract:
    path = modelica_dir(project_dir) / "input" / "modelica_generation_contract.json"
    return ModelicaGenerationContract.model_validate_json(path.read_text(encoding="utf-8"))


def save_legacy_comparisons(project_dir: Path, comparisons: list[LegacyComparison]) -> None:
    path = modelica_dir(project_dir) / "analysis" / "legacy_comparison.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([c.model_dump() for c in comparisons], indent=2), encoding="utf-8")


def load_legacy_comparisons(project_dir: Path) -> list[LegacyComparison]:
    path = modelica_dir(project_dir) / "analysis" / "legacy_comparison.json"
    if not path.exists():
        return []
    return [LegacyComparison.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]


def save_plan(project_dir: Path, plan: ModelicaGenerationPlan) -> None:
    path = modelica_dir(project_dir) / "plan" / "modelica_generation_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")


def load_plan(project_dir: Path) -> ModelicaGenerationPlan:
    path = modelica_dir(project_dir) / "plan" / "modelica_generation_plan.json"
    return ModelicaGenerationPlan.model_validate_json(path.read_text(encoding="utf-8"))


def save_mappings(project_dir: Path, mappings: list[ModelicaMapping]) -> None:
    path = modelica_dir(project_dir) / "plan" / "modelica_mappings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([m.model_dump() for m in mappings], indent=2), encoding="utf-8")


def load_mappings(project_dir: Path) -> list[ModelicaMapping]:
    path = modelica_dir(project_dir) / "plan" / "modelica_mappings.json"
    if not path.exists():
        return []
    return [ModelicaMapping.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]


def save_state_machines(project_dir: Path, state_machines: list[StateMachine]) -> None:
    path = modelica_dir(project_dir) / "plan" / "state_machines.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([sm.model_dump() for sm in state_machines], indent=2), encoding="utf-8")


def load_state_machines(project_dir: Path) -> list[dict]:
    """Returns plain dicts, not re-validated `StateMachine` objects --
    `generation/modelica_generator.py` only ever reads them with `.get(...)`
    (the same convention already used for `behaviors_by_id`/
    `requirements_by_id`, sourced from `sysml_contract_raw`), so there's no
    second consumer needing the Pydantic round-trip."""

    path = modelica_dir(project_dir) / "plan" / "state_machines.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_generated_files(project_dir: Path, files: dict[str, str]) -> None:
    generated_dir = modelica_dir(project_dir) / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    # Clear stale output from a previous run first -- found live (see
    # DECISIONS.md): this only ever wrote/overwrote the current run's
    # files, so a class the mapper stopped generating (e.g. renamed, or no
    # longer needed) left its old .mo file behind indefinitely. A real
    # compile check doesn't care about `generated/`'s history, only its
    # current, exact contents, so this directory is a mirror of the latest
    # run, not an accumulation -- immutable *versioned* snapshots already
    # live separately, under `versions/`.
    for stale in list(generated_dir.glob("*.mo")) + list(generated_dir.glob("package.order")):
        if stale.name not in files:
            stale.unlink()

    for filename, text in files.items():
        (generated_dir / filename).write_text(text, encoding="utf-8")


def load_generated_files(project_dir: Path) -> dict[str, str]:
    generated_dir = modelica_dir(project_dir) / "generated"
    if not generated_dir.exists():
        return {}
    files: dict[str, str] = {}
    for pattern in ("*.mo", "package.order"):
        files.update({p.name: p.read_text(encoding="utf-8") for p in sorted(generated_dir.glob(pattern))})
    return files


def save_command_overrides(project_dir: Path, overrides: dict[str, str]) -> None:
    """Human-confirmed answers for a never-assigned legacy variable that a
    scheduled command proposed a real value for (see `generation/
    modelica_generator.py`'s propose-then-confirm protocol) -- persisted so
    a later regeneration doesn't re-ask about something already confirmed."""

    path = modelica_dir(project_dir) / "generated" / "command_overrides.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(overrides, indent=2), encoding="utf-8")


def load_command_overrides(project_dir: Path) -> dict[str, str]:
    path = modelica_dir(project_dir) / "generated" / "command_overrides.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(project_dir: Path, manifest: ModelicaManifest) -> None:
    path = modelica_dir(project_dir) / "generated" / "modelica_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def load_manifest(project_dir: Path) -> ModelicaManifest:
    path = modelica_dir(project_dir) / "generated" / "modelica_manifest.json"
    return ModelicaManifest.model_validate_json(path.read_text(encoding="utf-8"))


def save_traceability(project_dir: Path, traceability: ModelicaTraceability) -> None:
    path = modelica_dir(project_dir) / "traceability" / "modelica_traceability.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(traceability.model_dump_json(indent=2), encoding="utf-8")


def save_validation_report(project_dir: Path, result: ModelicaValidationResult) -> None:
    path = modelica_dir(project_dir) / "validation" / "modelica_validation_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def load_validation_report(project_dir: Path) -> ModelicaValidationResult:
    path = modelica_dir(project_dir) / "validation" / "modelica_validation_report.json"
    return ModelicaValidationResult.model_validate_json(path.read_text(encoding="utf-8"))


def save_compile_result(project_dir: Path, result: CompileResult) -> None:
    # This agent stands in for the not-yet-built, standalone Compiler Agent
    # (see `compiler/openmodelica_client.py`) -- saved under this project's
    # own modelica/ tree, not under the separate `compiler/` folder that
    # eventual real agent would own (`Modelica Agent.md`, Section 32).
    path = modelica_dir(project_dir) / "compile" / "compile_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def load_compile_result(project_dir: Path) -> CompileResult | None:
    path = modelica_dir(project_dir) / "compile" / "compile_result.json"
    if not path.exists():
        return None
    return CompileResult.model_validate_json(path.read_text(encoding="utf-8"))


def save_result_validation_report(project_dir: Path, report: dict) -> None:
    """`report` is `shared/result_validation.py::evaluate_simulation_result`'s
    own plain dict -- not a dedicated Pydantic schema, since it's a small,
    self-describing structure (status/checked/unmatched/issues) with no
    other consumer needing a typed contract for it yet."""

    path = modelica_dir(project_dir) / "compile" / "result_validation_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def load_result_validation_report(project_dir: Path) -> dict | None:
    path = modelica_dir(project_dir) / "compile" / "result_validation_report.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def publish_version(project_dir: Path, version: str, parent: str | None) -> None:
    versions_dir = modelica_dir(project_dir) / "versions"
    version_dir = versions_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)
    metadata = {"modelica_version": version, "created_at": datetime.now(timezone.utc).isoformat(), "parent": parent}
    (version_dir / "version_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (versions_dir / "current.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
