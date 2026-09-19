"""Observation schema. Mirrors `Document Agent.md`, Section 18 (Observation Store)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .common import SourceLocation


class ObservationType(str, Enum):
    TEXT = "TEXT"
    TABLE = "TABLE"
    CELL = "CELL"
    ROW = "ROW"
    FIGURE = "FIGURE"
    CAPTION = "CAPTION"
    EMAIL_MESSAGE = "EMAIL_MESSAGE"
    DIAGRAM_RELATION = "DIAGRAM_RELATION"
    CODE = "CODE"
    JSON_VALUE = "JSON_VALUE"
    DATASET_SUMMARY = "DATASET_SUMMARY"


class Observation(BaseModel):
    observation_id: str
    document_id: str
    type: ObservationType
    content: str
    location: SourceLocation
    parser: str
    parser_version: str = "1.0"
