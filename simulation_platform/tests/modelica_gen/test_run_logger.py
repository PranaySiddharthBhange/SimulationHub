"""RunLogger against the real Modelica workflow: confirms both
deterministic nodes (`build_generation_contract`, `analyze_and_compare_
legacy`) log start/end, and the LLM-dependent `create_modelica_plan` node
logs a node_error with its own name attached when no OPENAI_API_KEY is
set -- same verified behavior as the other two agents' identical module.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from simulation_platform.modelica_gen.llm import LLMUnavailable
from simulation_platform.shared import RunLogger
from simulation_platform.modelica_gen.workflow.modelica_graph import build_modelica_graph

from .conftest import seed_upstream_project


def _read_log(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_run_logger_captures_both_deterministic_nodes_then_the_exact_failing_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    document_agent_project_dir, sysml_project_dir = seed_upstream_project(tmp_path)
    modelica_project_dir = tmp_path / "modelica_projects" / "tank_001"

    logger = RunLogger(modelica_project_dir, run_id="test_run_001")
    graph = build_modelica_graph(
        lambda pid: tmp_path / "document_agent_projects" / pid,
        lambda pid: tmp_path / "sysml_projects" / pid,
        lambda pid: tmp_path / "modelica_projects" / pid,
    ).compile(checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "tank_001"}, "callbacks": [logger]}
    initial_state = {
        "project_id": "tank_001", "generation_id": "gen_0001", "modelica_version": "v0001",
        "components_in_contract": 0, "properties_in_contract": 0,
        "legacy_files_found": 0, "legacy_comparisons_found": 0,
        "mappings_created": 0, "files_generated": 0,
        "validation_status": "", "compile_status": "", "result_validation_status": "", "repair_attempt": 0,
        "validation_error_signature": "", "compile_error_signature": "", "result_validation_error_signature": "",
        "repair_stalled": False,
        "status": "PENDING",
    }

    with pytest.raises(LLMUnavailable):
        graph.invoke(initial_state, config=config)

    events = _read_log(logger.path)
    node_starts = {e["node"] for e in events if e["event"] == "node_start"}
    node_ends = {e["node"] for e in events if e["event"] == "node_end"}
    node_errors = [e for e in events if e["event"] == "node_error"]

    assert "build_generation_contract" in node_starts and "build_generation_contract" in node_ends
    assert "analyze_and_compare_legacy" in node_starts and "analyze_and_compare_legacy" in node_ends
    assert len(node_errors) == 1
    assert node_errors[0]["node"] == "create_modelica_plan"
    assert "OPENAI_API_KEY" in node_errors[0]["error"]
    assert "create_modelica_plan" not in node_ends
