"""Auto-repair — LLM stage. Runs only after `validate_generation` fails.
Feeds the generated files plus the exact structured validation errors back
to an LLM and asks it to fix only what's flagged, then the caller
re-validates — see `workflow/sysml_graph.py`'s repair loop.

Kept as its own call (not folded into `mapping/element_mapper.py`) because
its input/output shape is different: it edits already-generated file TEXT
directly against concrete parser errors, not abstract contract elements.

Found live in this session's own gap audit: fixing file TEXT directly,
with no corresponding update to `mappings.json`, silently let the two
drift apart -- e.g. a requirement-coverage gap resolved by adding a brand
new `requirement def` in the file left NO mapping entry behind it at all.
`updated_mappings` (see the prompt) closes this: the SAME repair call also
reports any new/renamed traceable element its file edits introduced, which
the caller merges back into `mappings.json` -- not a full re-architecture
into mapping-driven regeneration (a genuinely different repair strategy
this module deliberately doesn't use), just keeping the two artifacts from
silently disagreeing about what the model actually contains.
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.sysml_repair import SYSTEM_PROMPT as _BASE_SYSTEM_PROMPT
from simulation_platform.schemas import SysMLElementMapping, SysMLValidationResult
from simulation_platform.skills import with_sysml_skills
from simulation_platform.sysml_gen.config import SETTINGS
from simulation_platform.sysml_gen.llm import run_structured

_SYSTEM_PROMPT = with_sysml_skills(_BASE_SYSTEM_PROMPT)


class _RepairResponse(BaseModel):
    files: dict[str, str]
    updated_mappings: list[SysMLElementMapping] = []


def repair_sysml_files(
    files: dict[str, str],
    validation_result: SysMLValidationResult,
    mappings: list[SysMLElementMapping] | None = None,
    callbacks: list | None = None,
) -> tuple[dict[str, str], list[SysMLElementMapping]]:
    """Returns `(files, mappings)`: `files` is `files` with any repaired
    file's text replaced (untouched files returned unchanged); `mappings`
    is the given `mappings` (or `[]` if none given) with any `engineering_id`
    the repair introduced/renamed replaced -- everything else passed
    straight through unchanged, exactly like `command_overrides`'s
    apply-only-what-changed convention elsewhere in this platform.

    `callbacks` is where the caller attaches a `BudgetGuard` scoped to the
    repair loop's own separate budget (see `workflow/sysml_graph.py`) --
    distinct from the stage's main planning/mapping/validation budget."""

    user_prompt = (
        f"Current files:\n{files}\n\n"
        f"Validation report (status={validation_result.status.value}):\n"
        f"Syntax errors: {[e.model_dump() for e in validation_result.syntax_errors]}\n"
        f"Structural errors: {[e.model_dump() for e in validation_result.structural_errors]}\n"
        f"Requirement coverage gaps: {validation_result.requirement_coverage.missing}\n"
        f"Traceability errors: {[e.model_dump() for e in validation_result.traceability_errors]}\n"
        f"Semantic errors: {[e.model_dump() for e in validation_result.semantic_errors]}"
    )
    response = run_structured(SETTINGS.repair_model, _SYSTEM_PROMPT, user_prompt, _RepairResponse, callbacks=callbacks)

    updated_by_id = {m.engineering_id: m for m in response.updated_mappings}
    merged_mappings = [updated_by_id.pop(m.engineering_id, m) for m in (mappings or [])]
    merged_mappings.extend(updated_by_id.values())  # any genuinely new id, not just a replacement

    return {**files, **response.files}, merged_mappings
