"""A real, persistent record of what the pipeline did for one project --
answers "is there a log preserved in the project folder" with an actual
yes. Complements `progress.py`'s real-time terminal printing (which
nothing keeps once the terminal scrolls away): every stage start/end,
every LLM call, and every real validator/compiler attempt is appended as
one JSON object per line to `projects/<project_id>/run.jsonl`, so a run
can be inspected, replayed, or costed out after the fact.

Deliberately JSONL (one JSON object per line), not one big JSON array --
append-only, so a run that's killed mid-way still leaves a complete,
parseable log of everything that happened before the kill, and `tail -f`
works on it the same way it works on a plain text log.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


class RunLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, kind: str, **fields) -> None:
        record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": kind, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    @contextmanager
    def stage(self, name: str, **fields) -> Iterator[None]:
        """Wraps one stage/attempt: logs `stage_start` on entry and
        `stage_end` (with elapsed seconds, and the exception type/message
        if it raised) on exit -- used the same way `_traced_stage` prints
        to the terminal, just also durably recorded."""

        started = datetime.now(timezone.utc)
        self.event("stage_start", name=name, **fields)
        error: BaseException | None = None
        try:
            yield
        except BaseException as exc:  # noqa: BLE001 -- re-raised immediately below, just observed first
            error = exc
            raise
        finally:
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            if error is None:
                self.event("stage_end", name=name, elapsed_seconds=round(elapsed, 1), ok=True)
            else:
                self.event(
                    "stage_end", name=name, elapsed_seconds=round(elapsed, 1), ok=False,
                    error_type=type(error).__name__, error_message=str(error),
                )
