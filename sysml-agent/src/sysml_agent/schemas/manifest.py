"""SysML Manifest. Mirrors `Agent Contracts.md`, Section 7."""

from __future__ import annotations

from pydantic import BaseModel


class SysMLManifest(BaseModel):
    sysml_version: str
    knowledge_version: str
    files: list[str] = []
    requirement_map: dict[str, str] = {}
    entity_map: dict[str, str] = {}
