"""Runs the real LangGraph Modelica workflow, confirming it persists the
generation contract and legacy comparison correctly and then fails with a
precise `LLMUnavailable` -- not a confusing crash -- exactly at the model
planner boundary, when no OPENAI_API_KEY is configured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from simulation_platform.modelica_gen.llm import LLMUnavailable
from simulation_platform.modelica_gen.workflow.modelica_graph import build_modelica_graph

from .conftest import seed_upstream_project


def _initial_state() -> dict:
    return {
        "project_id": "tank_001", "generation_id": "gen_0001", "modelica_version": "v0001",
        "components_in_contract": 0, "properties_in_contract": 0,
        "legacy_files_found": 0, "legacy_comparisons_found": 0,
        "mappings_created": 0, "files_generated": 0,
        "validation_status": "", "compile_status": "", "result_validation_status": "", "repair_attempt": 0,
        "validation_error_signature": "", "compile_error_signature": "", "result_validation_error_signature": "",
        "repair_stalled": False,
        "status": "PENDING",
    }


def test_graph_builds_contract_and_legacy_comparison_then_fails_cleanly_without_llm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    document_agent_project_dir, sysml_project_dir = seed_upstream_project(tmp_path)
    modelica_project_dir = tmp_path / "modelica_projects" / "tank_001"

    graph = build_modelica_graph(
        lambda pid: tmp_path / "document_agent_projects" / pid,
        lambda pid: tmp_path / "sysml_projects" / pid,
        lambda pid: tmp_path / "modelica_projects" / pid,
    ).compile(checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "tank_001"}}
    with pytest.raises(LLMUnavailable):
        graph.invoke(_initial_state(), config=config)

    contract_path = modelica_project_dir / "modelica" / "input" / "modelica_generation_contract.json"
    assert contract_path.exists()
    contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract_data["project_id"] == "tank_001"
    assert contract_data["components"] == ["ENT-001"]

    comparison_path = modelica_project_dir / "modelica" / "analysis" / "legacy_comparison.json"
    assert comparison_path.exists()
    comparisons = json.loads(comparison_path.read_text(encoding="utf-8"))
    assert len(comparisons) == 1
    assert comparisons[0]["sysml_element"] == "ENT-001"  # keyed by engineering id, not the SysML name
    assert comparisons[0]["legacy_class"] == "TankDemo_Rev12"

    # Must not have progressed past the plan step.
    assert not (modelica_project_dir / "modelica" / "plan" / "modelica_generation_plan.json").exists()
    assert not (modelica_project_dir / "modelica" / "generated").exists()
