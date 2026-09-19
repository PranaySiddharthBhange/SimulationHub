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

from simulation_platform.schemas import (
    RequirementItem,
    SysMLConstruct,
    SysMLElementMapping,
    SysMLGenerationContract,
)

_ILLEGAL_IDENTIFIER_CHARS = re.compile(r"[^0-9A-Za-z_]+")
_NON_ALNUM = re.compile(r"[^0-9A-Za-z]+")


def _is_bare_id_name(name: str, engineering_id: str) -> bool:
    """True when an LLM-produced `sysml_element_name` degenerated into just
    the bare engineering id with punctuation stripped (e.g. "REQ0001" from
    "REQ-0001") -- the exact same failure mode found live on the Modelica
    side (see `modelica_gen/naming.py`'s `readable_identifier` docstring):
    a generated model's parameters all showed up in OMEdit's variable
    browser as "REQ0001", "REQ0002", ... A fact id carries no engineering
    meaning on its own, so this is never an acceptable element name even
    though it's a syntactically legal identifier the mapper prompt asked
    for -- worth guarding deterministically rather than trusting the
    prompt's "be descriptive" instruction alone."""

    return bool(name) and _NON_ALNUM.sub("", name).lower() == _NON_ALNUM.sub("", engineering_id).lower()


def _readable_identifier(*parts: str, fallback: str) -> str:
    """Same helper as `modelica_gen/naming.py`'s `readable_identifier` --
    builds a real lowerCamelCase identifier from free engineering text
    (e.g. an entity's own `name`, or a requirement's `subject`/`property`),
    never a hardcoded string. Used ONLY as a deterministic fallback for the
    rare case the mapper LLM's own `sysml_element_name` degenerates to a
    bare id -- the LLM's real, descriptive name is always preferred when
    it gave one."""

    words: list[str] = []
    for part in parts:
        words.extend(re.findall(r"[A-Za-z0-9]+", part or ""))
    if not words:
        return fallback
    first, *rest = words
    identifier = first.lower() + "".join(w[:1].upper() + w[1:] for w in rest)
    return _legal_identifier(identifier, fallback=fallback)


def _meaningful_name(mapping: SysMLElementMapping, *fallback_parts: str) -> str:
    """The mapper LLM's own `sysml_element_name` when it's real and
    descriptive (the normal, preferred case) -- a deterministic, readable
    fallback built from real extracted text (`fallback_parts`, e.g. an
    entity's `name` or a requirement's `subject`/`property`) only when the
    LLM's name degenerated into the bare id or was left empty."""

    if not mapping.sysml_element_name or _is_bare_id_name(mapping.sysml_element_name, mapping.engineering_id):
        return _readable_identifier(
            *fallback_parts, fallback=mapping.sysml_element_name or _legal_identifier(mapping.engineering_id)
        )
    return mapping.sysml_element_name


# Confirmed live against the REAL ANTLR-based SysML v2 parser, not the
# full official keyword list (not published anywhere this pipeline can
# introspect): batch-tested ~150 candidate words as a bare `attribute
# <word> : ScalarValues::Real;` declaration, one word per `constraint
# def`, in a single real-kernel run -- these actually failed to parse
# ("no viable alternative at input 'attribute'"), everything else
# (including many other plausible SysML keywords like `part`, `action`,
# `interface`, `requirement`) parsed fine as a bare attribute name in this
# grammatical position. Found live on TWO separate real datasets: a
# requirement's own extracted `property` text was literally "flow" (as in
# "V1 nominal flow value") on the first attempt, and "state" (as in
# "sequence context.state") on the very next one -- each survived 6 real
# auto-repair attempts before escalating to human review, since the
# repair LLM kept proposing syntactically-plausible-looking fixes that
# didn't address the actual root cause (a reserved word, not a malformed
# declaration). `state` in particular is exactly the kind of word real
# engineering text uses constantly ("current state", "controller state"),
# so this set should be expected to grow -- not necessarily exhaustive; a
# new collision found on a future dataset should be added here the same
# way (a real, minimal, live-verified repro), never guessed at.
_SYSML_RESERVED_ATTRIBUTE_NAMES = {"flow", "port", "loop", "state"}


