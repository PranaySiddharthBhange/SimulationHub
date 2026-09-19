"""XLSX parser. Mirrors `Document Agent.md`, Section 11.

Never flattens a register into prose: each sheet gets one TABLE observation
(the full grid, for context) plus one CELL observation per non-empty data
cell (for exact `sheet`/`cell` provenance), matching the sheet+cell location
example in the spec (`Requirements!F17`).
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError


class XlsxParser(BaseParser):
    parser_name = "xlsx_parser"
    extensions = (".xlsx", ".xlsm")

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            workbook = openpyxl.load_workbook(str(file_path), data_only=True)
        except Exception as exc:
            raise ParserError(f"Unable to open XLSX: {exc}") from exc

        observations: list[Observation] = []
        for sheet in workbook.worksheets:
            rows = list(sheet.iter_rows(values_only=False))
            if not rows:
                continue

            headers = [str(c.value).strip() if c.value is not None else "" for c in rows[0]]

            grid_text = "\n".join(
                " | ".join("" if c.value is None else str(c.value) for c in row) for row in rows
            )
            observations.append(
                Observation(
                    observation_id=self.next_observation_id(document),
                    document_id=document.document_id,
                    type=ObservationType.TABLE,
                    content=grid_text,
                    location=SourceLocation(sheet=sheet.title),
                    parser=self.parser_name,
                    parser_version=self.parser_version,
                )
            )

            for row in rows[1:]:
                for col_index, cell in enumerate(row):
                    if cell.value is None or cell.value == "":
                        continue
                    header = headers[col_index] if col_index < len(headers) else ""
                    content = f"{header}: {cell.value}" if header else str(cell.value)
                    observations.append(
                        Observation(
                            observation_id=self.next_observation_id(document),
                            document_id=document.document_id,
                            type=ObservationType.CELL,
                            content=content,
                            location=SourceLocation(sheet=sheet.title, cell=cell.coordinate),
                            parser=self.parser_name,
                            parser_version=self.parser_version,
                        )
                    )

        if not observations:
            raise ParserError("Workbook contained no non-empty sheets.")
        return observations
