"""SysML v2 generator. Mirrors `SysML V2 Agent.md`, Section 14.

Deterministic — no LLM call happens here. Takes the already-validated plan
and element mappings and renders them into the five logical files the spec
calls for: `Architecture.sysml`, `Requirements.sysml`, `Interfaces.sysml`,
`Behaviors.sysml`, `Constraints.sysml`.

Honesty note: this renders textual syntax that matches the SysML v2
grammar to the best of our knowledge, but has not been checked against the
official SysML v2 pilot implementation (not installed in this environment).
`validation/syntax_validator.py` catches structural mistakes we can check
without that toolchain (balanced braces, legal identifiers, no dangling
references) — it is not a substitute for a real SysML v2 parser.
"""

from __future__ import annotations

import re
from collections import defaultdict

from sysml_agent.schemas import (
    RequirementItem,
    SysMLConstruct,
    SysMLElementMapping,
    SysMLGenerationContract,
)

_ILLEGAL_IDENTIFIER_CHARS = re.compile(r"[^0-9A-Za-z_]+")


def _legal_identifier(text: str, fallback: str = "value") -> str:
    """`RequirementItem.property`/`ConstraintItem.property` are free-text
    engineering phrases (e.g. "wait time after Tank 1 reaches high level
    before opening V2", not "waitTime") -- found live against a real
    dataset (see DECISIONS.md): embedding one directly as a SysML
    `attribute` name produces an identifier containing spaces, which is
    not legal syntax. Every non-identifier character becomes `_`; a
    leading digit gets an underscore prefix; an empty result (all-illegal
    input) falls back to a generic placeholder rather than emitting
    nothing."""

    cleaned = _ILLEGAL_IDENTIFIER_CHARS.sub("_", text.strip()).strip("_")
    if not cleaned:
        return fallback
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    return cleaned


def _instance_name(element_name: str) -> str:
    """part def Name -> part instance name, lowerCamel of the def name.

    Lowercasing just the first character breaks on acronym-led names like
    "AHU01" (-> "aHU01" instead of "ahu01") or "CO2Sensor01" (-> "cO2Sensor01"
    instead of "co2Sensor01"). Lowercase the whole leading run of
    uppercase/digit characters instead, keeping the last uppercase letter of
    that run capitalized if a new word starts right after it.
    """
    if not element_name:
        return element_name

    i = 0
    while i < len(element_name) and (element_name[i].isupper() or element_name[i].isdigit()):
        i += 1

    if i == 0:
        return element_name  # already starts lowercase
    if i == len(element_name):
        return element_name.lower()  # entirely uppercase/digits, e.g. "AHU01"

    prefix_len = i - 1 if i > 1 and element_name[i - 1].isupper() else i
    return element_name[:prefix_len].lower() + element_name[prefix_len:]


def _render_requirement_doc(item: RequirementItem) -> str:
    if item.min is not None and item.max is not None:
        bound = f"{item.min} {item.operator.value} {item.subject}.{item.property} {item.operator.value} {item.max}"
    elif item.max is not None:
        bound = f"{item.subject}.{item.property} {item.operator.value} {item.max}"
    elif item.min is not None:
        bound = f"{item.subject}.{item.property} {item.operator.value} {item.min}"
    else:
        bound = f"{item.subject}.{item.property} {item.operator.value} {item.value}"
    unit = f" {item.unit}" if item.unit else ""
    return f"{bound}{unit}"


