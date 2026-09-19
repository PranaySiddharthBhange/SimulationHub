"""BudgetGuard: the hard spending cap for LLM-driven planning/mapping.

Mirrors the other two agents' `test_budget_guard.py` -- same verified
mechanism (BaseCallbackHandler swallows exceptions raised in its own hooks
unless raise_error=True is set), tested here in isolation and cheaply.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from simulation_platform.shared import BudgetExceeded, BudgetGuard


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
    # Targets `PlatformSettings.stage3_budget_usd` directly, not the
    # stage-local `modelica_gen.config.Settings` -- that dataclass used to
    # mirror this same value in a field (`llm_budget_usd`) nothing ever
    # actually read; removed in this session's dead-config cleanup (see
    # its own docstring). Real Stage 3 budget enforcement (`pipeline.py`'s
    # `_stage_budget_guard`) always reads this field.
    from simulation_platform.config import PlatformSettings

    # Also clear the PRIMARY name, not just the legacy fallback -- found
    # live: a real `.env` on disk (needed for an actual Stage 3 test run)
    # legitimately set `STAGE_3_BUDGET_USD=4.0`, and since `python-dotenv`
    # loads `.env` straight into `os.environ`, this test's assumption of a
    # clean default was silently false in that environment. This test
    # verifies the DEFAULT specifically, so it must isolate itself from
    # whatever the real `.env` happens to say, not just the deprecated name.
    monkeypatch.delenv("MODELICA_AGENT_BUDGET_USD", raising=False)
    monkeypatch.delenv("STAGE_3_BUDGET_USD", raising=False)
    assert PlatformSettings.load().stage3_budget_usd == pytest.approx(2.0)


def test_settings_budget_is_overridable_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from simulation_platform.config import PlatformSettings

    monkeypatch.setenv("TOTAL_BUDGET_USD", "100")
    monkeypatch.setenv("MODELICA_AGENT_BUDGET_USD", "5.5")
    assert PlatformSettings.load().stage3_budget_usd == pytest.approx(5.5)


def test_settings_model_defaults_are_real_models(monkeypatch: pytest.MonkeyPatch) -> None:
    # Regression guard for the "gpt-5.1-mini does not exist" bug found live
    # in the Document Agent (see DECISIONS.md) and fixed pre-emptively here.
    from simulation_platform.modelica_gen.config import Settings

    monkeypatch.delenv("MODELICA_AGENT_PLANNING_MODEL", raising=False)
    monkeypatch.delenv("MODELICA_AGENT_MAPPING_MODEL", raising=False)
    monkeypatch.delenv("MODELICA_AGENT_VALIDATION_MODEL", raising=False)
    settings = Settings.load()
    assert settings.planning_model != "gpt-5.1-mini"
    assert settings.mapping_model != "gpt-5.1-mini"
    assert settings.validation_model != "gpt-5.1-mini"
