"""PDF parser. Mirrors `Document Agent.md`, Section 10."""

from __future__ import annotations

from pathlib import Path

import pymupdf

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError


class PdfParser(BaseParser):
    parser_name = "pdf_parser"
    extensions = (".pdf",)

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            doc = pymupdf.open(file_path)
        except Exception as exc:  # pymupdf raises its own exception types
            raise ParserError(f"Unable to open PDF: {exc}") from exc

        observations: list[Observation] = []
        try:
            for page_index, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if text:
                    observations.append(
                        Observation(
                            observation_id=self.next_observation_id(document),
                            document_id=document.document_id,
                            type=ObservationType.TEXT,
                            content=text,
                            location=SourceLocation(page=page_index),
                            parser=self.parser_name,
                            parser_version=self.parser_version,
                        )
                    )
                for table in page.find_tables().tables:
                    rows = table.extract()
                    if rows:
                        observations.append(
                            Observation(
                                observation_id=self.next_observation_id(document),
                                document_id=document.document_id,
                                type=ObservationType.TABLE,
                                content=_rows_to_text(rows),
                                location=SourceLocation(page=page_index),
                                parser=self.parser_name,
                                parser_version=self.parser_version,
                            )
                        )
        finally:
            doc.close()

        if not observations:
            raise ParserError("PDF produced no extractable text (likely a scanned image; OCR not yet wired in).")
        return observations


def _rows_to_text(rows: list[list[str | None]]) -> str:
    return "\n".join(" | ".join(cell or "" for cell in row) for row in rows)
