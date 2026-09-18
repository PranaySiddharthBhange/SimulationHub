"""CLI: run the SysML Agent for a project already ingested by the Document Agent.

Usage:
    python scripts/generate_sysml.py <project_id> [document_agent_projects_root]

Defaults `document_agent_projects_root` to ../document-agent/projects, so
running this against a project you already ingested there just works.
"""

from __future__ import annotations

import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402

from sysml_agent.config import SETTINGS  # noqa: E402
from sysml_agent.llm import LLMUnavailable  # noqa: E402
from sysml_agent.observability import BudgetExceeded, BudgetGuard, RunLogger  # noqa: E402
from sysml_agent.workflow.sysml_graph import build_sysml_graph  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        raise SystemExit(1)

    project_id = sys.argv[1]
    document_agent_root = (
        Path(sys.argv[2]) if len(sys.argv) == 3
        else Path(__file__).resolve().parent.parent.parent / "document-agent" / "projects"
    ).resolve()

    document_agent_dir = document_agent_root / project_id
    if not (document_agent_dir / "semantic" / "semantic_model.json").exists():
        raise SystemExit(
            f"No semantic_model.json found for '{project_id}' under {document_agent_root}. "
            "Run the Document Agent's ingest_project.py (with OPENAI_API_KEY set) first."
        )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + f"_{uuid.uuid4().hex[:8]}"
    logger = RunLogger(SETTINGS.project_dir(project_id), run_id=run_id)
    budget = BudgetGuard(
        limit_usd=SETTINGS.llm_budget_usd,
        price_per_1k_input_usd=SETTINGS.price_per_1k_input_usd,
        price_per_1k_output_usd=SETTINGS.price_per_1k_output_usd,
    )
    print(f"LLM budget cap: ${budget.limit_usd:.2f} (estimated cost, see observability/budget_guard.py)")

    graph = build_sysml_graph(
        lambda pid: document_agent_root / pid,
        lambda pid: SETTINGS.project_dir(pid),
    ).compile(checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": project_id}, "callbacks": [logger, budget]}
    initial_state = {
        "project_id": project_id,
        "generation_id": "gen_0001",
        "entities_in_contract": 0,
        "requirements_in_contract": 0,
        "mappings_created": 0,
        "files_generated": 0,
        "validation_status": "",
        "repair_attempt": 0,
        "sysml_version": "v0001",
        "status": "PENDING",
    }

    try:
        result = graph.invoke(initial_state, config=config)
    except LLMUnavailable:
        sysml_dir = SETTINGS.project_dir(project_id) / "sysml"
        print(
            "\nGeneration contract was built and persisted, but planning/mapping needs an LLM.\n"
            "Set OPENAI_API_KEY in .env and re-run to continue past this point.\n"
            f"\nInspect what's already there: {sysml_dir / 'input' / 'generation_contract.json'}\n"
            f"Run log: {logger.path}"
        )
        return
    except BudgetExceeded as exc:
        print(
            f"\nStopped: {exc}\n"
            f"Estimated spend this run: ${budget.spent_usd:.4f} over {budget.call_count} LLM calls "
            f"(cap: ${budget.limit_usd:.2f}).\n"
            "This is an estimate from token counts, not a billing figure — see "
            "observability/budget_guard.py. Raise SYSML_AGENT_BUDGET_USD in .env to continue.\n"
            f"\nWhatever completed before the cap tripped was already written to disk: "
            f"{SETTINGS.project_dir(project_id)}\n"
            f"Run log: {logger.path}"
        )
        return

    if "__interrupt__" in result:
        print("\nGeneration paused for human review of a failed validation:")
        for interrupt_obj in result["__interrupt__"]:
            print(interrupt_obj.value)
        print("\nResume with: graph.invoke(Command(resume=True), config=config)")
        return

    print("\nSysML generation complete.")
    for key in (
        "entities_in_contract", "requirements_in_contract", "mappings_created",
        "files_generated", "validation_status", "status",
    ):
        print(f"  {key}: {result.get(key)}")
    print(f"\nEstimated LLM spend this run: ${budget.spent_usd:.4f} over {budget.call_count} calls (not a billing figure)")
    print(f"Generated files: {SETTINGS.project_dir(project_id) / 'sysml' / 'generated'}")
    print(f"Run log: {logger.path}")


if __name__ == "__main__":
    main()
