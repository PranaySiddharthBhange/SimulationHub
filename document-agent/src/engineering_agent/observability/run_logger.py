"""Local run logger — a JSONL trail of every graph node, tool call, and LLM
call for one run. Mirrors `Document Agent.md`, Section 62 (Observability).

Built on `langchain_core.callbacks.BaseCallbackHandler`, which is the
built-in extensibility point both LangGraph nodes and LangChain tools/LLMs
already fire through — there is no separate "LangGraph logging library";
this callback system *is* the mechanism. Verified empirically (not
assumed) that:

- a plain Python function used as a `StateGraph` node fires
  `on_chain_start`/`on_chain_end`/`on_chain_error` with `name=<node name>`
  on start, but `on_chain_error` does NOT receive `name` — only `run_id`.
  So this handler tracks `run_id -> name` from the start event and looks
  it up again on error/end, rather than trusting the name to be passed
  every time.
- invoking a `@tool`-decorated function or a `ChatOpenAI` call with
  `config={"callbacks": [...]}` fires the matching `on_tool_*`/`on_llm_*`
  hooks the same way.

Usage: pass `config={"callbacks": [RunLogger(project_dir, run_id)]}` to
`graph.invoke(...)` or to any tool/agent `.invoke(...)` call you want
captured into the same log.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

_SKIP_NAMES = {"LangGraph"}  # the synthetic top-level wrapper chain; every real node logs its own start/end


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate(value: Any, limit: int = 2000) -> str:
    text = str(value)
    return text if len(text) <= limit else text[: limit] + f"...[{len(text) - limit} more chars]"


class RunLogger(BaseCallbackHandler):
    def __init__(self, project_dir: Path, run_id: str):
        self.run_id = run_id
        self.path = project_dir / "logs" / f"run_{run_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._names_by_run: dict[UUID, str] = {}
        self._skipped_run_ids: set[UUID] = set()

    def _write(self, event: str, **fields: Any) -> None:
        record = {"timestamp": _now(), "run_id": self.run_id, "event": event, **fields}
        with self._lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")

    def _remember(self, run_id: UUID, name: str | None) -> None:
        if name:
            self._names_by_run[run_id] = name

    def _lookup(self, run_id: UUID) -> str | None:
        return self._names_by_run.pop(run_id, None)

    # -- graph nodes ("chains" in callback terms) ---------------------------

    def on_chain_start(self, serialized, inputs, *, run_id, **kwargs):
        name = kwargs.get("name") or (serialized or {}).get("name")
        if name in _SKIP_NAMES:
            self._skipped_run_ids.add(run_id)
            return
        self._remember(run_id, name)
        self._write("node_start", node=name, inputs=_truncate(inputs))

    def on_chain_end(self, outputs, *, run_id, **kwargs):
        if run_id in self._skipped_run_ids:
            self._skipped_run_ids.discard(run_id)
            return
        name = self._lookup(run_id)
        if name is None:
            return  # was a skipped/untracked chain
        self._write("node_end", node=name, outputs=_truncate(outputs))

    def on_chain_error(self, error, *, run_id, **kwargs):
        if run_id in self._skipped_run_ids:
            self._skipped_run_ids.discard(run_id)
            return  # the top-level graph wrapper re-raising a node's own error
        name = self._lookup(run_id)
        self._write("node_error", node=name, error=_truncate(error))

    # -- tool calls -----------------------------------------------------------

    def on_tool_start(self, serialized, input_str, *, run_id, inputs=None, **kwargs):
        name = (serialized or {}).get("name")
        self._remember(run_id, name)
        self._write("tool_start", tool=name, input=_truncate(inputs if inputs is not None else input_str))

    def on_tool_end(self, output, *, run_id, **kwargs):
        self._write("tool_end", tool=self._lookup(run_id), output=_truncate(output))

    def on_tool_error(self, error, *, run_id, **kwargs):
        self._write("tool_error", tool=self._lookup(run_id), error=_truncate(error))

    # -- LLM calls -------------------------------------------------------------

    def on_llm_start(self, serialized, prompts, *, run_id, metadata=None, **kwargs):
        model = (metadata or {}).get("ls_model_name") or (serialized or {}).get("name")
        self._remember(run_id, model)
        self._write("llm_start", model=model, prompts=_truncate(prompts))

    def on_chat_model_start(self, serialized, messages, *, run_id, metadata=None, **kwargs):
        model = (metadata or {}).get("ls_model_name") or (serialized or {}).get("name")
        self._remember(run_id, model)
        self._write("llm_start", model=model, messages=_truncate(messages))

    def on_llm_end(self, response, *, run_id, **kwargs):
        self._write("llm_end", model=self._lookup(run_id), response=_truncate(response))

    def on_llm_error(self, error, *, run_id, **kwargs):
        self._write("llm_error", model=self._lookup(run_id), error=_truncate(error))
