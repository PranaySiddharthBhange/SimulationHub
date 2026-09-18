"""Shared primitives. Mirrors `Agent Contracts.md`, Section 1."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class FactStatus(str, Enum):
    EXPLICIT = "EXPLICIT"
    CONFIRMED = "CONFIRMED"
    INFERRED = "INFERRED"
    ASSUMED = "ASSUMED"
    PROPOSED = "PROPOSED"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"
    USER_CONFIRMED = "USER_CONFIRMED"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"


class Comparator(str, Enum):
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    EQ = "=="
    RANGE = "RANGE"


class VersionRef(BaseModel):
    knowledge_version: str
    sysml_version: str | None = None
