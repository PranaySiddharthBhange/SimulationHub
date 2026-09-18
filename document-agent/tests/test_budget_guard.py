"""BudgetGuard: the hard spending cap for LLM-driven extraction.

Two things are worth testing deliberately, not just trusting the design:
1. Cost actually accumulates from token usage the way `on_llm_end` reports it.
2. Once accumulated cost crosses the limit, the *next* call is blocked
   before it happens — verified end-to-end against a real `ChatOpenAI`
   (with a deliberately bogus key) in `test_run_logger.py`'s sibling
   exploration; this file covers the guard's own accounting logic in
   isolation, cheaply and deterministically.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from engineering_agent.observability import BudgetExceeded, BudgetGuard


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
    # BaseCallbackHandler swallows exceptions raised inside its hooks unless
    # raise_error=True — confirmed empirically against a real ChatOpenAI call.
    # If this ever regresses back to False, the guard silently stops guarding.
    assert BudgetGuard(limit_usd=2.0).raise_error is True


def test_accumulates_cost_from_token_usage() -> None:
    guard = BudgetGuard(limit_usd=2.0, price_per_1k_input_usd=0.001, price_per_1k_output_usd=0.002)
    guard.on_llm_end(_fake_response(prompt_tokens=1000, completion_tokens=500))
    assert guard.call_count == 1
    assert guard.spent_usd == pytest.approx(0.001 + 0.001)  # 1000/1000*0.001 + 500/1000*0.002

    guard.on_llm_end(_fake_response(prompt_tokens=1000, completion_tokens=500))
    assert guard.call_count == 2
    assert guard.spent_usd == pytest.approx(0.004)


def test_blocks_the_next_call_once_over_budget() -> None:
    guard = BudgetGuard(limit_usd=0.01, price_per_1k_input_usd=0.01, price_per_1k_output_usd=0.01)

    # First call: under budget, start-hook must not raise.
    guard.on_chat_model_start(serialized={}, messages=[])
    guard.on_llm_end(_fake_response(prompt_tokens=1000, completion_tokens=0))  # costs exactly $0.01
    assert guard.spent_usd == pytest.approx(0.01)

    # Second call: already at the limit — must block before it happens.
    with pytest.raises(BudgetExceeded) as exc_info:
        guard.on_chat_model_start(serialized={}, messages=[])
    assert "0.01" in str(exc_info.value)
    assert "1" in str(exc_info.value)  # call_count so far, in the error message

    # on_llm_start (non-chat models) must be blocked the same way.
    with pytest.raises(BudgetExceeded):
        guard.on_llm_start(serialized={}, prompts=[])


def test_settings_default_budget_is_two_dollars(monkeypatch: pytest.MonkeyPatch) -> None:
    from engineering_agent.config.settings import Settings

    monkeypatch.delenv("ENGINEERING_AGENT_BUDGET_USD", raising=False)
    assert Settings.load().extraction_budget_usd == pytest.approx(2.0)


def test_settings_budget_is_overridable_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from engineering_agent.config.settings import Settings

    monkeypatch.setenv("ENGINEERING_AGENT_BUDGET_USD", "5.5")
    assert Settings.load().extraction_budget_usd == pytest.approx(5.5)
