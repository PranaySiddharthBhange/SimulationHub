"""Builds/updates the ONE central `ResolvedSystemModel` for a project --
see `schemas/resolved_system_model.py` and `new direction.txt` §7.

Deterministic aggregation only, no LLM call: each stage already produced
its own validated facts (extraction's `SemanticModel`, the SysML plan +
mappings); this just merges them into one cross-stage read-model instead
of leaving three independently-invented versions of the system lying
around in three separate files. Called after Stage 1 and again after
Stage 2 (and, when it exists, after Stage 3) -- always additive, never
dropping an earlier stage's contribution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from simulation_platform.schemas import (
    ResolvedSystemModel,
    SemanticModel,
    SysMLConstruct,
    SysMLElementMapping,
    SysMLGenerationPlan,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_system_model(path: Path, project_id: str) -> ResolvedSystemModel:
    if path.exists():
        return ResolvedSystemModel.model_validate_json(path.read_text(encoding="utf-8"))
    return ResolvedSystemModel(project_id=project_id, generated_at=_now())


def save_system_model(path: Path, model: ResolvedSystemModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def apply_stage1(path: Path, project_id: str, semantic_model: SemanticModel) -> ResolvedSystemModel:
    """Populates the entities/relationships/requirements/behaviors/
    constraints/assumptions/conflicts/unknowns from Stage 1's own already-
    validated `SemanticModel` -- these are the model's source of truth for
    "what the system is"; Stage 2/3 never re-derive their own copies."""

    model = load_system_model(path, project_id)
    model.generated_at = _now()
    model.knowledge_version = semantic_model.model_version
    model.entities = semantic_model.entities
    model.relationships = semantic_model.relationships
    model.requirements = semantic_model.requirements
    model.behaviors = semantic_model.behaviors
    model.constraints = semantic_model.constraints
    model.assumptions = semantic_model.assumptions
    model.conflicts = semantic_model.conflicts
    model.unknowns = semantic_model.unknowns
    save_system_model(path, model)
    return model


def apply_stage2(
    path: Path,
    project_id: str,
    sysml_version: str,
    plan: SysMLGenerationPlan,
    mappings: list[SysMLElementMapping],
) -> ResolvedSystemModel:
    """Adds the SysML-level structure -- which engineering elements became
    which SysML constructs, and which of those are states/control logic --
    without re-deriving or overwriting anything Stage 1 already resolved."""

    model = load_system_model(path, project_id)
    model.generated_at = _now()
    model.sysml_version = sysml_version
    model.sysml_elements = {m.engineering_id: m.sysml_element_name for m in mappings}
    model.states = sorted(
        {m.sysml_element_name for m in mappings if m.sysml_construct == SysMLConstruct.STATE_DEF}
    )
    model.control_logic = sorted(
        {m.sysml_element_name for m in mappings if m.sysml_construct == SysMLConstruct.ACTION_DEF}
    )
    model.system_boundary = plan.system_boundary
    model.physical_domains = plan.physical_domains
    model.sensors = plan.sensors
    model.actuators = plan.actuators
    model.open_questions = [q.model_dump() for q in plan.open_questions]
    save_system_model(path, model)
    return model


def apply_stage3(
    path: Path,
    project_id: str,
    modelica_version: str,
    compile_status: str | None,
    result_validation: dict | None,
) -> ResolvedSystemModel:
    """Adds whether Stage 3 actually ran and whether the simulated result
    looked reasonable (`new direction.txt` §21-22) -- see
    `shared/result_validation.py`. `result_validation` is that module's own
    report dict, or None when the compiler was unavailable/skipped."""

    model = load_system_model(path, project_id)
    model.generated_at = _now()
    model.modelica_version = modelica_version
    model.compile_status = compile_status
    model.result_validation = result_validation
    save_system_model(path, model)
    return model
