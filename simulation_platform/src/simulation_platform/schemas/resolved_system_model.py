"""The ONE central resolved system model, per `new direction.txt` §7:
"Do not allow different agents/stages to independently invent their own
versions of the system." Aggregated (deterministically, no LLM) from each
stage's own already-validated artifacts, not a competing source of new
facts -- Stage 1 populates entities/relationships/requirements/behaviors/
constraints/assumptions/conflicts, Stage 2 adds states/control_logic/
sysml_elements, Stage 3 (when it runs) adds resolved_parameters actually
used in the generated Modelica. See `shared/system_model_builder.py`.
"""

from __future__ import annotations

from pydantic import BaseModel

from .behavior import Behavior
from .constraint import Constraint
from .entity import Entity
from .relationship import Relationship
from .requirement import Requirement
from .uncertainty import Ambiguity, Assumption, Conflict, Unknown


class ResolvedParameter(BaseModel):
    """One value in the final resolved model, with its provenance --
    distinguishes `explicit_problem_value`/`document_value`/`user_value`/
    `derived_value`/`assumed_value` per §16, so no numeric value in the
    system model is ever unattributed."""

    name: str
    value: str | float | int | bool | None = None
    unit: str | None = None
    source: str = "assumed_value"
    reason: str | None = None
    user_approved: bool = False


class ResolvedSystemModel(BaseModel):
    project_id: str
    generated_at: str

    knowledge_version: str | None = None
    sysml_version: str | None = None
    modelica_version: str | None = None

    # -- Stage 1: what the system IS -------------------------------------
    entities: list[Entity] = []
    relationships: list[Relationship] = []
    requirements: list[Requirement] = []
    behaviors: list[Behavior] = []
    constraints: list[Constraint] = []

    # -- Stage 2: how the system is STRUCTURED as SysML -------------------
    states: list[str] = []
    control_logic: list[str] = []
    sysml_elements: dict[str, str] = {}  # engineering_id -> sysml_element_name

    # Real system-reasoning output (`new direction.txt` §10), from the
    # planning stage's own boundary/domain/sensor/actuator/control-law
    # analysis -- see `SysMLGenerationPlan`.
    system_boundary: str = ""
    physical_domains: list[str] = []
    sensors: list[str] = []
    actuators: list[str] = []

    # -- resolved values, honestly sourced (§13/§16) -----------------------
    parameters: list[ResolvedParameter] = []

    # -- Stage 3: did it actually run, and is the result reasonable? -------
    compile_status: str | None = None
    result_validation: dict | None = None  # see shared/result_validation.py

    # -- honesty / provenance (§15/§16) ------------------------------------
    assumptions: list[Assumption] = []
    conflicts: list[Conflict] = []
    unknowns: list[Unknown] = []
    open_questions: list[dict] = []  # from sysml/modelica generation plans -- OpenQuestion.model_dump()
    ambiguities: list[Ambiguity] = []
