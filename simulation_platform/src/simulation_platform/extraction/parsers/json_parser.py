"""JSON parser. Mirrors `Document Agent.md`, Section 13.

Preserves the exact JSON path to every leaf value, so provenance can point
at e.g. `rooms[3].equipment[1].setpoint` instead of "somewhere in the file".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError


def _walk(value: Any, path: str) -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        leaves: list[tuple[str, Any]] = []
        for key, sub in value.items():
            leaves.extend(_walk(sub, f"{path}.{key}" if path else key))
        return leaves
    if isinstance(value, list):
        leaves = []
        for index, sub in enumerate(value):
            leaves.extend(_walk(sub, f"{path}[{index}]"))
        return leaves
    return [(path, value)]


class JsonParser(BaseParser):
    parser_name = "json_parser"
    extensions = (".json",)

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ParserError(f"Unable to parse JSON: {exc}") from exc

        leaves = _walk(data, "")
        if not leaves:
            raise ParserError("JSON document contained no leaf values.")

        return [
            Observation(
                observation_id=self.next_observation_id(document),
                document_id=document.document_id,
                type=ObservationType.JSON_VALUE,
                content=f"{path} = {value!r}",
                location=SourceLocation(json_path=path),
                parser=self.parser_name,
                parser_version=self.parser_version,
            )
            for path, value in leaves
        ]
