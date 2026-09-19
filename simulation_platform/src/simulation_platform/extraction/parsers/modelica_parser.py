"""Modelica parser. Mirrors `Document Agent.md`, Section 17.

Treats `.mo` as source code and NEVER executes it (execution belongs to the
Compiler / Simulation Agent — see `Compiler Agent.md`). This is a pragmatic
regex-based extraction, not a full Modelica grammar/AST — good enough to
recover class declarations, parameters (with their inline description
strings, which is where legacy files flag stale values), equations, and
`connect()` topology, each with an exact line number.
"""

from __future__ import annotations

import re
from pathlib import Path

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError

_CLASS_DECL = re.compile(r"^\s*(model|block|package|class|record|connector)\s+(\w+)")
_PARAMETER_DECL = re.compile(
    r'^\s*parameter\s+\w+(?:\.\w+)*\s+(\w+)\s*=\s*([^;"]+?)\s*(?:"([^"]*)")?\s*;'
)
_CONNECT_CALL = re.compile(r"connect\s*\(\s*([\w.]+)\s*,\s*([\w.]+)\s*\)\s*;")
_EQUATION_SECTION = re.compile(r"^\s*(equation|algorithm)\b")
_END_DECL = re.compile(r"^\s*end\s+\w+\s*;")
_COMMENT = re.compile(r"//.*$")


class ModelicaParser(BaseParser):
    parser_name = "modelica_parser"
    extensions = (".mo",)

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ParserError(f"Unable to read Modelica file: {exc}") from exc

        observations: list[Observation] = []
        in_equation_section = False

        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("//"):
                continue

            if class_match := _CLASS_DECL.match(line):
                observations.append(self._obs(document, document.path, line_no, f"{class_match.group(1)} {class_match.group(2)}"))
                continue

            if param_match := _PARAMETER_DECL.match(line):
                name, value, description = param_match.groups()
                content = f"parameter {name} = {value.strip()}"
                if description:
                    content += f'  // "{description}"'
                observations.append(self._obs(document, document.path, line_no, content))
                continue

            for source, target in _CONNECT_CALL.findall(line):
                observations.append(self._obs(document, document.path, line_no, f"{source} -> {target}"))

            if _EQUATION_SECTION.match(line):
                in_equation_section = True
                continue
            if _END_DECL.match(line):
                in_equation_section = False
                continue

            if in_equation_section and line.endswith(";"):
                cleaned = _COMMENT.sub("", line).strip()
                if cleaned:
                    observations.append(self._obs(document, document.path, line_no, cleaned))

        if not observations:
            raise ParserError("No recognizable Modelica constructs found (class/parameter/connect/equation).")
        return observations

    def _obs(self, document, file: str, line: int, content: str) -> Observation:
        return Observation(
            observation_id=self.next_observation_id(document),
            document_id=document.document_id,
            type=ObservationType.CODE,
            content=content,
            location=SourceLocation(file=file, line=line),
            parser=self.parser_name,
            parser_version=self.parser_version,
        )
