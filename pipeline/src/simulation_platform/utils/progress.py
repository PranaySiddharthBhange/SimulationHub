"""Real-time, human-facing progress printing -- separate from `RunLog`
(`utils/run_log.py`, which writes a structured JSONL trail to disk for
later inspection). Local models are slow enough per call that a run can
sit silent for many minutes with zero visible output; this exists so a
person watching the terminal can actually see which node/stage/model is
active right now, not just infer it from CPU usage or wait for the whole
thing to finish.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Callable


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def traced_node(stage_label: str, node_name: str, func: Callable[[dict], dict]) -> Callable[[dict], dict]:
    """Wraps a LangGraph node function so entering/leaving it prints a
    visible, timestamped marker (including how long the node actually
    took) -- essential for answering "how much longer will this take" from
    the log itself, not a guess. Applied at `graph.add_node(name,
    traced_node(...))` call sites rather than inside every node body -- one
    wrapper, every node covered, nothing to forget when a new node is
    added later."""

    def wrapped(state: dict) -> dict:
        started = time.monotonic()
        print(f"\n=== [{_now()}] [{stage_label}] {node_name} ===", flush=True)
        result = func(state)
        elapsed = time.monotonic() - started
        print(f"--- [{_now()}] [{stage_label}] {node_name} done in {elapsed:.1f}s: {result} ---", flush=True)
        return result

    return wrapped


def log_llm_call(stage_label: str, model_name: str, purpose: str) -> None:
    """Printed immediately before every real LLM call this fork makes --
    `purpose` is normally a response schema's class name (e.g.
    `_EntityExtractionResult`), which is a readable-enough label without
    needing every call site to invent and pass its own description."""

    label = purpose.lstrip("_").replace("Result", "").replace("Extraction", "")
    print(f"    [{_now()}] [{stage_label}] calling {model_name} -> {label or purpose}...", flush=True)
