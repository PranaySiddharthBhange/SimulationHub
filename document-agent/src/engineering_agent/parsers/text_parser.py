"""Plain-text parser. Mirrors `Document Agent.md`, Section 9 (TXT row).

One observation per blank-line-separated paragraph, so field notes and
scratch notes keep some internal structure instead of becoming one giant blob.
"""

from __future__ import annotations

from pathlib import Path

from engineering_agent.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError


class TextParser(BaseParser):
    parser_name = "text_parser"
    extensions = (".txt",)

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ParserError(f"Unable to read text file: {exc}") from exc

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            raise ParserError("Text file was empty.")

        return [
            Observation(
                observation_id=self.next_observation_id(document),
                document_id=document.document_id,
                type=ObservationType.TEXT,
                content=paragraph,
                location=SourceLocation(section=f"paragraph {index}"),
                parser=self.parser_name,
                parser_version=self.parser_version,
            )
            for index, paragraph in enumerate(paragraphs, start=1)
        ]
