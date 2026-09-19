"""Auto-repair — LLM stage. Runs after `validate_generation` or the real
`compile_check` fails. Fixes the MAPPINGS (not generated file text) because
`generate_modelica_files` deterministically recomputes every file from
`mappings` on every call — see `workflow/modelica_graph.py`'s repair loop,
which re-enters at `generate_modelica` after this so the fix actually
takes effect.
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.llm import run_structured
from simulation_platform.prompts.modelica_repair import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.schemas import CompileResult, ModelicaMapping, ModelicaValidationResult
from simulation_platform.skills import with_modelica_skills

_SYSTEM_PROMPT = with_modelica_skills(_BASE_SYSTEM_PROMPT)


class _RepairResponse(BaseModel):
    mappings: list[ModelicaMapping]


def repair_modelica_mappings(
    mappings: list[ModelicaMapping],
    validation_result: ModelicaValidationResult | None,
    compile_result: CompileResult | None,
    result_validation_report: dict | None = None,
    callbacks: list | None = None,
) -> list[ModelicaMapping]:
    """Returns a new mapping list: `mappings` with any corrected entry
    (matched by `sysml_element`) replaced. Entries the model didn't touch
    are returned unchanged.

    `callbacks` is where the caller attaches a `BudgetGuard` scoped to the
    repair loop's own separate budget (see `workflow/modelica_graph.py`) --
    distinct from the stage's main planning/mapping/validation budget."""

    user_prompt_parts = [f"Current mappings: {[m.model_dump() for m in mappings]}"]
    if validation_result is not None:
        user_prompt_parts.append(
            f"Validation report (status={validation_result.status.value}): "
            f"{[i.model_dump() for i in validation_result.issues]}"
        )
    if compile_result is not None:
        user_prompt_parts.append(
            f"Compiler report (status={compile_result.status.value}): "
            f"{[e.model_dump() for e in compile_result.errors]}"
        )
    if result_validation_report is not None:
        user_prompt_parts.append(
            f"Simulation result validation (status={result_validation_report.get('status')}): "
            f"the model COMPILED AND RAN, but the actual simulated trajectory violates real "
            f"requirement bounds or contains a NaN/Inf -- issues="
            f"{result_validation_report.get('issues', [])}"
        )
    user_prompt = "\n\n".join(user_prompt_parts)

    response = run_structured(SETTINGS.repair_model, _SYSTEM_PROMPT, user_prompt, _RepairResponse, callbacks=callbacks)
    corrected_by_element = {m.sysml_element: m for m in response.mappings}
    return [corrected_by_element.get(m.sysml_element, m) for m in mappings]
