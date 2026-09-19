"""Legacy Modelica reuse -- Section 14/15 in `Modelica Agent.md`. Parses an
existing `.mo` file into structured `LegacyClass` records (parameters,
variables, connects, equations), each with an exact line number, so
`legacy/legacy_comparator.py` can compare it against the SysML semantic
model instead of the agent throwing the legacy file away and regenerating
from scratch.

Deliberately never executes the file (that belongs to the Compiler /
Simulation Agent). Pragmatic regex extraction, not a full Modelica
grammar/AST -- the same honest scope call the Document Agent's own
`parsers/modelica_parser.py` already made for the identical file format,
extended here to actually structure parameters (including the
`(unit="...")` declaration-modifier syntax the real legacy files use, which
the Document Agent's simpler regex does not attempt to parse out) and,
found live to be necessary rather than assumed (see DECISIONS.md), a
variable's declared type is captured whatever it is (not just Real/
Boolean/Integer/String) alongside any `type X = enumeration(...);`
declaration -- a legacy file's algorithm section can reference a variable
of a custom enum type, and skipping the enum/variable while still
faithfully reusing the algorithm that references it produces a legacy
class that references an undeclared variable outright.
"""

from __future__ import annotations

import re

from simulation_platform.schemas import LegacyClass, LegacyModel, LegacyParameter, LegacyVariable

_CLASS_DECL = re.compile(r"^\s*(model|block|package|class|record|connector)\s+(\w+)")
_END_DECL = re.compile(r"^\s*end\s+(\w+)\s*;")
_PARAMETER_DECL = re.compile(
    r'^\s*parameter\s+([\w.]+)\s+(\w+)\s*(?:\(([^)]*)\))?\s*=\s*([^;"]+?)\s*(?:"[^"]*")?\s*;'
)
_VARIABLE_DECL = re.compile(
    r"^\s*(?P<discrete>discrete\s+)?(?:flow\s+|input\s+|output\s+)*"
    r"(?P<type>\w+)\s+(?P<name>\w+)\s*(?:\((?P<modifiers>[^)]*)\))?\s*;"
)
_TYPE_ENUM_DECL = re.compile(r"^\s*type\s+\w+\s*=\s*enumeration\s*\([^)]*\)\s*;")
_CONNECT_CALL = re.compile(r"connect\s*\(\s*([\w.]+)\s*,\s*([\w.]+)\s*\)\s*;")
_EQUATION_SECTION = re.compile(r"^\s*(equation|algorithm)\b")
_UNIT_MODIFIER = re.compile(r'unit\s*=\s*"([^"]*)"')
_START_MODIFIER = re.compile(r"start\s*=\s*([^,)]+)")
_COMMENT = re.compile(r"//.*$")


def _unit_from_modifiers(modifiers: str | None) -> str | None:
    if not modifiers:
        return None
    match = _UNIT_MODIFIER.search(modifiers)
    return match.group(1) if match else None


def _start_from_modifiers(modifiers: str | None) -> str | None:
    if not modifiers:
        return None
    match = _START_MODIFIER.search(modifiers)
    return match.group(1).strip() if match else None


def analyze_legacy_file(filename: str, text: str) -> LegacyModel:
    classes: list[LegacyClass] = []
    current: LegacyClass | None = None
    section_kind: str | None = None  # "equation" | "algorithm" | None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("//") or line.startswith("within "):
            continue

        if end_match := _END_DECL.match(line):
            if current is not None and end_match.group(1) == current.name:
                classes.append(current)
                current = None
                section_kind = None
            continue

        if class_match := _CLASS_DECL.match(line):
            if current is not None:
                classes.append(current)
            current = LegacyClass(kind=class_match.group(1), name=class_match.group(2))
            section_kind = None
            continue

        if current is None:
            continue

        if param_match := _PARAMETER_DECL.match(line):
            type_, name, modifiers, value = param_match.groups()
            current.parameters.append(
                LegacyParameter(
                    name=name, type=type_, value=value.strip(), unit=_unit_from_modifiers(modifiers), line=line_no
                )
            )
            continue

        for source, target in _CONNECT_CALL.findall(line):
            current.connects.append((source, target))

        if section_match := _EQUATION_SECTION.match(line):
            section_kind = section_match.group(1)
            continue

        if section_kind is not None:
            if line.endswith(";"):
                cleaned = _COMMENT.sub("", line).strip()
                if cleaned:
                    if section_kind == "algorithm":
                        current.algorithm_statements.append(cleaned)
                    else:
                        current.equations.append(cleaned)
            continue

        if _TYPE_ENUM_DECL.match(line):
            current.type_declarations.append(line)
            continue

        if var_match := _VARIABLE_DECL.match(line):
            modifiers = var_match.group("modifiers")
            current.variables.append(
                LegacyVariable(
                    name=var_match.group("name"), type=var_match.group("type"),
                    unit=_unit_from_modifiers(modifiers), is_discrete=bool(var_match.group("discrete")),
                    start_value=_start_from_modifiers(modifiers), line=line_no,
                )
            )

    if current is not None:
        classes.append(current)

    return LegacyModel(filename=filename, classes=classes)
