"""Layer 6 -- Semantic validation (LLM). Mirrors `Modelica Agent.md`,
Section 22 and Section 28's warning not to conclude "compiles, therefore
done." The only validation layer that genuinely needs a model: does the
generated Modelica actually represent the SysML system it was supposed to
implement, not just parse cleanly?
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.modelica_gen.config import SETTINGS
from simulation_platform.modelica_gen.llm import run_structured
from simulation_platform.prompts.modelica_semantic_review import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import ModelicaValidationIssue


class _SemanticReview(BaseModel):
    issues: list[ModelicaValidationIssue]


def validate_semantics(sysml_contract_raw: dict, generated_files: dict[str, str]) -> list[ModelicaValidationIssue]:
    user_prompt = (
        f"Engineering/SysML contract:\n{sysml_contract_raw}\n\n"
        f"Generated Modelica:\n\n"
        + "\n\n".join(f"--- {name} ---\n{text}" for name, text in generated_files.items())
    )
    response = run_structured(SETTINGS.validation_model, _SYSTEM_PROMPT, user_prompt, _SemanticReview)
    return response.issues
