"""SysML Agent workflow state. Mirrors `SysML V2 Agent.md`, Section 25.

Kept small: ids and counts, never the generated SysML text or the full
contract — those live on disk, loaded by each node as needed.
"""

from __future__ import annotations

from typing import TypedDict


class SysMLState(TypedDict):
    project_id: str
    generation_id: str

    entities_in_contract: int
    requirements_in_contract: int

    mappings_created: int
    files_generated: int

    validation_status: str
    repair_attempt: int
    validation_error_signature: str
    repair_stalled: bool

    sysml_version: str
    status: str
