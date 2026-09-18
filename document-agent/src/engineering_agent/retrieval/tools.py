"""LangChain tool wrappers over `ProjectKnowledge`. Mirrors `Document Agent.md`, Section 51.

`build_retrieval_tools` binds every tool to one project's knowledge, so the
Deep Agent created in `engineering_agent.agent` only ever sees compact,
structured retrieval results — never the raw project folder.
"""

from __future__ import annotations

from langchain_core.tools import tool

from .knowledge import ProjectKnowledge


def build_retrieval_tools(knowledge: ProjectKnowledge) -> list:
    @tool
    def search_files(query: str) -> list[dict]:
        """Search source files by path or filename substring."""
        return [doc.model_dump() for doc in knowledge.search_files(query)]

    @tool
    def search_entities(query: str) -> list[dict]:
        """Search resolved entities by name, alias, or type substring."""
        return [ent.model_dump() for ent in knowledge.search_entities(query)]

    @tool
    def search_requirements(query: str) -> list[dict]:
        """Search requirements by subject or property substring."""
        return [req.model_dump() for req in knowledge.search_requirements(query)]

    @tool
    def get_entity(entity_id: str) -> dict | None:
        """Get one resolved entity by its entity_id (e.g. ENT-0001)."""
        entity = knowledge.get_entity(entity_id)
        return entity.model_dump() if entity else None

    @tool
    def get_requirement(requirement_id: str) -> dict | None:
        """Get one requirement by its requirement_id (e.g. REQ-0001)."""
        requirement = knowledge.get_requirement(requirement_id)
        return requirement.model_dump() if requirement else None

    @tool
    def get_evidence(fact_id: str) -> list[dict]:
        """Get every evidence record backing a fact_id (an entity/requirement/relationship/behavior/constraint id)."""
        return [ev.model_dump() for ev in knowledge.get_evidence(fact_id)]

    @tool
    def get_source_section(document_id: str) -> list[dict]:
        """Get every observation extracted from one document_id, in extraction order."""
        return [obs.model_dump() for obs in knowledge.get_source_section(document_id)]

    @tool
    def get_conflicts() -> list[dict]:
        """List every detected conflict between competing claims, resolved or open."""
        return knowledge.get_conflicts()

    @tool
    def get_ambiguities() -> list[dict]:
        """List every open interpretation ambiguity."""
        return knowledge.get_ambiguities()

    @tool
    def get_unknowns() -> list[dict]:
        """List every property that is required but has no known value in any source."""
        return knowledge.get_unknowns()

    @tool
    def get_decisions() -> list[dict]:
        """List every human decision recorded in the decision ledger."""
        return knowledge.get_decisions()

    @tool
    def get_dataset_statistics(file: str) -> dict | None:
        """Get column-level statistics for a CSV dataset file (never the raw rows)."""
        return knowledge.get_dataset_statistics(file)

    @tool
    def get_dataset_rows(file: str, start: int = 0, end: int | None = None) -> list[dict]:
        """Get a bounded row range from a CSV dataset file — never call this without start/end on a large file."""
        return knowledge.get_dataset_rows(file, start, end)

    return [
        search_files,
        search_entities,
        search_requirements,
        get_entity,
        get_requirement,
        get_evidence,
        get_source_section,
        get_conflicts,
        get_ambiguities,
        get_unknowns,
        get_decisions,
        get_dataset_statistics,
        get_dataset_rows,
    ]
