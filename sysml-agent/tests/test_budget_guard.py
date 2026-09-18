"""BudgetGuard: the hard spending cap for LLM-driven planning/mapping.

Mirrors the Document Agent's `test_budget_guard.py` — same verified
mechanism (BaseCallbackHandler swallows exceptions raised in its own hooks
unless raise_error=True is set), tested here in isolation and cheaply.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from sysml_agent.observability import BudgetExceeded, BudgetGuard


def _fake_response(prompt_tokens: int, completion_tokens: int) -> SimpleNamespace:
    return SimpleNamespace(
        llm_output={
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            }
        }
    )


def test_raise_error_is_enabled() -> None:
    assert BudgetGuard(limit_usd=2.0).raise_error is True


def test_accumulates_cost_from_token_usage() -> None:
    guard = BudgetGuard(limit_usd=2.0, price_per_1k_input_usd=0.001, price_per_1k_output_usd=0.002)
    guard.on_llm_end(_fake_response(prompt_tokens=1000, completion_tokens=500))
    assert guard.call_count == 1
    assert guard.spent_usd == pytest.approx(0.001 + 0.001)

    guard.on_llm_end(_fake_response(prompt_tokens=1000, completion_tokens=500))
    assert guard.call_count == 2
    assert guard.spent_usd == pytest.approx(0.004)


def test_blocks_the_next_call_once_over_budget() -> None:
    guard = BudgetGuard(limit_usd=0.01, price_per_1k_input_usd=0.01, price_per_1k_output_usd=0.01)

    guard.on_chat_model_start(serialized={}, messages=[])
    guard.on_llm_end(_fake_response(prompt_tokens=1000, completion_tokens=0))  # costs exactly $0.01
    assert guard.spent_usd == pytest.approx(0.01)

    with pytest.raises(BudgetExceeded) as exc_info:
        guard.on_chat_model_start(serialized={}, messages=[])
    assert "0.01" in str(exc_info.value)
    assert "1" in str(exc_info.value)

    with pytest.raises(BudgetExceeded):
        guard.on_llm_start(serialized={}, prompts=[])


def test_settings_default_budget_is_two_dollars(monkeypatch: pytest.MonkeyPatch) -> None:
    from sysml_agent.config import Settings

    monkeypatch.delenv("SYSML_AGENT_BUDGET_USD", raising=False)
    assert Settings.load().llm_budget_usd == pytest.approx(2.0)


def test_settings_budget_is_overridable_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from sysml_agent.config import Settings

    monkeypatch.setenv("SYSML_AGENT_BUDGET_USD", "5.5")
    assert Settings.load().llm_budget_usd == pytest.approx(5.5)


def test_settings_model_defaults_are_real_models(monkeypatch: pytest.MonkeyPatch) -> None:
    # Regression guard for the "gpt-5.1-mini does not exist" bug found live
    # in the Document Agent (see DECISIONS.md) and fixed here before it was
    # ever exercised — this only checks the default isn't the broken name.
    from sysml_agent.config import Settings

    monkeypatch.delenv("SYSML_AGENT_PLANNING_MODEL", raising=False)
    monkeypatch.delenv("SYSML_AGENT_MAPPING_MODEL", raising=False)
    monkeypatch.delenv("SYSML_AGENT_VALIDATION_MODEL", raising=False)
    settings = Settings.load()
    assert settings.planning_model != "gpt-5.1-mini"
    assert settings.mapping_model != "gpt-5.1-mini"
    assert settings.validation_model != "gpt-5.1-mini"
