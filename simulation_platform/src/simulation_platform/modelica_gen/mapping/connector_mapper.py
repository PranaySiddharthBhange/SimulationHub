"""Interface/Connector Mapping -- deterministic. Mirrors `Modelica Agent.md`,
Section 12: "the actual connector selection must depend on the engineering
domain" -- looked up from the fixed `CONNECTOR_CATALOG`, never invented.
"""

from __future__ import annotations

from simulation_platform.modelica_gen.libraries import CONNECTOR_CATALOG
from simulation_platform.schemas import ModelicaMapping, ModelicaMappingType


def map_connectors(interface_ids: list[str], sysml_contract_raw: dict) -> list[ModelicaMapping]:
    interfaces_by_id = {i["id"]: i for i in sysml_contract_raw.get("interfaces", [])}

    mappings: list[ModelicaMapping] = []
    for interface_id in interface_ids:
        interface = interfaces_by_id.get(interface_id)
        if interface is None:
            continue

        kind = interface.get("kind") or "SIGNAL"
        candidates = CONNECTOR_CATALOG.get(kind, CONNECTOR_CATALOG["SIGNAL"])
        target = " / ".join(c.modelica_class for c in candidates)
        mappings.append(
            ModelicaMapping(
                sysml_element=interface_id,
                mapping_type=ModelicaMappingType.CONNECTOR,
                target=target,
                reason=f"Interface kind '{kind}' maps to the {kind} connector pair in the standard catalog.",
                evidence=interface.get("evidence", []),
            )
        )
    return mappings
