"""Deterministic, on-demand search across everything in a project -- the
"retrieval" side of `new direction.txt` §9/§29/§40: a later stage that
discovers it needs something ("Stage 3 may discover a parameter that was
not explicitly needed during Stage 2") should be able to search
`problem.md`/`documents/`/the Stage 1 knowledge base for it, instead of
either re-reading every document through an LLM again or silently
fabricating a value.

No LLM call here -- plain substring/keyword search over text already on
disk. This is deliberately the LAST resort before falling back to a
proposed assumption (see `new direction.txt` §15's priority order): check
`system_model.json` and the structured knowledge first (cheap, exact),
only fall through to this free-text search when the structured facts
don't have the answer.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml"}


@dataclass
class SearchHit:
    source: str  # "problem.md" | "documents/<relpath>" | "project_knowledge.json:<section>"
    line: int | None
    text: str

    def to_dict(self) -> dict:
        return {"source": self.source, "line": self.line, "text": self.text}


def _tokenize(query: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", query.lower())
    return [w for w in words if len(w) > 2]  # skip stopword-length noise ("a", "of", "is", ...)


def _matches(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return any(w in lowered for w in words)


def _search_text_file(path: Path, source_label: str, words: list[str], max_hits: int) -> list[SearchHit]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    hits = []
    for i, line in enumerate(lines, start=1):
        if line.strip() and _matches(line, words):
            hits.append(SearchHit(source=source_label, line=i, text=line.strip()))
            if len(hits) >= max_hits:
                break
    return hits


def _search_project_knowledge(project_dir: Path, words: list[str], max_hits: int) -> list[SearchHit]:
    knowledge_path = project_dir / "workspace" / "extracted" / "project_knowledge.json"
    if not knowledge_path.exists():
        return []
    try:
        model = json.loads(knowledge_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    hits: list[SearchHit] = []
    for section in ("entities", "requirements", "behaviors", "constraints", "relationships"):
        for item in model.get(section, []):
            text = json.dumps(item)
            if _matches(text, words):
                label = item.get("name") or item.get("subject") or item.get("entity_id") or item.get("requirement_id") or ""
                hits.append(SearchHit(source=f"project_knowledge.json:{section}", line=None, text=f"{label}: {text}"[:300]))
                if len(hits) >= max_hits:
                    return hits
    return hits


def search_project(project_dir: Path, query: str, max_results: int = 8) -> list[dict]:
    """Searches `problem.md`, every text-readable file under `documents/`,
    and Stage 1's `project_knowledge.json` for `query`. Returns up to
    `max_results` hits as plain dicts (source, line, text) -- callers
    (a planning/mapping prompt's extra context, or a human-review payload)
    decide how to use them; this never calls an LLM itself."""

    words = _tokenize(query)
    if not words:
        return []

    hits: list[SearchHit] = []

    problem_path = project_dir / "problem.md"
    if problem_path.exists():
        hits.extend(_search_text_file(problem_path, "problem.md", words, max_results))

    documents_dir = project_dir / "documents"
    if documents_dir.exists():
        for file_path in sorted(documents_dir.rglob("*")):
            if len(hits) >= max_results:
                break
            if file_path.is_file() and file_path.suffix.lower() in _TEXT_SUFFIXES:
                rel = file_path.relative_to(documents_dir)
                hits.extend(_search_text_file(file_path, f"documents/{rel}", words, max_results - len(hits)))

    if len(hits) < max_results:
        hits.extend(_search_project_knowledge(project_dir, words, max_results - len(hits)))

    return [h.to_dict() for h in hits[:max_results]]
