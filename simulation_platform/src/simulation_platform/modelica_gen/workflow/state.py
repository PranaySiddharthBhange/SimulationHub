"""LangGraph state. Mirrors `Modelica Agent.md`, Section 29 -- small,
serializable fields only; every artifact this workflow actually produces
lives on disk (`storage/modelica_store.py`), not in graph state.
"""

from __future__ import annotations

from typing import TypedDict


class ModelicaState(TypedDict):
    project_id: str
    generation_id: str
    modelica_version: str

    components_in_contract: int
    properties_in_contract: int
    legacy_files_found: int
    legacy_comparisons_found: int

    mappings_created: int
    state_machines_synthesized: int
    files_generated: int

    validation_status: str
    compile_status: str
    result_validation_status: str
    repair_attempt: int
    validation_error_signature: str
    compile_error_signature: str
    result_validation_error_signature: str
    repair_stalled: bool
    status: str
