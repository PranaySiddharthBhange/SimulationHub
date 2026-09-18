"""The Engineering Knowledge Agent (investigation mode). Mirrors `Document Agent.md`, Section 51.

Wraps the retrieval tools in a Deep Agent so downstream questions ("What are
the temperature requirements for Zone-01?") are answered by planning a
targeted retrieval, not by dumping the whole project into one prompt.

To capture a local run log of every tool call and LLM call this agent makes
(see `observability/run_logger.py`), pass a `RunLogger` as a callback at
invoke time — it is not baked into the agent itself, so each conversation
gets its own log file:

    from engineering_agent.observability import RunLogger
    logger = RunLogger(project_dir, run_id="investigation_001")
    agent.invoke({"messages": [...]}, config={"callbacks": [logger]})
"""

from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent

from engineering_agent.config.settings import SETTINGS
from engineering_agent.retrieval.knowledge import ProjectKnowledge
from engineering_agent.retrieval.tools import build_retrieval_tools

SYSTEM_PROMPT = """\
You are the Engineering Knowledge Agent for one engineering project.

You do not have direct access to the source documents — only to the tools
below, which return compact, evidence-linked facts already extracted from
those documents. Always ground your answers in tool results and cite the
specific requirement_id / entity_id / evidence_id you used.

If the available evidence is insufficient or conflicting, say so explicitly
(UNKNOWN / INSUFFICIENT_EVIDENCE, or point at the open conflict/ambiguity) —
never fabricate a value that no tool returned.

Typical investigation pattern:
1. search_entities / search_requirements / search_files to find candidates.
2. get_entity / get_requirement / get_source_section for full detail.
3. get_evidence to cite the exact source location.
4. get_conflicts / get_ambiguities / get_unknowns before asserting a value
   that might be contested.
"""


def build_engineering_knowledge_agent(project_dir: Path):
    knowledge = ProjectKnowledge(project_dir)
    tools = build_retrieval_tools(knowledge)
    return create_deep_agent(
        model=f"openai:{SETTINGS.agent_model}",
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        name="engineering_knowledge_agent",
    )
