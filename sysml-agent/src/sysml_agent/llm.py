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
    structured_model = model.with_structured_output(response_schema)
    result = structured_model.invoke(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    )
    return result  # type: ignore[return-value]
