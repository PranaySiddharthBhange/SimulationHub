"""Shared LLM plumbing. Mirrors `SysML V2 Agent.md`, Section 27 (five separate
LLM responsibilities — never one prompt for all of them) and the same
discipline used in the Document Agent's `extraction/llm.py`.
"""

from __future__ import annotations

import os
from typing import TypeVar

from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class LLMUnavailable(RuntimeError):
    """Raised when an LLM-dependent stage is invoked without an OPENAI_API_KEY."""


def run_structured(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    response_schema: type[ResponseT],
    callbacks: list | None = None,
) -> ResponseT:
    # Read live, not a frozen settings snapshot — otherwise a test can never
    # simulate "no key" once a real .env exists (see Document Agent's
    # extraction/llm.py, fixed for the identical reason).
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMUnavailable(
            "This stage requires OPENAI_API_KEY — set it in .env before running the planner/mapper."
        )

    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=model_name, api_key=api_key, temperature=0)
    # `method="function_calling"`, not the `with_structured_output` default
    # (`json_schema`, OpenAI's strict structured-outputs mode) -- found live
    # on a real run (see `modelica_gen/llm.py`'s identical fix): OpenAI's
    # strict mode requires "required" to list EVERY property, which
    # Pydantic's default JSON Schema generation doesn't do for any field
    # with a default (e.g. `list[X] = []`) -- a real, hard 400 error for
    # `sysml_repairer.py`'s `_RepairResponse.updated_mappings` field.
    # Verified directly against the real API: the identical schema shape
    # that broke under `json_schema` succeeds under `function_calling`.
    structured_model = model.with_structured_output(response_schema, method="function_calling")
    result = structured_model.invoke(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        config={"callbacks": callbacks} if callbacks else None,
    )
    return result  # type: ignore[return-value]
