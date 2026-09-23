"""The Reasoner: one model client used by every stage in `reasoner_pipeline.py`.

Stage-specific prompts live in `skills/` (each extends `prompts.common.COMMON`);
this module only holds the client that sends them -- local via Ollama for Stage 1,
OpenAI for consolidation/Stage 2/Stage 3 (see `backend=` on `Reasoner.__init__`).
"""

from __future__ import annotations

import os
from typing import TypeVar

from pydantic import BaseModel

from simulation_platform.config import PlatformSettings
from simulation_platform.utils.local_models import (
    check_ollama_available,
    ensure_exclusive_model_loaded,
    structured_output_method,
)
from simulation_platform.utils.progress import log_llm_call
from simulation_platform.utils.run_log import RunLog
from simulation_platform.sources import Packet

T = TypeVar("T", bound=BaseModel)


def _estimate_num_ctx(prompt: str, content: list[dict]) -> int:
    """A fixed `num_ctx` doesn't fit this architecture -- unlike the
    per-batch pipeline (bounded to <=80 observations per call), `Reasoner`
    sends an ENTIRE project's document set in one Stage 1 call, whose size
    varies enormously by project. Found live: the tank dataset's full
    packet needed 17023 tokens, well past the shared per-batch
    `DEFAULT_NUM_CTX=8192`. Estimates from actual character count (~3
    chars/token, a conservative overestimate -- safe direction to be wrong
    in) rather than guessing one fixed number, rounded up to a 4096
    multiple with a floor (small requests still get real headroom) and a
    ceiling (this GPU's VRAM math means bigger isn't free -- see
    `utils/local_models.py`'s own docstring for the live-measured
    30x-load-time-difference lesson)."""

    total_chars = len(prompt) + sum(
        len(block.get("text", "")) for block in content if isinstance(block.get("text"), str)
    )
    estimated_tokens = total_chars // 3 + 2048  # + buffer for response + system overhead
    return max(8192, min(40960, -(-estimated_tokens // 4096) * 4096))  # ceil-round to a 4096 multiple


def _to_chat_content(blocks: list[dict]) -> list[dict]:
    """`Packet.content()` renders Responses-API-shaped blocks
    (`input_text`/`input_image`) -- translate to the Chat-style blocks
    `ChatOllama` expects (`text`/`image_url`, confirmed live to accept the
    exact same `image_url` shape the OpenAI-backed code already used)."""

    converted = []
    for block in blocks:
        if block["type"] == "input_text":
            converted.append({"type": "text", "text": block["text"]})
        elif block["type"] == "input_image":
            converted.append({"type": "image_url", "image_url": {"url": block["image_url"]}})
    return converted


def _with_transient_retry(call, *args, attempts: int = 3, backoff: float = 2.0):
    """Retry an OpenAI call through a transient network failure.

    A stage's repair loop has a small, fixed number of attempts against the real
    compiler, and each one is a full generation. Found live: a bare
    `APIConnectionError` consumed the last Stage 3 attempt and failed the whole
    stage while the model itself was making real progress. A dropped connection
    is not a modelling error, so it must not cost a modelling attempt.
    """

    import time as _time

    for attempt in range(attempts):
        try:
            return call(*args)
        except Exception as exc:  # noqa: BLE001 -- re-raised below unless transient
            name = type(exc).__name__
            transient = (
                "Connection" in name or "Timeout" in name or "RateLimit" in name
                or "InternalServer" in name or "APIStatus" in name
            )
            if not transient or attempt == attempts - 1:
                raise
            delay = backoff * (2 ** attempt)
            print(f"    [Reasoner] transient {name}, retrying in {delay:.0f}s "
                  f"({attempt + 2}/{attempts})", flush=True)
            _time.sleep(delay)


class OpenAIUnavailable(RuntimeError):
    """Raised when an OpenAI-backed stage is invoked without OPENAI_API_KEY
    configured -- fails clean, never silently falls back to a local model
    for a stage the caller asked to run on OpenAI."""


class Reasoner:
    def __init__(self, settings: PlatformSettings, stage: int, backend: str = "ollama",
                 model_override: str | None = None, run_log: RunLog | None = None):
        self.settings, self.stage, self.backend = settings, stage, backend
        self.run_log = run_log
        self.spent = 0.0
        self.calls = 0
        self.limit = getattr(settings, f"stage{stage}_budget_usd")
        if backend == "openai":
            self.model = model_override or settings.openai_model
        else:
            # Vision is deliberately OFF for now (user's explicit choice,
            # found live: a vision call on a 2-image document took 320s vs.
            # seconds for text-only calls) --
            # `reasoner_pipeline.py::_understand_documents` never attaches
            # an image to any packet it builds, so Stage 1 no longer needs
            # the vision-capable model either. `gemma3:4b` everywhere, per
            # the user's standing choice; `settings.stage1_vision_model`
            # (`gemma3:4b`) is kept configured, unused, in case vision is
            # turned back on later rather than deleted.
            self.model = {1: settings.stage1_extraction_model, 2: settings.stage2_mapping_model,
                          3: settings.stage3_mapping_model}[stage]

    def _record_openai_usage(self, message) -> tuple[int, int, float]:
        """Record the configured best-effort API cost for one raw AI message."""
        if self.backend != "openai":
            return 0, 0, 0.0
        usage = getattr(message, "usage_metadata", None) or {}
        input_tokens = int(usage.get("input_tokens", 0) or 0)
        output_tokens = int(usage.get("output_tokens", 0) or 0)
        call_spent = (
            (input_tokens / 1000) * self.settings.price_per_1k_input_usd
            + (output_tokens / 1000) * self.settings.price_per_1k_output_usd
        )
        self.spent += call_spent
        return input_tokens, output_tokens, call_spent

    def _build_model(self, prompt: str, content: list[dict]):
        """Returns a constructed, backend-appropriate chat model -- the ONE
        place `ask()`/`ask_free_text()` branch on `self.backend`, so
        neither has to duplicate this logic."""

        if self.backend == "openai":
            if not self.settings.openai_api_key:
                raise OpenAIUnavailable(
                    f"Stage {self.stage} is configured to use OpenAI but OPENAI_API_KEY is not set -- "
                    "add it to .env before running this stage."
                )
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=self.model, api_key=self.settings.openai_api_key, temperature=0)

        from langchain_ollama import ChatOllama

        check_ollama_available()
        # The GPU can only hold one of the two installed models at a time.
        ensure_exclusive_model_loaded(self.model)
        num_ctx = _estimate_num_ctx(prompt, content)
        return ChatOllama(model=self.model, temperature=0, num_ctx=num_ctx)

    def ask(self, prompt: str, context: str, schema: type[T], packet: Packet,
            input_tables: set[str] | None = None) -> T:
        if self.spent >= self.limit:
            raise RuntimeError(f"Stage {self.stage} estimated budget exhausted (${self.spent:.4f}).")

        content = _to_chat_content(packet.content(input_tables, int(os.environ.get("MAX_CONTEXT_CHARS", "300000"))))
        content.append({"type": "text", "text": context})

        model = self._build_model(prompt, content)
        # OpenAI's strict `json_schema` structured-outputs mode rejects a
        # Pydantic schema with any optional/defaulted field ("required" must
        # list EVERY property) -- `function_calling` doesn't share that issue.
        # Ollama's own per-model choice (`structured_output_method`) is
        # unrelated and doesn't apply here.
        method = "function_calling" if self.backend == "openai" else structured_output_method(self.model)
        log_llm_call(f"Stage {self.stage}", self.model, schema.__name__)
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": content}]
        if self.backend == "openai":
            wrapped = _with_transient_retry(
                model.with_structured_output(schema, method=method, include_raw=True).invoke, messages,
            )
            result = wrapped.get("parsed")
            if result is None:
                raise wrapped.get("parsing_error") or RuntimeError("OpenAI returned no parsed structured result")
            input_tokens, output_tokens, call_spent = self._record_openai_usage(wrapped.get("raw"))
        else:
            structured_model = model.with_structured_output(schema, method=method)
            result = structured_model.invoke(messages)
            input_tokens, output_tokens, call_spent = 0, 0, 0.0
        self.calls += 1
        if self.run_log is not None:
            self.run_log.event(
                "llm_call", stage=self.stage, backend=self.backend, model=self.model,
                schema=schema.__name__, input_tokens=input_tokens, output_tokens=output_tokens,
                call_spent_usd=round(call_spent, 6), cumulative_spent_usd=round(self.spent, 6),
            )
        return result  # type: ignore[return-value]

    def ask_free_text(self, prompt: str, context: str, packet: Packet) -> str:
        """Same plumbing as `ask()`, but no response schema at all -- plain
        text out. Used for Stage 1's per-document/per-chunk understanding
        (see `reasoner_pipeline.py`): one document (or one page-sized chunk
        of a large one) per call, so no call's context ever needs to hold
        more than a single document's worth of content."""

        if self.spent >= self.limit:
            raise RuntimeError(f"Stage {self.stage} estimated budget exhausted (${self.spent:.4f}).")

        content = _to_chat_content(packet.content())
        content.append({"type": "text", "text": context})

        model = self._build_model(prompt, content)
        log_llm_call(f"Stage {self.stage}", self.model, "free text")
        result = _with_transient_retry(
            model.invoke, [{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        )
        input_tokens, output_tokens, call_spent = self._record_openai_usage(result)
        self.calls += 1
        if self.run_log is not None:
            self.run_log.event(
                "llm_call", stage=self.stage, backend=self.backend, model=self.model,
                schema="free text", input_tokens=input_tokens, output_tokens=output_tokens,
                call_spent_usd=round(call_spent, 6), cumulative_spent_usd=round(self.spent, 6),
            )
        return result.content
