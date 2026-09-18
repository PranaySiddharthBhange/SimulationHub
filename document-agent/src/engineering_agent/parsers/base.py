"""Parser interface. Mirrors `Document Agent.md`, Section 9.

Every parser turns one source file into a list of `Observation` records.
Parsers never create entities/relationships/requirements directly — that is
the job of the semantic extraction stage (`extraction/`), which runs on
observations, not on raw files.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import count
from pathlib import Path
from typing import ClassVar

from engineering_agent.schemas import DocumentRecord, Observation


class ParserError(Exception):
    """Raised by a parser when a file cannot be parsed at all."""


class BaseParser(ABC):
    parser_name: ClassVar[str]
    parser_version: ClassVar[str] = "1.0"
    extensions: ClassVar[tuple[str, ...]] = ()

    def __init__(self) -> None:
        self._counter = count(1)

    def next_observation_id(self, document: DocumentRecord) -> str:
        return f"obs_{document.document_id}_{next(self._counter):04d}"

    @abstractmethod
    def parse(self, document: DocumentRecord, file_path: Path) -> list[Observation]:
        """Parse `file_path` and return its observations. Raise `ParserError` on failure."""
