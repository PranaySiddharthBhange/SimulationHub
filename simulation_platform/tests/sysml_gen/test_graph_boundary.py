"""Runs the real LangGraph SysML workflow, confirming it persists the
generation contract correctly and then fails with a precise `LLMUnavailable`
— not a confusing crash — exactly at the model-planner boundary, when no
OPENAI_API_KEY is configured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from simulation_platform.sysml_gen.llm import LLMUnavailable
from simulation_platform.sysml_gen.workflow.sysml_graph import build_sysml_graph


def _seed_document_agent_semantic_model(document_agent_project_dir: Path) -> None:
    extracted_dir = document_agent_project_dir / "workspace" / "extracted"
    extracted_dir.mkdir(parents=True)
    (extracted_dir / "project_knowledge.json").write_text(
        json.dumps(
            {
                "model_version": "v0008",
                "project_id": "iaq_001",
                "entities": [
                    {"entity_id": "ENT-001", "name": "AHU-01", "type": "AirHandlingUnit", "status": "EXPLICIT", "evidence": ["EV-1"], "aliases": []}
                ],
                "relationships": [],
                "requirements": [
                    {
                        "requirement_id": "REQ-001", "subject": "Zone-01", "property": "CO2", "operator": "<=",
                        "value": None, "min": None, "max": 1000, "unit": "ppm", "condition": None,
                        "status": "CONFIRMED", "evidence": ["EV-1"],
                    }
                ],
                "behaviors": [], "constraints": [],
                "evidence": [
                    {"evidence_id": "EV-1", "fact_id": "REQ-001", "type": "EXPLICIT_TEXT", "document_id": "doc_001", "location": {"page": 8}, "quote": "CO2 <= 1000 ppm"}
                ],
                "conflicts": [], "ambiguities": [], "unknowns": [], "assumptions": [], "decisions": [],
            }
        ),
        encoding="utf-8",
    )


def test_graph_builds_contract_then_fails_cleanly_without_llm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    document_agent_project_dir = tmp_path / "document_agent_projects" / "iaq_001"
    sysml_project_dir = tmp_path / "sysml_projects" / "iaq_001"
    _seed_document_agent_semantic_model(document_agent_project_dir)

    graph = build_sysml_graph(
        lambda pid: tmp_path / "document_agent_projects" / pid,
        lambda pid: tmp_path / "sysml_projects" / pid,
    ).compile(checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "iaq_001"}}
    initial_state = {
        "project_id": "iaq_001",
        "generation_id": "gen_0001",
        "entities_in_contract": 0,
        "requirements_in_contract": 0,
        "mappings_created": 0,
        "files_generated": 0,
        "validation_status": "",
        "repair_attempt": 0,
        "validation_error_signature": "",
        "repair_stalled": False,
        "sysml_version": "v0001",
        "status": "PENDING",
    }

    with pytest.raises(LLMUnavailable):
        graph.invoke(initial_state, config=config)

    contract_path = sysml_project_dir / "sysml" / "input" / "generation_contract.json"
    assert contract_path.exists()
    contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract_data["project_id"] == "iaq_001"
    assert len(contract_data["entities"]) == 1
    assert len(contract_data["requirements"]) == 1

    # Must not have progressed past the contract-build step.
    assert not (sysml_project_dir / "sysml" / "plan" / "generation_plan.json").exists()
    assert not (sysml_project_dir / "sysml" / "generated").exists()
