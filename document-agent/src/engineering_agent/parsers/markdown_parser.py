"""Markdown parser. Mirrors `Document Agent.md`, Section 9 (Markdown row).

A lightweight custom parser rather than a full CommonMark implementation:
splits on ATX headings (`#`...`######`) to track section context, and emits
one observation per paragraph.
"""

from __future__ import annotations

import re
from pathlib import Path

from engineering_agent.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


class MarkdownParser(BaseParser):
    parser_name = "markdown_parser"
    extensions = (".md", ".markdown")

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ParserError(f"Unable to read Markdown file: {exc}") from exc

        observations: list[Observation] = []
        current_section = "(document start)"
        paragraph: list[str] = []

        def flush() -> None:
            if not paragraph:
                return
            content = "\n".join(paragraph).strip()
            paragraph.clear()
            if content:
                observations.append(
                    Observation(
                        observation_id=self.next_observation_id(document),
                        document_id=document.document_id,
                        type=ObservationType.TEXT,
                        content=content,
                        location=SourceLocation(section=current_section),
                        parser=self.parser_name,
                        parser_version=self.parser_version,
                    )
                )

        for line in text.splitlines():
            heading = _HEADING.match(line)
            if heading:
                flush()
                current_section = heading.group(2).strip()
                continue
            if line.strip() == "":
                flush()
                continue
            paragraph.append(line)
        flush()

        if not observations:
            raise ParserError("Markdown file contained no text.")
        return observations
