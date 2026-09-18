"""RunLogger against the real SysML workflow: confirms the deterministic
`build_generation_contract` node logs start/end, and the LLM-dependent
`create_generation_plan` node logs a node_error with its own name attached
when no OPENAI_API_KEY is set — same verified behavior as the Document
Agent's identical module.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from sysml_agent.llm import LLMUnavailable
from sysml_agent.observability import RunLogger
from sysml_agent.workflow.sysml_graph import build_sysml_graph


def _seed_document_agent_semantic_model(document_agent_project_dir: Path) -> None:
    semantic_dir = document_agent_project_dir / "semantic"
    semantic_dir.mkdir(parents=True)
    (semantic_dir / "semantic_model.json").write_text(
        json.dumps(
            {
                "model_version": "v0008", "project_id": "iaq_001",
                "entities": [{"entity_id": "ENT-001", "name": "AHU-01", "type": "AirHandlingUnit", "status": "EXPLICIT", "evidence": ["EV-1"], "aliases": []}],
                "relationships": [], "requirements": [], "behaviors": [], "constraints": [],
                "evidence": [], "conflicts": [], "ambiguities": [], "unknowns": [], "assumptions": [], "decisions": [],
            }
        ),
        encoding="utf-8",
    )


def _read_log(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_run_logger_captures_contract_build_then_the_exact_failing_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    document_agent_project_dir = tmp_path / "document_agent_projects" / "iaq_001"
    sysml_project_dir = tmp_path / "sysml_projects" / "iaq_001"
    _seed_document_agent_semantic_model(document_agent_project_dir)

    logger = RunLogger(sysml_project_dir, run_id="test_run_001")
    graph = build_sysml_graph(
        lambda pid: tmp_path / "document_agent_projects" / pid,
        lambda pid: tmp_path / "sysml_projects" / pid,
    ).compile(checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "iaq_001"}, "callbacks": [logger]}
    initial_state = {
        "project_id": "iaq_001", "generation_id": "gen_0001",
        "entities_in_contract": 0, "requirements_in_contract": 0,
        "mappings_created": 0, "files_generated": 0,
        "validation_status": "", "repair_attempt": 0,
        "sysml_version": "v0001", "status": "PENDING",
    }

    with pytest.raises(LLMUnavailable):
        graph.invoke(initial_state, config=config)

    events = _read_log(logger.path)
    node_starts = {e["node"] for e in events if e["event"] == "node_start"}
    node_ends = {e["node"] for e in events if e["event"] == "node_end"}
    node_errors = [e for e in events if e["event"] == "node_error"]

    assert "build_generation_contract" in node_starts
    assert "build_generation_contract" in node_ends
    assert len(node_errors) == 1
    assert node_errors[0]["node"] == "create_generation_plan"
    assert "OPENAI_API_KEY" in node_errors[0]["error"]
    assert "create_generation_plan" not in node_ends
