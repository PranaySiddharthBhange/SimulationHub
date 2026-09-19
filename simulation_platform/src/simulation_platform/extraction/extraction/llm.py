"""Shared LLM plumbing for semantic extraction. Mirrors `Document Agent.md`, Sections 25 and 49-50.

Every extraction call is scoped to one document's observations at a time —
never "all project text in one prompt" — and every call uses a strict
Pydantic response schema, never free-form text.
"""

from __future__ import annotations

import os
from typing import TypeVar

from pydantic import BaseModel

from simulation_platform.extraction.config.settings import SETTINGS
from simulation_platform.schemas import DocumentRecord, Observation

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
    # Read the env var live rather than trusting a frozen settings snapshot
    # taken at process start — otherwise a test can never simulate "no key"
    # once a real .env exists.
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ExtractionUnavailable(
            "Semantic extraction requires OPENAI_API_KEY — set it in .env before running extraction."
        )

    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=SETTINGS.extraction_model, api_key=api_key, temperature=0)
    # `method="function_calling"`, not the `with_structured_output` default
    # (`json_schema`, OpenAI's strict structured-outputs mode) -- found live
    # on a real Stage 2 run (see `modelica_gen/llm.py`'s identical fix):
    # OpenAI's strict mode requires "required" to list EVERY property,
    # which Pydantic's default JSON Schema generation doesn't always do for
    # a field with a default -- a real, hard 400 error for one schema.
    # Applied uniformly here too, even though no Stage 1 schema has hit it
    # yet, since the same class of schema shape could easily show up in a
    # future extractor and `function_calling` is verified not to regress
    # the schemas that already worked.
    structured_model = model.with_structured_output(response_schema, method="function_calling")

    user_prompt = (
        f"Document: {document.path} (role: {document.role.value})\n\n"
        f"Observations (cite the bracketed [obs_id] as evidence — never invent an id):\n\n"
        f"{render_observations(observations)}"
    )
    result = structured_model.invoke(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    )
    return result  # type: ignore[return-value]
