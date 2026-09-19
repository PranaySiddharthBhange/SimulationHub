"""Traceability. Mirrors `Modelica Agent.md`, Section 21 and Section 33's
full chain: Document -> Evidence -> Requirement -> SysML -> Modelica.
Purely deterministic -- every field here was already decided by an earlier
stage; this just records the mapping.
"""

from __future__ import annotations

from simulation_platform.modelica_gen.naming import legal_identifier as _legal_identifier
from simulation_platform.schemas import (
    ModelicaMapping,
    ModelicaMappingType,
    ModelicaTraceability,
    ModelicaTraceEntity,
    ModelicaTraceRequirement,
)


def build_traceability(
    modelica_version: str,
    sysml_version: str,
    knowledge_version: str,
    mappings: list[ModelicaMapping],
    entry_class: str,
    sysml_element_names_by_id: dict[str, str],
) -> ModelicaTraceability:
    entities: list[ModelicaTraceEntity] = []
    requirements: list[ModelicaTraceRequirement] = []

    for mapping in mappings:
        sysml_element_name = sysml_element_names_by_id.get(mapping.sysml_element, mapping.sysml_element)

        if mapping.mapping_type == ModelicaMappingType.PARAMETER:
            parameter_name = _legal_identifier(mapping.sysml_element)
            requirements.append(
                ModelicaTraceRequirement(
                    requirement_id=mapping.sysml_element,
                    sysml_requirement=sysml_element_name,
                    modelica_elements=[f"{entry_class}.{parameter_name}"],
                    evidence=mapping.evidence,
                )
            )
            continue

        if mapping.mapping_type == ModelicaMappingType.LIBRARY_COMPONENT:
            entities.append(
                ModelicaTraceEntity(
                    engineering_id=mapping.sysml_element,
                    sysml_element=sysml_element_name,
                    modelica_class=mapping.target,
                    file="",
                )
            )
            continue

        if mapping.mapping_type in (ModelicaMappingType.MODEL, ModelicaMappingType.BLOCK):
            class_name = _legal_identifier(mapping.target.rsplit(".", 1)[-1]) if mapping.target else mapping.sysml_element
            entities.append(
                ModelicaTraceEntity(
                    engineering_id=mapping.sysml_element,
                    sysml_element=sysml_element_name,
                    modelica_class=class_name,
                    file=f"{class_name}.mo",
                )
            )

    return ModelicaTraceability(
        modelica_version=modelica_version,
        sysml_version=sysml_version,
        knowledge_version=knowledge_version,
        entities=entities,
        requirements=requirements,
    )
