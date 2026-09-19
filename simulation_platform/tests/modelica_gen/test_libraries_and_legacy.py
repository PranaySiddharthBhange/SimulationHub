from __future__ import annotations

from simulation_platform.modelica_gen.analysis import analyze_legacy_file
from simulation_platform.modelica_gen.legacy import compare_legacy_models
from simulation_platform.modelica_gen.libraries import connector_kinds_compatible, resolve_component
from simulation_platform.schemas import SysMLPart


def test_resolve_component_unambiguous_for_single_keyword_match() -> None:
    resolution = resolve_component("CO2Sensor01", "CO2Sensor")
    assert resolution.matched_keywords == ["sensor"]
    assert not resolution.ambiguous
    assert resolution.candidates[0].modelica_class == "Modelica.Blocks.Interfaces.RealOutput"


def test_resolve_component_ambiguous_for_controller() -> None:
    resolution = resolve_component("Controller01", "Controller")
    assert resolution.ambiguous
    assert len(resolution.candidates) == 2


def test_resolve_component_no_match_returns_empty_candidates() -> None:
    resolution = resolve_component("SomethingNovel", None)
    assert resolution.candidates == []
    assert not resolution.ambiguous


def test_connector_kinds_compatible() -> None:
    assert connector_kinds_compatible("SIGNAL", "SIGNAL")
    assert not connector_kinds_compatible("SIGNAL", "FLUID")
    assert connector_kinds_compatible(None, "SIGNAL")  # unknown -- not enough info to flag
    assert not connector_kinds_compatible("NOT_A_KIND", "SIGNAL")


_LEGACY_MO = """\
model TankDemo_Rev12
  parameter Real h1High(unit="m") = 0.78;
end TankDemo_Rev12;
"""


def test_compare_legacy_models_detects_matching_value() -> None:
    legacy_model = analyze_legacy_file("tank.mo", _LEGACY_MO)
    parts = [SysMLPart(part_def="TankDemo", instance_name="tankDemo")]
    bounds = [{"subject": "TankDemo", "property": "h1High", "min": None, "max": 0.78, "value": None, "unit": "m"}]

    comparisons = compare_legacy_models(parts, [legacy_model], bounds)

    assert len(comparisons) == 1
    comparison = comparisons[0]
    assert comparison.legacy_class == "TankDemo_Rev12"
    assert comparison.recommendation.value == "REUSE_AS_IS"
    assert comparison.differences == []


def test_compare_legacy_models_detects_changed_requirement_and_records_override() -> None:
    legacy_model = analyze_legacy_file("tank.mo", _LEGACY_MO)
    parts = [SysMLPart(part_def="TankDemo", instance_name="tankDemo")]
    bounds = [{"subject": "TankDemo", "property": "h1High", "min": None, "max": 0.70, "value": None, "unit": "m"}]

    comparisons = compare_legacy_models(parts, [legacy_model], bounds)

    assert len(comparisons) == 1
    comparison = comparisons[0]
    assert comparison.recommendation.value == "MODIFY_LEGACY"
    assert comparison.overrides == {"h1High": "0.7"}


def test_compare_legacy_models_skips_unrelated_parts() -> None:
    legacy_model = analyze_legacy_file("tank.mo", _LEGACY_MO)
    parts = [SysMLPart(part_def="TotallyUnrelatedThing", instance_name="x")]

    comparisons = compare_legacy_models(parts, [legacy_model], [])
    assert comparisons == []
