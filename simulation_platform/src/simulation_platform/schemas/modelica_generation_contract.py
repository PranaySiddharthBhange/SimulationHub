"""Modelica Generation Contract. Mirrors `Agent Contracts.md`, Section 8,
and `Modelica Agent.md`, Section 7.

Deliberately thin -- every list here is engineering-id references, not full
items (unlike the SysML Generation Contract). The full item content lives
upstream: `analysis/sysml_analyzer.py` parses the actual generated `.sysml`
text for structure, and `storage/from_sysml_agent.py` cross-references the
SysML Agent's own persisted input contract (`sysml/input/generation_contract
.json`) for anything numeric/typed that can't be reliably recovered from a
SysML doc comment.
"""

from __future__ import annotations

from pydantic import BaseModel

from .common import VersionRef


class ModelicaGenerationContract(BaseModel):
    project_id: str
    version: VersionRef  # sysml_version + knowledge_version required here

    components: list[str] = []  # SysMLElementMapping.engineering_id list, part-typed
    properties: list[str] = []
    interfaces: list[str] = []
    behaviors: list[str] = []
    control_laws: list[str] = []
    constraints: list[str] = []

    legacy_models: list[str] = []  # filenames under source/original/, e.g. 07_legacy_co2_control.mo
