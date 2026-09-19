"""Deterministic-only tests for `parameter_value_suggester.py` -- the
LLM call itself (`run_structured`) isn't exercised (needs OPENAI_API_KEY,
see `test_graph_boundary.py` for that kind of boundary test); this covers
the plumbing that runs BEFORE that call: never calling the LLM at all when
there's nothing to refine, and never touching an already-`grounded` entry.
"""

from __future__ import annotations

import pytest

from simulation_platform.modelica_gen.llm import LLMUnavailable
from simulation_platform.modelica_gen.mapping.parameter_value_suggester import suggest_parameter_values


def test_suggest_parameter_values_skips_the_llm_call_when_everything_is_already_grounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    decisions = [
        {"class_name": "Controller1", "variable": "startCmd", "suggested_value": "true", "reason": "...", "grounded": True},
    ]

    # No API key AND no LLM call attempted -- would raise if it tried.
    result = suggest_parameter_values(decisions, {"requirements": []})

    assert result == decisions


def test_suggest_parameter_values_reaches_the_real_llm_boundary_when_something_needs_refining(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    decisions = [
        {"class_name": "Valve1", "variable": "valve1.opening", "suggested_value": "1.0", "reason": "...", "grounded": False},
    ]

    with pytest.raises(LLMUnavailable):
        suggest_parameter_values(decisions, {"requirements": []}, legacy_files={"a.mo": "model A end A;"})
