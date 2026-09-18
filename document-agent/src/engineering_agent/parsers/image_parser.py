"""Image/diagram parser. Mirrors `Document Agent.md`, Section 15.

This is the one parser in the pipeline that is not purely deterministic —
turning a raster diagram into structured relations genuinely requires a
vision model. Vision-derived facts are marked with `parser="image_parser"`
so downstream semantic extraction and evidence records can tell them apart
from parsed text/table facts, exactly as the spec requires.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from pydantic import BaseModel

from engineering_agent.config.settings import SETTINGS
from engineering_agent.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError

_MIME_BY_SUFFIX = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

_VISION_PROMPT = (
    "You are looking at an engineering architecture/control diagram. "
    "Extract every labeled component and every directed connection between "
    "components, exactly as drawn — do not infer connections that are not "
    "visibly present. Return strict JSON."
)


class _DiagramRelation(BaseModel):
    source: str
    target: str
    relation: str


class _DiagramExtraction(BaseModel):
    components: list[str]
    relations: list[_DiagramRelation]
    labels: list[str] = []


class ImageParser(BaseParser):
    parser_name = "image_parser"
    extensions = (".png", ".jpg", ".jpeg")

    def parse(self, document, file_path: Path) -> list[Observation]:
        # Read live, not the frozen SETTINGS snapshot — see extraction/llm.py for why.
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ParserError(
                "image_parser requires OPENAI_API_KEY (vision-based OCR) — set it in .env to parse diagrams."
            )

        from langchain_openai import ChatOpenAI

        mime = _MIME_BY_SUFFIX.get(file_path.suffix.lower(), "image/png")
        b64 = base64.b64encode(file_path.read_bytes()).decode("ascii")
        model = ChatOpenAI(model=SETTINGS.extraction_model, api_key=api_key)
        structured_model = model.with_structured_output(_DiagramExtraction)

        try:
            result = structured_model.invoke(
                [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": _VISION_PROMPT},
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                        ],
                    }
                ]
            )
        except Exception as exc:
            raise ParserError(f"Vision extraction failed: {exc}") from exc

        extraction: _DiagramExtraction = result  # type: ignore[assignment]
        observations: list[Observation] = []
        for relation in extraction.relations:
            observations.append(
                self._obs(
                    document,
                    ObservationType.DIAGRAM_RELATION,
                    f"{relation.source} -> {relation.target} : {relation.relation}",
                )
            )
        if extraction.labels:
            observations.append(self._obs(document, ObservationType.TEXT, "\n".join(extraction.labels)))

        if not observations:
            raise ParserError("Vision model returned no components or relations.")
        return observations

    def _obs(self, document, obs_type: ObservationType, content: str) -> Observation:
        return Observation(
            observation_id=self.next_observation_id(document),
            document_id=document.document_id,
            type=obs_type,
            content=content,
            location=SourceLocation(file=document.path),
            parser=self.parser_name,
            parser_version=self.parser_version,
        )
