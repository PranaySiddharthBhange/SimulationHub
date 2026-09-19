"""Found live on a real Windows test run: `simulation-platform index`
completed the ENTIRE Stage 1 pipeline successfully, then crashed with
`UnicodeEncodeError` trying to print its own "✓" result marker, because
Windows' default console codepage (cp1252) can't encode it. The real
pipeline work was never at risk -- only the CLI's own result printout.
"""

from __future__ import annotations

import io
import sys

import pytest

from simulation_platform.cli import InteractiveInputUnavailable, _ensure_utf8_streams, _interactive_on_interrupt, _print_stage_result
from simulation_platform.pipeline import StageResult


def test_ensure_utf8_streams_lets_a_checkmark_print_on_a_cp1252_console(monkeypatch: pytest.MonkeyPatch) -> None:
    raw_stdout = io.BytesIO()
    cp1252_stdout = io.TextIOWrapper(raw_stdout, encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", cp1252_stdout)
    monkeypatch.setattr(sys, "stderr", cp1252_stdout)

    # Without the fix, this next line raises UnicodeEncodeError -- the
    # exact crash seen live, after Stage 1 had already fully succeeded.
    _ensure_utf8_streams()
    _print_stage_result(StageResult(stage="stage_1", project_id="p", status="READY", details={}))
    cp1252_stdout.flush()

    assert "stage_1: READY" in raw_stdout.getvalue().decode("utf-8")


def test_print_stage_result_shows_a_cross_for_a_non_ready_status(capsys: pytest.CaptureFixture) -> None:
    _print_stage_result(StageResult(stage="stage_2", project_id="p", status="NEEDS_REVIEW", details={}))
    out = capsys.readouterr().out
    assert "stage_2: NEEDS_REVIEW" in out
    assert "✗" in out


def test_human_review_acknowledgment_survives_eof_on_non_interactive_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture,
) -> None:
    """Found live: running a stage non-interactively (stdin has no real
    terminal) crashed with a raw `EOFError` traceback right after the
    real work had already finished and only needed acknowledgment --
    nothing is actually decided by this prompt, so EOF is safe to treat
    as "proceed"."""

    monkeypatch.setattr("builtins.input", lambda *_: (_ for _ in ()).throw(EOFError()))
    handle = _interactive_on_interrupt("p")

    result = handle({"validation_report_path": None})

    # Never a bare `None` -- a real `langgraph` 1.2.11 bug crashes on
    # `Command(resume=None)` (see cli.py's own note on this); the actual
    # value is discarded by `human_review_node` either way.
    assert result == "acknowledged"
    assert "no interactive terminal available" in capsys.readouterr().out


def test_pending_value_decision_raises_a_clean_error_on_non_interactive_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unlike plain acknowledgment, this DOES decide something real (was
    a proposed value confirmed?) -- silently auto-accepting on EOF would
    rubber-stamp exactly the kind of unconfirmed value `new direction.txt`
    §15 says must never be applied without a real human answer, so this
    must fail loudly and cleanly instead."""

    monkeypatch.setattr("builtins.input", lambda *_: (_ for _ in ()).throw(EOFError()))
    handle = _interactive_on_interrupt("p")

    with pytest.raises(InteractiveInputUnavailable):
        handle({"pending_value_decisions": [{"class_name": "C", "variable": "x", "reason": "r", "suggested_value": "0.0"}]})
