"""Retrieval-on-demand for a planning stage that came back with open
questions -- `new direction.txt` §9/§40: a stage should retrieve only when
it actually discovers it needs something, not read every document up
front, and a later stage should be able to pull from the shared project
workspace (`problem.md`/`documents/`/Stage 1's extracted knowledge) when it
needs to. Deterministic search only (`tools/knowledge_search.py`) -- no
LLM call of its own; the planner decides what to do with what's found.
"""

from __future__ import annotations

from pathlib import Path

from simulation_platform.tools.knowledge_search import search_project


def build_retrieval_context(project_dir: Path, questions: list[str], max_results_per_question: int = 4) -> str:
    """Returns a formatted text block of search hits for each question, or
    "" if nothing was found. Callers should skip a retry entirely when this
    is empty -- there's no point re-asking the LLM with no new information."""

    sections = []
    for question in questions:
        hits = search_project(project_dir, question, max_results=max_results_per_question)
        if hits:
            lines = "\n".join(f"  [{h['source']}] {h['text'][:200]}" for h in hits)
            sections.append(f"Q: {question}\n{lines}")
    return "\n\n".join(sections)
