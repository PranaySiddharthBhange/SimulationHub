"""Ingestion workflow state. Mirrors `Document Agent.md`, Section 53.

Kept small on purpose: no full document contents, no full observation
bodies — only ids, counts, and status flags. Large content stays on disk.
"""

from __future__ import annotations

from typing import TypedDict


class KnowledgeState(TypedDict):
    project_id: str
    source_dir: str

    files_discovered: int
    files_parsed: int
    files_failed: int

    observations_created: int

    entities_found: int
    relationships_found: int
    requirements_found: int
    behaviors_found: int
    constraints_found: int

    conflicts: int
    ambiguities: int
    unknowns: int
    assumptions: int
    topology_discrepancies: int

    model_version: str
    status: str
    errors: list[str]
