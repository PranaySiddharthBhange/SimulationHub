"""Local-model (Ollama) infra shared across every stage of this fork.

This fork replaces every OpenAI-backed LLM call with a local model served
by Ollama (`qwen3:8b`, `gemma3:4b`) -- no OpenAI dependency, no API key,
anywhere. Both models share ONE GPU that can only hold one of them at a
time, so every call explicitly unloads the OTHER known model before
invoking one (`keep_alive=0`, verified live to force an immediate evict)
rather than trusting Ollama's own VRAM-dependent default scheduling to
keep it down to one -- that default is real and often does the right
thing on its own (confirmed live), but it isn't a guarantee across every
context-window/VRAM combination, and the one-model-at-a-time constraint
here is a hard hardware limit, not a preference.
"""

from __future__ import annotations

KNOWN_LOCAL_MODELS = ("qwen3:8b", "gemma3:4b")

# Real bug found live (see `extraction/extraction/semantic_extractor.py`'s
# own docstring for the full story): Ollama's default 4096-token context
# window silently truncated a 981-observation document, and the model
# degenerated into garbage output. Fixed at the SOURCE by batching every
# document's observations to at most 80 per extraction call (see
# `semantic_extractor.py::_MAX_OBSERVATIONS_PER_BATCH`) -- which also
# means this no longer needs a huge context window to stay safe.
#
# A second, much bigger real finding on THIS machine's hardware (a 4GB-VRAM
# Quadro T1000): context window size, not model size or structured-output
# method, was the dominant cost. `qwen3:8b`'s KV cache at `num_ctx=32768`
# alone left only ~23% of the model's total memory footprint able to fit
# in VRAM, forcing the rest onto much slower CPU inference -- verified
# live: an identical trivial call's `load_duration` (Ollama's own reported
# metric, not wall-clock guesswork) dropped from 207s at num_ctx=32768 to
# ~7s at num_ctx=8192, a ~30x difference, from this ONE setting alone.
# 8192 is generously sized for an 80-observation batch (comfortably under
# 2500 tokens in practice) with real headroom, not a tight fit.
DEFAULT_NUM_CTX = 8192


class LocalModelUnavailable(RuntimeError):
    """Raised when the local Ollama server can't be reached, or a
    configured model name isn't one of the models actually installed --
    the local-model fork's replacement for the old "no OPENAI_API_KEY"
    check, so a misconfiguration fails fast with a clear message instead
    of a confusing connection error deep inside a LangChain call."""


def ensure_exclusive_model_loaded(model_name: str) -> None:
    """Unloads every OTHER known local model before a call to
    `model_name`. Unconditional (not "only if it was the last one used")
    so this is correct with no state to track, even across separate
    process runs."""

    if model_name not in KNOWN_LOCAL_MODELS:
        raise LocalModelUnavailable(
            f"'{model_name}' is not one of the installed local models {KNOWN_LOCAL_MODELS} -- "
            "check the STAGE_*_MODEL settings in .env."
        )

    import ollama

    client = ollama.Client()
    try:
        currently_loaded = {m["model"] for m in client.ps().get("models", [])}
    except Exception:
        currently_loaded = set()  # best-effort visibility only -- never block the real unload below on this

    for other in KNOWN_LOCAL_MODELS:
        if other == model_name:
            continue
        if other in currently_loaded:
            print(f"    [gpu] unloading {other} to make room for {model_name}...", flush=True)
        try:
            client.generate(model=other, keep_alive=0)
        except Exception:
            pass  # not currently loaded, or Ollama already evicted it -- nothing to do


_TOOL_CALLING_CAPABLE_MODELS = {"qwen3:8b"}


def structured_output_method(model_name: str) -> str:
    """Which `with_structured_output(..., method=...)` value to use, per
    model -- NOT a blanket constant, after a real, decisive live finding:
    `method="json_schema"` (grammar-constrained decoding) genuinely HANGS
    on `qwen3:8b` for a schema shaped like a list of multi-field objects
    with an enum -- confirmed to never complete in a full 10-minute window,
    on a 5-sentence prompt, nothing to do with document size or context
    window. `method="function_calling"` on the IDENTICAL schema/prompt
    completed in 282s with a correct result. `gemma3:4b` has no
    tool-calling capability at all (confirmed via Ollama's own model
    listing), so it must stay on `json_schema` -- there is no universal
    "right" method across both models on this hardware, only a per-model
    one verified to actually work."""

    return "function_calling" if model_name in _TOOL_CALLING_CAPABLE_MODELS else "json_schema"


def check_ollama_available() -> None:
    """Fails fast, with a clear message, if the local Ollama server isn't
    reachable at all -- call this at the same boundary the old
    `OPENAI_API_KEY` check used to guard."""

    import ollama

    try:
        ollama.Client().list()
    except Exception as exc:
        raise LocalModelUnavailable(
            "Local Ollama server is not reachable at http://localhost:11434 -- "
            "start it (`ollama serve`) before running this pipeline."
        ) from exc
