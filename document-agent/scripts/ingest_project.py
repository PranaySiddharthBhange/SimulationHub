"""CLI: create a project from a source folder and run the ingestion graph.

Usage:
    python scripts/ingest_project.py <project_id> <name> <source_dir>

Example (against the IAQ golden dataset):
    python scripts/ingest_project.py iaq_001 "IAQ Control System" \\
        "../test cases/iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset"
"""

from __future__ import annotations

import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402

from engineering_agent.config.settings import SETTINGS  # noqa: E402
from engineering_agent.extraction.llm import ExtractionUnavailable  # noqa: E402
from engineering_agent.observability import BudgetExceeded, BudgetGuard, RunLogger  # noqa: E402
from engineering_agent.storage.project_store import ProjectStore  # noqa: E402
from engineering_agent.workflows.ingestion_graph import build_ingestion_graph  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__)
        raise SystemExit(1)

    project_id, name, source_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
    if not source_dir.is_dir():
        raise SystemExit(f"Source directory not found: {source_dir}")

    store = ProjectStore(SETTINGS.projects_root)
    store.create_project(project_id, name, source_dir)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + f"_{uuid.uuid4().hex[:8]}"
    logger = RunLogger(store.project_dir(project_id), run_id=run_id)
    budget = BudgetGuard(
        limit_usd=SETTINGS.extraction_budget_usd,
        price_per_1k_input_usd=SETTINGS.price_per_1k_input_usd,
        price_per_1k_output_usd=SETTINGS.price_per_1k_output_usd,
    )
    print(f"Extraction budget cap: ${budget.limit_usd:.2f} (estimated cost, see observability/budget_guard.py)")

    graph = build_ingestion_graph(store).compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": project_id}, "callbacks": [logger, budget]}

    initial_state = {
        "project_id": project_id,
        "source_dir": str(source_dir),
        "files_discovered": 0,
        "files_parsed": 0,
        "files_failed": 0,
        "observations_created": 0,
        "entities_found": 0,
        "relationships_found": 0,
        "requirements_found": 0,
        "behaviors_found": 0,
        "constraints_found": 0,
        "conflicts": 0,
        "ambiguities": 0,
        "unknowns": 0,
        "assumptions": 0,
        "model_version": "",
        "status": "INGESTING",
        "errors": [],
    }

    try:
        result = graph.invoke(initial_state, config=config)
    except ExtractionUnavailable:
        project_dir = store.project_dir(project_id)
        print(
            "\nDeterministic stages (discovery, classification, parsing, indexing) "
            "completed and were written to disk, but semantic extraction needs an LLM.\n"
            "Set OPENAI_API_KEY in .env and re-run to continue past this point.\n"
            f"\nInspect what's already there: {project_dir}\n"
            f"  - {project_dir / 'source_manifest.json'}\n"
            f"  - {project_dir / 'observations' / 'observations.jsonl'}\n"
            f"  - {project_dir / 'index'}\n"
            f"  - {logger.path} (run log: every node this run executed)"
        )
        return
    except BudgetExceeded as exc:
        print(
            f"\nStopped: {exc}\n"
            f"Estimated spend this run: ${budget.spent_usd:.4f} over {budget.call_count} LLM calls "
            f"(cap: ${budget.limit_usd:.2f}).\n"
            "This is an estimate from token counts, not a billing figure — see "
            "observability/budget_guard.py. Raise ENGINEERING_AGENT_BUDGET_USD in .env to continue.\n"
            f"\nWhatever completed before the cap tripped was already written to disk: "
            f"{store.project_dir(project_id)}\n"
            f"Run log: {logger.path}"
        )
        return

    if "__interrupt__" in result:
        print("\nIngestion paused — human clarification required:")
        for interrupt_obj in result["__interrupt__"]:
            print(interrupt_obj.value)
        print(
            "\nResume with: graph.invoke(Command(resume=[{'ambiguity_id': ..., 'answer': ...}]), config=config)"
        )
        return

    print("\nIngestion complete.")
    for key in (
        "files_discovered",
        "files_parsed",
        "files_failed",
        "observations_created",
        "entities_found",
        "relationships_found",
        "requirements_found",
        "behaviors_found",
        "constraints_found",
        "conflicts",
        "ambiguities",
        "unknowns",
        "assumptions",
        "model_version",
        "status",
    ):
        print(f"  {key}: {result.get(key)}")
    print(f"\nEstimated LLM spend this run: ${budget.spent_usd:.4f} over {budget.call_count} calls (not a billing figure)")
    print(f"Project folder: {store.project_dir(project_id)}")
    print(f"Run log: {logger.path}")


if __name__ == "__main__":
    main()
