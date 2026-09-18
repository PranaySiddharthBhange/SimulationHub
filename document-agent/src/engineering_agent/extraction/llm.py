"""Shared LLM plumbing for semantic extraction. Mirrors `Document Agent.md`, Sections 25 and 49-50.

Every extraction call is scoped to one document's observations at a time —
never "all project text in one prompt" — and every call uses a strict
Pydantic response schema, never free-form text.
"""

from __future__ import annotations

import os
from typing import TypeVar

from pydantic import BaseModel

from engineering_agent.config.settings import SETTINGS
from engineering_agent.schemas import DocumentRecord, Observation

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class ExtractionUnavailable(RuntimeError):
    """Raised when semantic extraction is invoked without an OPENAI_API_KEY."""


def render_observations(observations: list[Observation]) -> str:
    """Render a document's observations as a compact, evidence-id-tagged block for the prompt."""

    lines = []
    for obs in observations:
        location = obs.location.model_dump(exclude_none=True)
        lines.append(f"[{obs.observation_id}] ({obs.type.value} @ {location}) {obs.content}")
    return "\n".join(lines)


def run_structured_extraction(
    system_prompt: str,
    document: DocumentRecord,
    observations: list[Observation],
    response_schema: type[ResponseT],
) -> ResponseT:
    # Read the env var live rather than trusting the frozen SETTINGS snapshot
    # taken at process start — otherwise a test can never simulate "no key"
    # once a real .env exists, since SETTINGS.openai_api_key would already be set.
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ExtractionUnavailable(
            "Semantic extraction requires OPENAI_API_KEY — set it in .env before running extraction."
        )

    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=SETTINGS.extraction_model, api_key=api_key, temperature=0)
    structured_model = model.with_structured_output(response_schema)

    user_prompt = (
        f"Document: {document.path} (role: {document.role.value})\n\n"
        f"Observations (cite the bracketed [obs_id] as evidence — never invent an id):\n\n"
        f"{render_observations(observations)}"
    )
    result = structured_model.invoke(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    )
    return result  # type: ignore[return-value]
