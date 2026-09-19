"""PlantUML parser. Mirrors `Document Agent.md`, Section 16.

Regex-based extraction rather than a full PlantUML grammar: recovers
component declarations, `A --> B : label` relations (as
`DIAGRAM_RELATION` observations, matching the spec's worked example), and
`note ... end note` blocks — which in these datasets often carry the
engineering decision that resolves an ambiguity in the diagram itself.
"""

from __future__ import annotations

import re
from pathlib import Path

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError

_COMPONENT = re.compile(r'component\s+"([^"]+)"\s+as\s+(\w+)')
_RELATION = re.compile(r"(\w+)\s*-+>\s*(\w+)\s*(?::\s*(.*))?$")
_NOTE_START = re.compile(r"note\s+\w+(?:\s+of\s+(\w+))?", re.IGNORECASE)
_NOTE_END = re.compile(r"end\s+note", re.IGNORECASE)


class PumlParser(BaseParser):
    parser_name = "puml_parser"
    extensions = (".puml", ".plantuml")

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception as exc:
            raise ParserError(f"Unable to read PlantUML file: {exc}") from exc

        observations: list[Observation] = []
        note_buffer: list[str] | None = None
        note_start_line = 0
        note_subject: str | None = None

        for line_no, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if line.startswith("'") or not line:
                continue

            if note_buffer is not None:
                if _NOTE_END.match(line):
                    subject = f" (on {note_subject})" if note_subject else ""
                    observations.append(
                        self._obs(
                            document,
                            ObservationType.TEXT,
                            "\n".join(note_buffer),
                            SourceLocation(file=document.path, line=note_start_line),
                        )
                    )
                    note_buffer = None
                    continue
                note_buffer.append(line)
                continue

            if note_match := _NOTE_START.match(line):
                note_buffer = []
                note_start_line = line_no
                note_subject = note_match.group(1)
                continue

            if comp_match := _COMPONENT.search(line):
                label, alias = comp_match.groups()
                observations.append(
                    self._obs(
                        document,
                        ObservationType.DIAGRAM_RELATION,
                        f"component {alias}: {label}",
                        SourceLocation(file=document.path, line=line_no),
                    )
                )
                continue

            if rel_match := _RELATION.search(line):
                source, target, label = rel_match.groups()
                content = f"{source} -> {target}" + (f" : {label}" if label else "")
                observations.append(
                    self._obs(document, ObservationType.DIAGRAM_RELATION, content, SourceLocation(file=document.path, line=line_no))
                )

        if not observations:
            raise ParserError("No components, relations, or notes found in PlantUML file.")
        return observations

    def _obs(self, document, obs_type: ObservationType, content: str, location: SourceLocation) -> Observation:
        return Observation(
            observation_id=self.next_observation_id(document),
            document_id=document.document_id,
            type=obs_type,
            content=content,
            location=location,
            parser=self.parser_name,
            parser_version=self.parser_version,
        )
