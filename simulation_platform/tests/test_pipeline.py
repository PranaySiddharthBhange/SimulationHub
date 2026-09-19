"""Resumability (`new direction.txt` §30-31): skip a stage rerun when its
input hasn't actually changed since the last completed run. The skip
decision happens BEFORE any graph is built/invoked, so this is fully
testable without OPENAI_API_KEY -- confirmed here by checking that a
"should rerun" case reaches (and fails at) the real LLM boundary, while a
"should skip" case never gets that far at all.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pytest
from langgraph.graph import END, START, StateGraph

from simulation_platform import pipeline
from simulation_platform.extraction.extraction.llm import ExtractionUnavailable
from simulation_platform.shared import BudgetGuard
from simulation_platform.workspace import ProjectState, StageState, Workspace, compute_hash


def _seed_project(tmp_path: Path, project_id: str) -> Path:
    ws = Workspace(tmp_path)
    docs_dir = ws.documents_dir(project_id)
    docs_dir.mkdir(parents=True)
    (docs_dir / "a.txt").write_text("hello", encoding="utf-8")
    ws.ensure_layout(project_id)
    return ws.project_dir(project_id)


def test_compute_hash_is_stable_and_content_sensitive(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    a.write_text("hello", encoding="utf-8")

    first = compute_hash(a)
    assert compute_hash(a) == first  # stable across repeated calls

    a.write_text("hello, world", encoding="utf-8")
    assert compute_hash(a) != first  # content change -> different hash


def test_compute_hash_ignores_touch_only_changes(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    a.write_text("hello", encoding="utf-8")
    before = compute_hash(a)
    a.touch()  # mtime changes, content doesn't
    assert compute_hash(a) == before


def test_execute_stage_1_skips_when_input_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    project_id = "tank_test"
    ws = Workspace(tmp_path)
    _seed_project(tmp_path, project_id)

    matching_hash = compute_hash(ws.documents_dir(project_id), ws.problem_path(project_id))
    ws.save_state(
        ProjectState(
            project_id=project_id,
            stage_1=StageState(status="completed", input_hash=matching_hash),
        )
    )

    result = pipeline.execute_stage_1(project_id, projects_root=tmp_path)

    assert result.status == "READY"
    assert result.details.get("skipped") is True


def test_execute_stage_1_reruns_when_input_changed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    project_id = "tank_test"
    ws = Workspace(tmp_path)
    _seed_project(tmp_path, project_id)

    ws.save_state(
        ProjectState(
            project_id=project_id,
            stage_1=StageState(status="completed", input_hash="stale-hash-does-not-match-anything"),
        )
    )

    # Not skipped -> actually attempts the real (deterministic) pipeline and
    # reaches the genuine LLM boundary, which fails cleanly without a key --
    # proof it didn't just short-circuit.
    with pytest.raises(ExtractionUnavailable):
        pipeline.execute_stage_1(project_id, projects_root=tmp_path)


def test_execute_stage_1_force_reruns_even_when_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    project_id = "tank_test"
    ws = Workspace(tmp_path)
    _seed_project(tmp_path, project_id)

    matching_hash = compute_hash(ws.documents_dir(project_id), ws.problem_path(project_id))
    ws.save_state(
        ProjectState(
            project_id=project_id,
            stage_1=StageState(status="completed", input_hash=matching_hash),
        )
    )

    with pytest.raises(ExtractionUnavailable):
        pipeline.execute_stage_1(project_id, force=True, projects_root=tmp_path)


class _ResumeState(TypedDict):
    calls: int
    status: str


def test_execute_graph_stage_resumes_after_a_crash_without_rerunning_completed_nodes(tmp_path: Path) -> None:
    """The real bug this fixes: with only an in-memory checkpointer, a crash
    partway through a graph (e.g. a real `BudgetGuard` cutoff) left a retry
    with no way to know earlier nodes already ran -- it re-ran (and
    re-paid for) all of them. Proven here with a tiny 2-node graph where
    the SECOND node fails on its first invocation ("simulated crash") --
    the retry (same `input_hash`) must resume from the checkpoint after
    node "a", never calling it again."""

    ws = Workspace(tmp_path)
    project_id = "resume_test"
    ws.ensure_layout(project_id)

    call_log: list[str] = []
    attempts = {"b": 0}

    def node_a(state: _ResumeState) -> dict:
        call_log.append("a")
        return {"calls": state["calls"] + 1}

    def node_b(state: _ResumeState) -> dict:
        attempts["b"] += 1
        if attempts["b"] == 1:
            raise RuntimeError("simulated crash")
        call_log.append("b")
        return {"status": "READY"}

    graph = StateGraph(_ResumeState)
    graph.add_node("a", node_a)
    graph.add_node("b", node_b)
    graph.add_edge(START, "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", END)

    guard = BudgetGuard(limit_usd=1000.0, price_per_1k_input_usd=0.0, price_per_1k_output_usd=0.0, stage_name="test")
    initial_state: _ResumeState = {"calls": 0, "status": "PENDING"}
    input_hash = "hash-1"

    with pytest.raises(RuntimeError, match="simulated crash"):
        pipeline._execute_graph_stage(
            ws, project_id, "stage_1", "resume-thread", graph, initial_state, guard, lambda p: None,
            input_hash, force=False,
        )
    assert call_log == ["a"]  # node "a" completed and was checkpointed before the crash

    result = pipeline._execute_graph_stage(
        ws, project_id, "stage_1", "resume-thread", graph, initial_state, guard, lambda p: None,
        input_hash, force=False,
    )
    assert call_log == ["a", "b"]  # resumed -- "a" was NOT re-run
    assert result["status"] == "READY"


def test_execute_graph_stage_restarts_when_input_hash_differs_from_the_abandoned_attempt(tmp_path: Path) -> None:
    """A crashed attempt's checkpoint belongs to a SPECIFIC input -- if the
    input changed since then (or `force=True`), resuming into it would
    silently continue a run for stale data. Must discard and restart
    fresh, re-running every node including "a"."""

    ws = Workspace(tmp_path)
    project_id = "resume_test_2"
    ws.ensure_layout(project_id)

    call_log: list[str] = []
    attempts = {"b": 0}

    def node_a(state: _ResumeState) -> dict:
        call_log.append("a")
        return {"calls": state["calls"] + 1}

    def node_b(state: _ResumeState) -> dict:
        attempts["b"] += 1
        if attempts["b"] == 1:
            raise RuntimeError("simulated crash")
        call_log.append("b")
        return {"status": "READY"}

    graph = StateGraph(_ResumeState)
    graph.add_node("a", node_a)
    graph.add_node("b", node_b)
    graph.add_edge(START, "a")
    graph.add_edge("a", "b")
    graph.add_edge("b", END)

    guard = BudgetGuard(limit_usd=1000.0, price_per_1k_input_usd=0.0, price_per_1k_output_usd=0.0, stage_name="test")
    initial_state: _ResumeState = {"calls": 0, "status": "PENDING"}

    with pytest.raises(RuntimeError, match="simulated crash"):
        pipeline._execute_graph_stage(
            ws, project_id, "stage_1", "resume-thread-2", graph, initial_state, guard, lambda p: None,
            "hash-old", force=False,
        )
    assert call_log == ["a"]

    result = pipeline._execute_graph_stage(
        ws, project_id, "stage_1", "resume-thread-2", graph, initial_state, guard, lambda p: None,
        "hash-new", force=False,
    )
    assert call_log == ["a", "a", "b"]  # restarted -- "a" ran again, not resumed
    assert result["status"] == "READY"
