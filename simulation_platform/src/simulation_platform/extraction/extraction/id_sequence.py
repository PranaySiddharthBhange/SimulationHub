"""Stable, project-scoped id generation for extracted semantic facts."""

from __future__ import annotations

from collections import defaultdict


class IdSequence:
    """Generates ids like `ENT-0007`, monotonically increasing per prefix for one run."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)

    def next(self, prefix: str) -> str:
        self._counters[prefix] += 1
        return f"{prefix}-{self._counters[prefix]:04d}"
