"""Legacy Comparison. Mirrors `Modelica Agent.md`, Sections 14-15:

    Find legacy implementation -> parse Modelica -> understand structure
    -> compare with SysML -> reuse compatible parts -> modify where
    requirements changed.

Deterministic name-similarity matching (no LLM) between each SysML part
and the legacy classes parsed by `analysis/legacy_analyzer.py`, then a
deterministic numeric comparison between each matched legacy parameter and
the current requirement bound covering the same property name (passed in
as plain dicts by `storage/from_sysml_agent.py`, kept decoupled from the
SysML/Document Agents' own schema types).
"""

from __future__ import annotations

from difflib import SequenceMatcher

from simulation_platform.schemas import LegacyComparison, LegacyModel, LegacyRecommendation, SysMLPart

_NAME_MATCH_THRESHOLD = 0.5


def _normalized(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _name_similarity(a: str, b: str) -> float:
    na, nb = _normalized(a), _normalized(b)
    if na in nb or nb in na:
        return 1.0
    return SequenceMatcher(None, na, nb).ratio()


def compare_legacy_models(
    parts: list[SysMLPart],
    legacy_models: list[LegacyModel],
    requirement_bounds: list[dict],
    engineering_id_by_name: dict[str, str] | None = None,
) -> list[LegacyComparison]:
    """`requirement_bounds` items look like
    `{"subject": "Zone-01", "property": "CO2", "min": None, "max": 1000, "value": None, "unit": "ppm"}`.

    `engineering_id_by_name` maps a SysML part's element *name* (all a
    parsed `.sysml` part has) back to its engineering id -- the mapping
    stages downstream (`mapping/element_mapper.py`) key every
    `ModelicaMapping.sysml_element` by engineering id, so `sysml_element`
    on the returned `LegacyComparison` must match that, not the SysML
    name, or `generation/modelica_generator.py`'s lookup by
    `mapping.sysml_element` would silently never find this comparison.
    Falls back to the SysML name itself when no id mapping is given (e.g.
    a test that doesn't care about the generator wiring).
    """
    engineering_id_by_name = engineering_id_by_name or {}

    comparisons: list[LegacyComparison] = []

    for part in parts:
        best_class = None
        best_file = None
        best_score = 0.0
        for legacy_model in legacy_models:
            for legacy_class in legacy_model.classes:
                score = _name_similarity(part.part_def, legacy_class.name)
                if score > best_score:
                    best_score, best_class, best_file = score, legacy_class, legacy_model.filename

        if best_class is None or best_score < _NAME_MATCH_THRESHOLD:
            continue  # no reasonable legacy candidate for this part -- not an error, just nothing to reuse

        matches: list[str] = []
        differences: list[str] = []
        overrides: dict[str, str] = {}
        legacy_params_by_property = {
            key: param
            for param in best_class.parameters
            for key in (param.name,)
        }

        for bound in requirement_bounds:
            property_name = bound.get("property")
            if not property_name:
                continue
            matching_param = next(
                (p for name, p in legacy_params_by_property.items() if property_name.lower() in name.lower()),
                None,
            )
            if matching_param is None:
                continue

            legacy_value = matching_param.value
            current_bound = bound.get("max") if bound.get("max") is not None else bound.get("value")
            if current_bound is None:
                continue

            try:
                if float(legacy_value) == float(current_bound):
                    matches.append(f"{property_name} ({legacy_value} {bound.get('unit') or ''})".strip())
                else:
                    differences.append(
                        f"SysML requires {current_bound} {bound.get('unit') or ''} for {property_name}, "
                        f"legacy model uses {legacy_value}".strip()
                    )
                    overrides[matching_param.name] = str(current_bound)
            except (TypeError, ValueError):
                continue

        if not matches and not differences:
            matches.append(f"class name matches SysML part '{part.part_def}'")

        recommendation = LegacyRecommendation.MODIFY_LEGACY if differences else LegacyRecommendation.REUSE_AS_IS

        comparisons.append(
            LegacyComparison(
                sysml_element=engineering_id_by_name.get(part.part_def, part.part_def),
                legacy_class=best_class.name,
                legacy_file=best_file or "",
                matches=matches,
                differences=differences,
                recommendation=recommendation,
                overrides=overrides,
            )
        )

    return comparisons
