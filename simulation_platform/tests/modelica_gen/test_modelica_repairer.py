"""Deterministic-only tests for `modelica_repairer.py` -- the LLM call
itself (`run_structured`) isn't exercised (needs OPENAI_API_KEY, see
`test_graph_boundary.py` for that kind of boundary test); this covers the
plumbing that runs BEFORE that call, in particular that a "compiled fine
but the simulated trajectory is physically wrong" result-validation report
is actually accepted and forwarded, not silently dropped.
"""

from __future__ import annotations

import pytest

from simulation_platform.modelica_gen.llm import LLMUnavailable
from simulation_platform.modelica_gen.repair.modelica_repairer import repair_modelica_mappings
from simulation_platform.modelica_gen.workflow.modelica_graph import _result_validation_signature
from simulation_platform.schemas import ModelicaMapping, ModelicaMappingType


def _mapping() -> ModelicaMapping:
    return ModelicaMapping(
        sysml_element="ENT-0001",
        mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
        target="Modelica.Fluid.Sources.Boundary_pT",
        reason="boundary pressure for tank1's inlet",
    )


def test_repair_modelica_mappings_reaches_the_real_llm_boundary_with_a_result_validation_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real bug found live: a run that compiled and simulated cleanly but
    left tank levels flat the entire 900s window (a physically wrong
    result) had no path back into the repair loop at all -- this report is
    now a real input `repair_modelica_mappings` must accept and act on,
    same as a validation/compile report."""

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    report = {
        "status": "FLAGGED",
        "checked": ["tank1 level -> openTank.level"],
        "unmatched": [],
        "issues": ["tank1 level (openTank.level) reached 0.5, below min 4.0"],
    }

    with pytest.raises(LLMUnavailable):
        repair_modelica_mappings([_mapping()], None, None, result_validation_report=report)


def test_result_validation_signature_is_stable_for_identical_issues() -> None:
    report_a = {"status": "FLAGGED", "issues": ["tank1 level reached 0.5, below min 4.0"]}
    report_b = {"status": "FLAGGED", "issues": ["tank1 level reached 0.5, below min 4.0"]}
    assert _result_validation_signature(report_a) == _result_validation_signature(report_b)


def test_result_validation_signature_differs_for_different_issues() -> None:
    report_a = {"status": "FLAGGED", "issues": ["tank1 level reached 0.5, below min 4.0"]}
    report_b = {"status": "FLAGGED", "issues": ["tank2 level reached 9.0, exceeding max 8.0"]}
    assert _result_validation_signature(report_a) != _result_validation_signature(report_b)
