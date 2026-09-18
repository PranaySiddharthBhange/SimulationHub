"""Hard spending cap for LLM-driven planning/mapping — an operational
safety guard, not something the spec calls for. Identical mechanism to the
Document Agent's `observability/budget_guard.py` (same verified behavior,
mirrored here rather than shared as a package, consistent with how these
two agents stay decoupled — see `Agent Contracts.md`).

Built on the same callback mechanism as `run_logger.py`, with one critical
difference verified empirically before relying on it: `BaseCallbackHandler`
swallows exceptions raised inside its hooks by default
(`raise_error = False`) and only logs a warning — the guarded LLM call
would proceed anyway. Setting `raise_error = True` is required for a
callback's exception to actually propagate and abort the call; confirmed
against a real `ChatOpenAI.invoke()` (with a deliberately bogus API key, to
prove the block happens before any network request, not after one fails).

Also confirmed empirically: `ChatOpenAI` fires `on_chat_model_start`, not
`on_llm_start` — both are overridden here so the guard works regardless of
which LLM type is ever used. And callbacks attached at `graph.invoke(...,
config={"callbacks": [...]})` propagate automatically (via context vars)
into a nested `model.invoke(...)` call several function calls deep, with
no explicit config threading required.

Pricing note: token prices below are a documented placeholder, not
authoritative billing data — override via the constructor or the
`SYSML_AGENT_PRICE_PER_1K_*` env vars if you know your account's actual
rates. Deliberately erring slightly high, so the cap trips a little early
rather than a little late.
"""

from __future__ import annotations

import threading

from langchain_core.callbacks import BaseCallbackHandler

DEFAULT_PRICE_PER_1K_INPUT_USD = 0.00025
DEFAULT_PRICE_PER_1K_OUTPUT_USD = 0.001


class BudgetExceeded(RuntimeError):
    """Raised when the configured LLM budget has been spent."""


class BudgetGuard(BaseCallbackHandler):
    raise_error = True  # required — see module docstring.

    def __init__(
        self,
        limit_usd: float,
        price_per_1k_input_usd: float = DEFAULT_PRICE_PER_1K_INPUT_USD,
        price_per_1k_output_usd: float = DEFAULT_PRICE_PER_1K_OUTPUT_USD,
    ):
        self.limit_usd = limit_usd
        self.price_per_1k_input_usd = price_per_1k_input_usd
        self.price_per_1k_output_usd = price_per_1k_output_usd
        self._lock = threading.Lock()
        self.spent_usd = 0.0
        self.call_count = 0

    def _check(self) -> None:
        with self._lock:
            spent, calls = self.spent_usd, self.call_count
        if spent >= self.limit_usd:
            raise BudgetExceeded(
                f"LLM budget exceeded: ${spent:.4f} spent (estimated) >= "
                f"${self.limit_usd:.2f} limit, after {calls} LLM calls. "
                "Stopping before making another call."
            )

    def on_llm_start(self, serialized, prompts, **kwargs) -> None:
        self._check()

    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
        self._check()

    def on_llm_end(self, response, **kwargs) -> None:
        usage = (response.llm_output or {}).get("token_usage") or {}
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        cost = (
            (prompt_tokens / 1000) * self.price_per_1k_input_usd
            + (completion_tokens / 1000) * self.price_per_1k_output_usd
        )
        with self._lock:
            self.spent_usd += cost
            self.call_count += 1
