"""Local Ollama model support.

All local calls use `gemma3:4b`. Availability and model validation remain
centralized here so every local stage uses the same runtime rules.
"""

from __future__ import annotations

KNOWN_LOCAL_MODELS = ("gemma3:4b",)

# A live test on this 4 GB VRAM machine showed context size was the dominant
# inference cost: a 32768-token KV cache forced most model work onto the CPU,
# while 8192 kept enough headroom for the existing bounded extraction calls.
DEFAULT_NUM_CTX = 8192


class LocalModelUnavailable(RuntimeError):
    """Raised when Ollama is unavailable or the configured model is absent."""


def ensure_exclusive_model_loaded(model_name: str) -> None:
    """Validate the configured local model and unload any known alternative."""
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
        currently_loaded = set()

    for other in KNOWN_LOCAL_MODELS:
        if other == model_name:
            continue
        if other in currently_loaded:
            print(f"    [gpu] unloading {other} to make room for {model_name}...", flush=True)
        try:
            client.generate(model=other, keep_alive=0)
        except Exception:
            pass


_TOOL_CALLING_CAPABLE_MODELS: set[str] = set()


def structured_output_method(model_name: str) -> str:
    """Gemma has no tool-calling support, so structured calls use JSON schema."""
    return "function_calling" if model_name in _TOOL_CALLING_CAPABLE_MODELS else "json_schema"


def check_ollama_available() -> None:
    """Fail clearly when the local Ollama server cannot be reached."""
    import ollama

    try:
        ollama.Client().list()
    except Exception as exc:
        raise LocalModelUnavailable(
            "Local Ollama server is not reachable at http://localhost:11434 -- "
            "start it (`ollama serve`) before running this pipeline."
        ) from exc
