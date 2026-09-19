"""Deterministic-only tests for `modelica_planner.py`'s backstops -- the
LLM call itself (`create_modelica_plan`) isn't exercised here (needs
OPENAI_API_KEY).
"""

from __future__ import annotations

from simulation_platform.modelica_gen.planning.modelica_planner import _drop_dataset_properties, _keep_real_ids


def test_keep_real_ids_drops_a_name_the_model_substituted_for_a_real_id() -> None:
    """Found live on a real Tank system run: the planner's response
    substituted SysML part/requirement NAMES (e.g. "tK_101",
    "V1_open_during_normal_operation") for real engineering ids -- every
    downstream `{id}_by_id.get(name)` lookup then silently found nothing,
    collapsing 14 real components and 192 real properties into a
    completely empty generated model that still reported a clean PASSED
    compile status."""

    real_ids = ["ENT-0001", "ENT-0002", "REQ-0001"]
    proposed = ["ENT-0001", "tK_101", "V1_open_during_normal_operation"]

    assert _keep_real_ids(proposed, real_ids) == ["ENT-0001"]


def test_keep_real_ids_keeps_everything_when_all_are_real() -> None:
    real_ids = ["ENT-0001", "ENT-0002"]
    assert _keep_real_ids(real_ids, real_ids) == real_ids


def test_drop_dataset_properties_excludes_a_benchmark_csv_derived_requirement() -> None:
    """Found live: a requirement extracted FROM the project's own
    benchmark CSV ("dataset 09_datasets/10_demo_run_900s.csv", property
    "row_count", unit "rows") was selected as needing its own Modelica
    parameter -- a real, non-recoverable unit-validation failure, since
    there's no sensible physical unit for "rows". These are ground-truth
    VALIDATION bounds for `evaluate_simulation_result`, never something
    needing Modelica representation."""

    sysml_contract_raw = {
        "requirements": [
            {"id": "REQ-0001", "subject": "TK-101", "property": "height"},
            {"id": "REQ-0203", "subject": "dataset 09_datasets/10_demo_run_900s.csv", "property": "row_count"},
        ]
    }

    result = _drop_dataset_properties(["REQ-0001", "REQ-0203"], sysml_contract_raw)

    assert result == ["REQ-0001"]


def test_drop_dataset_properties_is_a_noop_without_contract_data() -> None:
    assert _drop_dataset_properties(["REQ-0001"], None) == ["REQ-0001"]
    assert _drop_dataset_properties(["REQ-0001"], {}) == ["REQ-0001"]
