"""CSV parser. Mirrors `Document Agent.md`, Section 12.

Never sends a full dataset to the LLM: the parser extracts column-level
statistics into one `DATASET_SUMMARY` observation. The raw file remains on
disk and queryable through `retrieval.tools.get_dataset_rows` /
`get_dataset_statistics`, using `document.path` as the file key.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from simulation_platform.schemas import Observation, ObservationType, SourceLocation

from .base import BaseParser, ParserError

_TIME_COLUMN_HINTS = ("time", "timestamp", "t_s", "t (s)")


def _guess_time_column(columns: list[str]) -> str | None:
    for col in columns:
        if any(hint in col.lower() for hint in _TIME_COLUMN_HINTS):
            return col
    return None


class CsvParser(BaseParser):
    parser_name = "csv_parser"
    extensions = (".csv",)

    def parse(self, document, file_path: Path) -> list[Observation]:
        try:
            frame = pd.read_csv(file_path)
        except Exception as exc:
            raise ParserError(f"Unable to parse CSV: {exc}") from exc

        if frame.empty:
            raise ParserError("CSV contained no rows.")

        columns = list(frame.columns)
        time_column = _guess_time_column(columns)

        summary: dict[str, object] = {
            "row_count": int(len(frame)),
            "columns": columns,
            "time_column": time_column,
            "missing_counts": {col: int(frame[col].isna().sum()) for col in columns},
        }

        numeric = frame.select_dtypes(include="number")
        summary["numeric_stats"] = {
            col: {"min": float(numeric[col].min()), "max": float(numeric[col].max()), "mean": float(numeric[col].mean())}
            for col in numeric.columns
        }

        if time_column is not None and len(frame) > 1 and time_column in numeric.columns:
            deltas = numeric[time_column].diff().dropna()
            if not deltas.empty:
                summary["sampling_period"] = float(deltas.median())

        return [
            Observation(
                observation_id=self.next_observation_id(document),
                document_id=document.document_id,
                type=ObservationType.DATASET_SUMMARY,
                content=json.dumps(summary, indent=2),
                location=SourceLocation(file=document.path),
                parser=self.parser_name,
                parser_version=self.parser_version,
            )
        ]
