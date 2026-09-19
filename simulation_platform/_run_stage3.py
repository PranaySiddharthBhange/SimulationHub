"""One-off driver for a non-interactive Stage 3 test run -- auto-accepts
every proposed value (equivalent to pressing Enter at each interactive
prompt) per the user's explicit standing instruction to approve real,
well-reasoned suggestions during testing. Prints every decision so it's
fully visible, never silent. Not part of the actual platform -- deleted
after use.
"""

from __future__ import annotations

import sys

from simulation_platform import pipeline


def on_interrupt(payload: dict) -> object:
    if "pending_value_decisions" in payload:
        answers = []
        for decision in payload["pending_value_decisions"]:
            print(f"\n{decision['class_name']}.{decision['variable']}: {decision['reason']}")
            print(f"  Suggested: {decision['suggested_value']}")
            print("  -> ACCEPTED (auto, per standing approval)")
            answers.append(decision["suggested_value"])
        return answers

    report_path = payload.get("validation_report_path")
    print(f"\nStage needs human review. Report: {report_path}")
    if payload.get("compile_status"):
        print(f"Compile status: {payload['compile_status']}")
    print("  -> ACKNOWLEDGED (auto)")
    return "acknowledged"


if __name__ == "__main__":
    project_id = sys.argv[1] if len(sys.argv) > 1 else "tank_003"
    force = "--force" in sys.argv
    result = pipeline.execute_stage_3(project_id, on_interrupt=on_interrupt, force=force)
    print(f"\n{result.stage}: {result.status}")
    if result.details.get("skipped"):
        print("  (skipped -- input unchanged since last completed run)")