def _legal_identifier(text: str, fallback: str = "value") -> str:
    """`RequirementItem.property`/`ConstraintItem.property` are free-text
    engineering phrases (e.g. "wait time after Tank 1 reaches high level
    before opening V2", not "waitTime") -- found live against a real
    dataset (see DECISIONS.md): embedding one directly as a SysML
    `attribute` name produces an identifier containing spaces, which is
    not legal syntax. Every non-identifier character becomes `_`; a
    leading digit gets an underscore prefix; an empty result (all-illegal
    input) falls back to a generic placeholder rather than emitting
    nothing. A result that collides with a real SysML v2 reserved word
    (`_SYSML_RESERVED_ATTRIBUTE_NAMES`) gets a `_value` suffix -- matches
    the naming style this generator already produces elsewhere (e.g.
    "tank1_level_default_value")."""

    cleaned = _ILLEGAL_IDENTIFIER_CHARS.sub("_", text.strip()).strip("_")
    if not cleaned:
        return fallback
    if cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    if cleaned.lower() in _SYSML_RESERVED_ATTRIBUTE_NAMES:
        cleaned = f"{cleaned}_value"
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

    # Computed once per entity id, not re-derived independently every time
    # it's referenced (part def, part instance, and every connect() line
    # all need the SAME name for the same entity) -- real extracted text
    # (`entity.name`) is the only fallback source, never a hardcoded
    # string; the mapper LLM's own descriptive name is used whenever it
    # gave one (see `_meaningful_name`).
    entity_name_by_id = {
        entity.id: _meaningful_name(mapping_by_id[entity.id], entity.name)
        for entity in contract.entities
        if mapping_by_id.get(entity.id) is not None
    }

    # --- Architecture.sysml: part defs, part instances, connections -------
    arch_lines: list[str] = []
    for entity in contract.entities:
        mapping = mapping_by_id.get(entity.id)
        if mapping is None or mapping.sysml_construct not in (SysMLConstruct.PART_DEF, SysMLConstruct.PART):
            continue
        arch_lines.append(f"    part def {entity_name_by_id[entity.id]};")
    for entity in contract.entities:
        mapping = mapping_by_id.get(entity.id)
        if mapping is None or mapping.sysml_construct not in (SysMLConstruct.PART_DEF, SysMLConstruct.PART):
            continue
        name = entity_name_by_id[entity.id]
        arch_lines.append(f"    part {_instance_name(name)} : {name};")
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
        source_instance = _instance_name(entity_name_by_id[rel.source])
        target_instance = _instance_name(entity_name_by_id[rel.target])
        arch_lines.append(f"    connect {source_instance} to {target_instance};  // {rel.type}")
    files["Architecture.sysml"] = ["package Architecture {", *arch_lines, "}"]

    # --- Requirements.sysml -------------------------------------------------
    req_lines: list[str] = []
    for req in contract.requirements:
        mapping = mapping_by_id.get(req.id)
        if mapping is None:
            continue
        req_lines.append(f"    requirement def {_meaningful_name(mapping, req.subject, req.property)} {{")
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
        iface_lines.append(f"    interface def {_meaningful_name(mapping, iface.name)};")
    files["Interfaces.sysml"] = ["package Interfaces {", *iface_lines, "}"]

    # --- Behaviors.sysml -------------------------------------------------------
    behavior_lines: list[str] = []
    for behavior in contract.behaviors:
        mapping = mapping_by_id.get(behavior.id)
        if mapping is None:
            continue
        behavior_lines.append(
            f"    action def {_meaningful_name(mapping, behavior.action_type, behavior.action_target)};"
        )
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
        constraint_lines.append(f"    constraint def {_meaningful_name(mapping, constraint.subject, constraint.property)} {{")
        constraint_lines.append(f"        attribute {_legal_identifier(constraint.property)} : ScalarValues::Real;")
        constraint_lines.append("    }")
    # Control laws (continuous/proportional relationships, distinct from a
    # behavior's discrete if/then action) map to the same `constraint def`
    # construct as a bounded-range constraint -- both are mathematical
    # relationships on properties, not a discrete trigger/action pair -- so
    # they render alongside regular constraints rather than adding a sixth
    # file (`new direction.txt` §6: prefer a few meaningful files).
    for control_law in contract.control_laws:
        mapping = mapping_by_id.get(control_law.id)
        if mapping is None:
            continue
        name = _meaningful_name(mapping, control_law.controlled_property, control_law.input_property)
        constraint_lines.append(f"    constraint def {name} {{")
        constraint_lines.append(f"        attribute {_legal_identifier(control_law.controlled_property)} : ScalarValues::Real;")
        constraint_lines.append(f"        attribute {_legal_identifier(control_law.input_property)} : ScalarValues::Real;")
        gains = ", ".join(
            f"{name}={value}" for name, value in (
                ("gain_p", control_law.gain_p), ("gain_i", control_law.gain_i), ("gain_d", control_law.gain_d),
            ) if value is not None
        )
        setpoint = f", setpoint={control_law.setpoint}{control_law.setpoint_unit or ''}" if control_law.setpoint is not None else ""
        constraint_lines.append(f"        doc /* {control_law.law_type}: {gains}{setpoint} */")
        constraint_lines.append("    }")
    files["Constraints.sysml"] = ["package Constraints {", *constraint_lines, "}"]

    return {name: "\n".join(lines) + "\n" for name, lines in files.items()}
