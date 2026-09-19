"""Layer 2 -- Structural validation. Mirrors `Modelica Agent.md`, Section
22: "Are classes/components/connectors/references valid?" Checks that
`package.order` matches the classes actually generated, that every class
name has a corresponding `.mo` file, and that no single canonical entity
ends up instantiated more than once.

Deliberately does NOT check whether a SysML connection *comment*'s
endpoints resolve to a declared instance -- most relationships are still
rendered as a `// connect: ...` comment (real `connect()` calls are only
generated for the known Fluid/Electrical/Magnetic port families, see
`generation/modelica_generator.py::_resolve_fluid_connections` and its
potential-based neighbor); a comment referencing an undeclared instance
is not a dangling reference in actual Modelica syntax, so there is
nothing there for the real compiler to fail to resolve.
"""

from __future__ import annotations

from simulation_platform.schemas import (
    ModelicaMapping,
    ModelicaMappingType,
    ModelicaValidationIssue,
    ValidationLayer,
)

# Only these mapping types actually instantiate a NEW top-level Modelica
# component (see `generate_modelica_files`'s `element_registry` assignment
# sites) -- PARAMETER/EQUATION/ALGORITHM/ASSERTION/CONNECTOR mappings
# modify or reference an existing instance, they never create one.
_INSTANCE_CREATING_MAPPING_TYPES = {
    ModelicaMappingType.LIBRARY_COMPONENT,
    ModelicaMappingType.MODEL,
    ModelicaMappingType.BLOCK,
}


def _duplicate_instance_engineering_ids(component_mappings: list[ModelicaMapping]) -> list[str]:
    """Real bug found live: the SAME real-world entity (a tank, a valve)
    ended up rendered as multiple SEPARATE Modelica instances -- discovered
    that time because entity resolution failed to merge cross-convention
    aliases (fixed in `extraction/resolution/entity_resolution.py`), but
    nothing here would catch the same symptom if it arose independently,
    e.g. a planning/mapping bug that emits two separate component mappings
    for one canonical engineering id. This is the structural invariant
    that actually matters -- one canonical entity, one instance -- checked
    directly on the mappings themselves rather than re-deriving it from
    generated text."""

    seen: set[str] = set()
    duplicates: list[str] = []
    for mapping in component_mappings:
        if mapping.mapping_type not in _INSTANCE_CREATING_MAPPING_TYPES:
            continue
        if mapping.sysml_element in seen and mapping.sysml_element not in duplicates:
            duplicates.append(mapping.sysml_element)
        seen.add(mapping.sysml_element)
    return duplicates


def _entry_class_has_no_real_content(entry_class: str, files: dict[str, str]) -> bool:
    """Found live on a real dataset -- the single most severe bug this
    platform has shipped: the planner's response substituted SysML part/
    requirement NAMES for real engineering ids, so every downstream
    lookup silently found nothing, and the "generated" entry class ended
    up with zero parameters, zero component instances, and zero real
    equations -- ONLY the always-present `// connect: ...` relationship
    comments (rendered directly from the SysML model, independent of
    mappings). That model still reported a clean, real `omc` compile
    PASS, since an empty model trivially compiles -- structurally valid,
    completely meaningless. Every substantive line this generator ever
    emits (a `parameter`, an instance declaration, a real equation) is
    something OTHER than the class/equation/end boilerplate and a `//`
    comment; if literally nothing else is present, the whole generation
    silently produced nothing worth compiling."""

    text = files.get(f"{entry_class}.mo", "")
    boilerplate = {f"model {entry_class}", "equation", f"end {entry_class};"}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped in boilerplate:
            continue
        return False
    return True


def validate_structure(
    files: dict[str, str],
    class_names: list[str],
    entry_class: str = "",
    component_mappings: list[ModelicaMapping] | None = None,
) -> list[ModelicaValidationIssue]:
    issues: list[ModelicaValidationIssue] = []

    for engineering_id in _duplicate_instance_engineering_ids(component_mappings or []):
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.STRUCTURAL, element=engineering_id,
                message=(
                    f"'{engineering_id}' has more than one component-creating mapping "
                    "(LIBRARY_COMPONENT/MODEL/BLOCK) -- the same real-world entity would be instantiated "
                    "as two or more separate Modelica instances. Real bug found live: unresolved entity/"
                    "mapping duplication produced 6 tank instances standing in for 2 real tanks. Merge "
                    "these mappings into one, or fix the duplicate at its source."
                ),
            )
        )

    if entry_class and entry_class in class_names and _entry_class_has_no_real_content(entry_class, files):
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.STRUCTURAL, element=entry_class,
                message=(
                    f"'{entry_class}' has no real parameters, component instances, or equations -- only "
                    "relationship comments (or nothing at all). This usually means the planning/mapping stage "
                    "silently dropped every real component (e.g. a plan referencing SysML names instead of "
                    "real engineering ids) -- a real compile could still trivially pass on an empty model."
                ),
            )
        )

    order_names = [line.strip() for line in files.get("package.order", "").splitlines() if line.strip()]
    missing_from_order = set(class_names) - set(order_names)
    extra_in_order = set(order_names) - set(class_names)
    for name in sorted(missing_from_order):
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.STRUCTURAL, element="package.order",
                message=f"Class '{name}' was generated but is missing from package.order.",
            )
        )
    for name in sorted(extra_in_order):
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.STRUCTURAL, element="package.order",
                message=f"'{name}' is listed in package.order but no such class was generated.",
            )
        )

    for name in class_names:
        if f"{name}.mo" not in files:
            issues.append(
                ModelicaValidationIssue(
                    layer=ValidationLayer.STRUCTURAL, element=name,
                    message=f"Class '{name}' has no corresponding '{name}.mo' file.",
                )
            )

    return issues
