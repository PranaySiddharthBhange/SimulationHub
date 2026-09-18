"""Runs the real LangGraph ingestion workflow (not just its individual
functions) against every golden dataset, up to the point where it genuinely
needs an LLM. Confirms: (1) every node before `semantic_extraction` persists
its artifacts to disk correctly, and (2) the graph fails with the specific,
clear `ExtractionUnavailable` error at that boundary — not a confusing crash
somewhere else — when no OPENAI_API_KEY is configured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from engineering_agent.extraction.llm import ExtractionUnavailable
from engineering_agent.storage.project_store import ProjectStore
from engineering_agent.workflows.ingestion_graph import build_ingestion_graph

TEST_CASES_ROOT = Path(__file__).resolve().parents[2] / "test cases"

DATASETS = [
    ("iaq_graph", "iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset"),
    ("magnetic_circuit_graph", "magnetic_circuit_sysmlv2_full_dataset/magnetic_circuit_sysmlv2_full_dataset"),
    ("nacl_evaporation_graph", "nacl_evaporation_sysmlv2_full_dataset/nacl_evaporation_sysmlv2_full_dataset"),
    ("tank_graph", "tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset"),
]


def _initial_state(project_id: str, source_dir: Path) -> dict:
    return {
        "project_id": project_id,
        "source_dir": str(source_dir),
        "files_discovered": 0,
        "files_parsed": 0,
        "files_failed": 0,
        "observations_created": 0,
        "entities_found": 0,
        "relationships_found": 0,
        "requirements_found": 0,
        "behaviors_found": 0,
        "constraints_found": 0,
        "conflicts": 0,
        "ambiguities": 0,
        "unknowns": 0,
        "assumptions": 0,
        "model_version": "",
        "status": "INGESTING",
        "errors": [],
    }


@pytest.mark.parametrize("project_id,relative_source", DATASETS)
def test_graph_runs_deterministic_nodes_then_fails_cleanly_without_llm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, project_id: str, relative_source: str
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    source_dir = TEST_CASES_ROOT / relative_source
    assert source_dir.is_dir(), f"golden dataset missing: {source_dir}"

    store = ProjectStore(tmp_path)
    store.create_project(project_id, project_id, source_dir)
    project_dir = store.project_dir(project_id)

    graph = build_ingestion_graph(store).compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": project_id}}

    with pytest.raises(ExtractionUnavailable):
        graph.invoke(_initial_state(project_id, source_dir), config=config)

    # Everything up to (and including) build_indexes must have persisted correctly.
    manifest_data = json.loads((project_dir / "source_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest_data["documents"]) > 5

    observations_path = project_dir / "observations" / "observations.jsonl"
    assert observations_path.exists()
    observation_lines = [line for line in observations_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(observation_lines) > 0

    for index_name in ("file_index", "topic_index", "information_type_index"):
        index_path = project_dir / "index" / f"{index_name}.json"
        assert index_path.exists(), f"{index_name}.json was not written before the LLM boundary"
        assert json.loads(index_path.read_text(encoding="utf-8")), f"{index_name}.json is empty"

    # The graph must not have progressed to entity resolution / conflict detection / publish.
    assert not (project_dir / "semantic" / "semantic_model.json").exists()
    assert not (project_dir / "versions" / "current.json").exists()
