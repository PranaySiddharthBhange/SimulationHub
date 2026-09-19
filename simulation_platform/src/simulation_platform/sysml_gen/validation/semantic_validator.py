"""Layer 5 — Semantic validation (LLM). Mirrors `SysML V2 Agent.md`, Section 17.

The only validation layer that genuinely needs a model: did the generated
SysML preserve the engineering meaning of the contract, not just its syntax?
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.sysml_semantic_review import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.sysml_gen.config import SETTINGS
from simulation_platform.sysml_gen.llm import run_structured
from simulation_platform.schemas import SemanticIssue, SysMLGenerationContract


class _SemanticReview(BaseModel):
    issues: list[SemanticIssue]


def validate_semantics(contract: SysMLGenerationContract, generated_files: dict[str, str]) -> list[SemanticIssue]:
    user_prompt = (
        f"Contract:\n{contract.model_dump_json(indent=2)}\n\n"
        f"Generated SysML:\n\n"
        + "\n\n".join(f"--- {name} ---\n{text}" for name, text in generated_files.items())
    )
    response = run_structured(SETTINGS.validation_model, _SYSTEM_PROMPT, user_prompt, _SemanticReview)
    return response.issues
