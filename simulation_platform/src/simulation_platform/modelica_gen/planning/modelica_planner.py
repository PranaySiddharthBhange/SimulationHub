"""Model Planner -- LLM stage 1. Mirrors `Modelica Agent.md`, Section 29's
`ModelicaState.generation_plan`, and the identical two-stage split
(plan shape, then map elements) already used by the SysML Agent's own
`planning/model_planner.py`.

Decides the SHAPE of the Modelica model -- which packages to create, which
components/behaviors/constraints from the contract are actually worth
representing given what the SysML analysis, legacy comparison, and library
resolution already found -- without writing any Modelica syntax yet.

Response schema fields are fully-typed Pydantic models throughout
(`OpenQuestion`, not a bare `dict`) -- a bare `dict` field is exactly the
bug the SysML Agent's planner shipped with and had fixed after its first
live run (OpenAI's structured-output mode rejects a nested object schema
without `additionalProperties: false`, which Pydantic only emits for a real
`BaseModel`). See `DECISIONS.md` D20 -- fixed here before ever running live.
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.llm import run_structured
from simulation_platform.prompts.modelica_planning import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.skills import with_modelica_skills
from simulation_platform.schemas import (
    LegacyComparison,
    ModelicaGenerationContract,
    ModelicaGenerationPlan,
    OpenQuestion,
    SysMLSemanticModel,
)

_SYSTEM_PROMPT = with_modelica_skills(_BASE_SYSTEM_PROMPT)


class _PlanResponse(BaseModel):
    packages: list[str]
    components: list[str]
    properties: list[str]
    behaviors: list[str]
    control_laws: list[str] = []
    constraints: list[str]
    open_questions: list[OpenQuestion] = []


def _keep_real_ids(proposed: list[str], real_ids: list[str]) -> list[str]:
    """Deterministic backstop, same discipline as `sysml_gen/mapping/
    element_mapper.py`'s `_deduplicate_names`/`_backfill_evidence` --
    found live on a real dataset: the planner's response substituted a
    SysML part/requirement NAME (e.g. "V1_open_during_normal_operation")
    for a real engineering id (e.g. "REQ-0001") despite both being shown
    in the prompt, and every downstream stage's `{id}_by_id.get(name)`
    lookup silently returned nothing for it -- an ENTIRE real Tank system
    (14 components, 192 properties, 72 behaviors) collapsed into a
    completely empty generated model that still reported a clean PASSED
    compile status, since an empty model trivially compiles. Dropping a
    name here is a real, disclosed loss of that one item (better surfaced
    by `structure_validator.py`'s empty-model check than silently kept as
    a dangling reference), never a guess at what real id was meant."""

    real = set(real_ids)
    return [item for item in proposed if item in real]


def _drop_dataset_properties(property_ids: list[str], sysml_contract_raw: dict | None) -> list[str]:
    """Deterministic backstop alongside the prompt's own "exclude dataset/
    benchmark facts" instruction -- found live on a real dataset: a
    requirement extracted from the project's own benchmark CSV ("dataset
    09_datasets/10_demo_run_900s.csv", property "row_count", unit "rows")
    was selected as needing its own Modelica parameter, producing a real,
    non-recoverable unit-validation failure (there is no sensible physical
    unit for "rows"). Every requirement genuinely extracted FROM a dataset
    file -- not a real system component -- has this exact, precise
    "dataset <path>" subject prefix (`extraction/extraction/requirement_
    extractor.py`'s own convention); these are ground-truth VALIDATION
    bounds for `evaluate_simulation_result` to check post-simulation, never
    something needing Modelica representation. A prompt instruction alone
    isn't fully reliable (the same lesson as `_keep_real_ids`/`sysml_gen`'s
    `_backfill_evidence`), so this guarantees it."""

    if not sysml_contract_raw:
        return property_ids
    subject_by_id = {r["id"]: r.get("subject", "") for r in sysml_contract_raw.get("requirements", [])}
    return [
        property_id for property_id in property_ids
        if not subject_by_id.get(property_id, "").lower().startswith("dataset ")
    ]


def create_modelica_plan(
    contract: ModelicaGenerationContract,
    generation_id: str,
    sysml_semantic_model: SysMLSemanticModel,
    legacy_comparisons: list[LegacyComparison],
    extra_context: str = "",
    sysml_contract_raw: dict | None = None,
) -> ModelicaGenerationPlan:
    user_prompt = (
        f"Project: {contract.project_id}\n\n"
        f"Component ids to consider: {contract.components}\n"
        f"Property/requirement ids to consider: {contract.properties}\n"
        f"Behavior ids to consider: {contract.behaviors}\n"
        f"Control law ids to consider: {contract.control_laws}\n"
        f"Constraint ids to consider: {contract.constraints}\n"
        f"Legacy models available: {contract.legacy_models}\n\n"
        f"SysML parts (def, instance): {[(p.part_def, p.instance_name) for p in sysml_semantic_model.parts]}\n"
        f"SysML connections: {[(c.source_instance, c.target_instance, c.relationship_type) for c in sysml_semantic_model.connections]}\n"
        f"SysML requirements: {[(r.name, r.doc, r.property) for r in sysml_semantic_model.requirements]}\n"
        f"SysML behaviors: {[(b.name, b.comment) for b in sysml_semantic_model.behaviors]}\n"
        f"SysML constraints: {[(c.name, c.property) for c in sysml_semantic_model.constraints]}\n\n"
        f"Legacy comparisons already computed: {[c.model_dump() for c in legacy_comparisons]}"
    )
    if extra_context:
        # A retrieval pass over problem.md/documents/ run after a first
        # attempt left open_questions (`new direction.txt` §9/§40) -- may
        # resolve some of them.
        user_prompt += f"\n\nAdditional information found by searching the project's own documents:\n{extra_context}"
    response = run_structured(SETTINGS.planning_model, _SYSTEM_PROMPT, user_prompt, _PlanResponse)
    return ModelicaGenerationPlan(
        project_id=contract.project_id,
        generation_id=generation_id,
        packages=response.packages,
        components=_keep_real_ids(response.components, contract.components),
        properties=_drop_dataset_properties(_keep_real_ids(response.properties, contract.properties), sysml_contract_raw),
        behaviors=_keep_real_ids(response.behaviors, contract.behaviors),
        control_laws=_keep_real_ids(response.control_laws, contract.control_laws),
        constraints=_keep_real_ids(response.constraints, contract.constraints),
        open_questions=response.open_questions,
    )
