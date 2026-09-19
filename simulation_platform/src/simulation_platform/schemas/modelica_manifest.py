"""Modelica Manifest. Mirrors `Agent Contracts.md`, Section 13, and
`Modelica Agent.md`, Section 20.
"""

from __future__ import annotations

from pydantic import BaseModel


class ModelicaManifest(BaseModel):
    modelica_version: str
    sysml_version: str
    knowledge_version: str
    entry_class: str
    classes: list[str]
    files: list[str]
