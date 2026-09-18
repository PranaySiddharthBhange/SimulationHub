"""SysML Traceability. Mirrors `Agent Contracts.md`, Section 6."""

from __future__ import annotations

from pydantic import BaseModel


class SysMLTraceEntry(BaseModel):
    engineering_id: str
    sysml_element: str
    file: str
    evidence: list[str] = []


class SysMLTraceability(BaseModel):
    sysml_version: str
    entries: list[SysMLTraceEntry] = []
