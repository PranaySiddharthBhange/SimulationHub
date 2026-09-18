"""RunLogger against the real ingestion graph: confirms every deterministic
node logs a start/end pair, and the node that raises without an LLM key
logs a node_error with the right node name attached (verified this needs
tracking `run_id -> name` ourselves — `on_chain_error` doesn't get `name`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from engineering_agent.extraction.llm import ExtractionUnavailable
from engineering_agent.observability import RunLogger
from engineering_agent.storage.project_store import ProjectStore
from engineering_agent.workflows.ingestion_graph import build_ingestion_graph

TEST_CASES_ROOT = Path(__file__).resolve().parents[2] / "test cases"
TANK_DATASET = TEST_CASES_ROOT / "tank_sysmlv2_full_dataset" / "tank_sysmlv2_full_dataset"


def _initial_state(project_id: str, source_dir: Path) -> dict:
    return {
        "project_id": project_id, "source_dir": str(source_dir),
        "files_discovered": 0, "files_parsed": 0, "files_failed": 0, "observations_created": 0,
        "entities_found": 0, "relationships_found": 0, "requirements_found": 0,
        "behaviors_found": 0, "constraints_found": 0,
        "conflicts": 0, "ambiguities": 0, "unknowns": 0, "assumptions": 0,
        "model_version": "", "status": "INGESTING", "errors": [],
    }


def _read_log(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_run_logger_captures_node_trail_and_the_exact_failing_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert TANK_DATASET.is_dir()

    store = ProjectStore(tmp_path)
    store.create_project("tank_log_test", "tank_log_test", TANK_DATASET)
    project_dir = store.project_dir("tank_log_test")

    logger = RunLogger(project_dir, run_id="test_run_001")
    graph = build_ingestion_graph(store).compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "tank_log_test"}, "callbacks": [logger]}

    with pytest.raises(ExtractionUnavailable):
        graph.invoke(_initial_state("tank_log_test", TANK_DATASET), config=config)

    assert logger.path.exists()
    events = _read_log(logger.path)

    node_starts = {e["node"] for e in events if e["event"] == "node_start"}
    node_ends = {e["node"] for e in events if e["event"] == "node_end"}
    node_errors = [e for e in events if e["event"] == "node_error"]

    for node in ("discover_files", "classify_files", "process_files", "build_indexes"):
        assert node in node_starts, f"missing node_start for {node}"
        assert node in node_ends, f"missing node_end for {node}"

    assert len(node_errors) == 1
    assert node_errors[0]["node"] == "semantic_extraction"
    assert "OPENAI_API_KEY" in node_errors[0]["error"]

    # The failing node must never show up as having "ended" successfully.
    assert "semantic_extraction" not in node_ends
