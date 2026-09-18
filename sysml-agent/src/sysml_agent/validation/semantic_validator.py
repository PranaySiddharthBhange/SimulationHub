"""Layer 5 — Semantic validation (LLM). Mirrors `SysML V2 Agent.md`, Section 17.

The only validation layer that genuinely needs a model: did the generated
SysML preserve the engineering meaning of the contract, not just its syntax?
"""

from __future__ import annotations

from pydantic import BaseModel

from sysml_agent.config import SETTINGS
from sysml_agent.llm import run_structured
from sysml_agent.schemas import SemanticIssue, SysMLGenerationContract

_SYSTEM_PROMPT = """\
You review a generated SysML v2 model against the engineering contract it \
was supposed to represent. Flag any element whose SysML representation \
does not mean what the contract says it should — e.g. a requirement bound \
that doesn't match the contract's value, or a relationship whose direction \
or type was flipped. Do not flag naming or formatting differences.
"""


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