def generate_sysml_files(
    contract: SysMLGenerationContract,
    mappings: list[SysMLElementMapping],
) -> dict[str, str]:
    """Returns {filename: sysml_text} for the five logical files."""

    mapping_by_id = {m.engineering_id: m for m in mappings}
    files: dict[str, list[str]] = defaultdict(list)

    # --- Architecture.sysml: part defs, part instances, connections -------
    arch_lines: list[str] = []
    for entity in contract.entities:
        mapping = mapping_by_id.get(entity.id)
        if mapping is None or mapping.sysml_construct not in (SysMLConstruct.PART_DEF, SysMLConstruct.PART):
            continue
        arch_lines.append(f"    part def {mapping.sysml_element_name};")
    for entity in contract.entities:
        mapping = mapping_by_id.get(entity.id)
        if mapping is None or mapping.sysml_construct not in (SysMLConstruct.PART_DEF, SysMLConstruct.PART):
            continue
        arch_lines.append(f"    part {_instance_name(mapping.sysml_element_name)} : {mapping.sysml_element_name};")
    _PART_CONSTRUCTS = (SysMLConstruct.PART_DEF, SysMLConstruct.PART)
    for rel in contract.relationships:
        source_mapping = mapping_by_id.get(rel.source)
        target_mapping = mapping_by_id.get(rel.target)
        if source_mapping is None or target_mapping is None:
            continue
        if source_mapping.sysml_construct not in _PART_CONSTRUCTS or target_mapping.sysml_construct not in _PART_CONSTRUCTS:
            # A relationship endpoint that isn't part-typed (e.g. mapped to
            # `state def` instead) has no declared `part` instance to
            # connect() to -- rendering one anyway produces a reference the
            # real SysML v2 parser can never resolve (found live against a
            # real dataset, see DECISIONS.md). Recorded as a comment instead
            # of silently dropped, so the relationship isn't lost entirely.
            arch_lines.append(
                f"    // not rendered as connect() -- {rel.source} ({source_mapping.sysml_construct.value}) "
                f"{rel.type} {rel.target} ({target_mapping.sysml_construct.value})"
            )
            continue
        source_instance = _instance_name(source_mapping.sysml_element_name)
        target_instance = _instance_name(target_mapping.sysml_element_name)
        arch_lines.append(f"    connect {source_instance} to {target_instance};  // {rel.type}")
    files["Architecture.sysml"] = ["package Architecture {", *arch_lines, "}"]

    # --- Requirements.sysml -------------------------------------------------
    req_lines: list[str] = []
    for req in contract.requirements:
        mapping = mapping_by_id.get(req.id)
        if mapping is None:
            continue
        req_lines.append(f"    requirement def {mapping.sysml_element_name} {{")
        req_lines.append(f"        doc /* {_render_requirement_doc(req)} */")
        req_lines.append(f"        attribute {_legal_identifier(req.property)} : ScalarValues::Real;")
        req_lines.append("    }")
    files["Requirements.sysml"] = ["package Requirements {", *req_lines, "}"]

    # --- Interfaces.sysml ----------------------------------------------------
    iface_lines: list[str] = []
    for iface in contract.interfaces:
        mapping = mapping_by_id.get(iface.id)
        if mapping is None:
            continue
        iface_lines.append(f"    interface def {mapping.sysml_element_name};")
    files["Interfaces.sysml"] = ["package Interfaces {", *iface_lines, "}"]

    # --- Behaviors.sysml -------------------------------------------------------
    behavior_lines: list[str] = []
    for behavior in contract.behaviors:
        mapping = mapping_by_id.get(behavior.id)
        if mapping is None:
            continue
        behavior_lines.append(f"    action def {mapping.sysml_element_name};")
        behavior_lines.append(
            f"    // {behavior.trigger_property} {behavior.trigger_operator.value} "
            f"{behavior.trigger_value} {behavior.trigger_unit or ''} -> {behavior.action_type} {behavior.action_target}"
        )
    files["Behaviors.sysml"] = ["package Behaviors {", *behavior_lines, "}"]

    # --- Constraints.sysml -------------------------------------------------------
    constraint_lines: list[str] = []
    for constraint in contract.constraints:
        mapping = mapping_by_id.get(constraint.id)
        if mapping is None:
            continue
        constraint_lines.append(f"    constraint def {mapping.sysml_element_name} {{")
        constraint_lines.append(f"        attribute {_legal_identifier(constraint.property)} : ScalarValues::Real;")
        constraint_lines.append("    }")
    files["Constraints.sysml"] = ["package Constraints {", *constraint_lines, "}"]

    return {name: "\n".join(lines) + "\n" for name, lines in files.items()}
