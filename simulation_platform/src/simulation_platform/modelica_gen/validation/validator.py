"""Deterministic validation orchestrator -- Layers 1-4 (Layer 5, parameter,
is split across a text check and a contract-level bound check; Layer 6,
semantic, is the LLM review and lives separately in `semantic_validator.py`
so it doesn't block the deterministic gate). Mirrors `Modelica Agent.md`,
Section 22.
"""

from __future__ import annotations

from simulation_platform.schemas import ModelicaMapping, ModelicaValidationResult, ValidationStatus

from .connection_validator import validate_connections
from .parameter_validator import validate_parameter_bounds, validate_parameter_values
from .structure_validator import validate_structure
from .syntax_validator import validate_syntax
from .unit_validator import validate_units


def validate_generation(
    modelica_version: str,
    generated_files: dict[str, str],
    class_names: list[str],
    interfaces: list[dict],
    component_mappings: list[ModelicaMapping],
    requirement_bounds: list[dict],
    entry_class: str = "",
) -> ModelicaValidationResult:
    mo_files = {name: text for name, text in generated_files.items() if name.endswith(".mo")}

    syntax_issues = [issue for filename, text in mo_files.items() for issue in validate_syntax(filename, text)]
    structure_issues = validate_structure(generated_files, class_names, entry_class, component_mappings)
    connection_issues = validate_connections(interfaces, component_mappings)
    unit_issues = [issue for filename, text in mo_files.items() for issue in validate_units(filename, text)]
    parameter_issues = [
        issue for filename, text in mo_files.items() for issue in validate_parameter_values(filename, text)
    ] + validate_parameter_bounds(requirement_bounds)

    all_issues = syntax_issues + structure_issues + connection_issues + unit_issues + parameter_issues
    status = ValidationStatus.PASSED if not all_issues else ValidationStatus.FAILED

    return ModelicaValidationResult(modelica_version=modelica_version, status=status, issues=all_issues)
