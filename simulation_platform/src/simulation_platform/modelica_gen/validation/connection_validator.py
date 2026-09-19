"""Layer 3 -- Connection validation. Mirrors `Modelica Agent.md`, Section
22: "Are connectors compatible?" Cross-checks each SysML interface's
declared domain (`kind`) against the connector domain implied by its
source/target component's own library mapping, via the same fixed
compatibility rule `connection_validator.py`'s neighbor,
`libraries/compatibility.py`, uses.
"""

from __future__ import annotations

from simulation_platform.modelica_gen.libraries import CONNECTOR_CATALOG, connector_kinds_compatible
from simulation_platform.schemas import ModelicaMapping, ModelicaValidationIssue, ValidationLayer

_CATALOG_CLASS_TO_KIND = {
    candidate.modelica_class: candidate.connector_kind
    for candidates in CONNECTOR_CATALOG.values()
    for candidate in candidates
}


def _component_connector_kind(entity_id: str | None, component_mappings_by_id: dict[str, ModelicaMapping]) -> str | None:
    if entity_id is None:
        return None
    mapping = component_mappings_by_id.get(entity_id)
    if mapping is None:
        return None
    return _CATALOG_CLASS_TO_KIND.get(mapping.target)


def validate_connections(
    interfaces: list[dict], component_mappings: list[ModelicaMapping]
) -> list[ModelicaValidationIssue]:
    mappings_by_id = {m.sysml_element: m for m in component_mappings}
    issues: list[ModelicaValidationIssue] = []

    for interface in interfaces:
        kind = interface.get("kind")
        if not kind:
            continue
        source_kind = _component_connector_kind(interface.get("source_entity"), mappings_by_id)
        target_kind = _component_connector_kind(interface.get("target_entity"), mappings_by_id)

        if not connector_kinds_compatible(source_kind, kind) or not connector_kinds_compatible(target_kind, kind):
            issues.append(
                ModelicaValidationIssue(
                    layer=ValidationLayer.CONNECTION,
                    element=interface.get("id", interface.get("name", "")),
                    message=(
                        f"Interface kind '{kind}' is incompatible with its source/target component's "
                        f"connector kind (source={source_kind}, target={target_kind})."
                    ),
                )
            )

    return issues
