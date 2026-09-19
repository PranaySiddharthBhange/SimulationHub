"""Step 1 -- Analyze SysML. Mirrors `Modelica Agent.md`, Section 6.

"The agent shouldn't rely only on an LLM to understand the SysML -- use
parser/AST information wherever possible." There is no real SysML v2 AST
library available here, but the exact textual grammar this pipeline's own
SysML Agent emits is known precisely (see `sysml-agent`'s
`generation/sysml_generator.py`) -- so this is a deterministic,
regex-based structural parser against that known shape, not a guess.

Deliberately does not reparse numeric bounds out of a requirement's `doc`
comment -- that value only exists there as free text for a human/LLM to
read, not as structured SysML syntax at this stage. Numeric/typed values
are cross-referenced from the upstream JSON contract instead (see
`storage/from_sysml_agent.py`).
"""

from __future__ import annotations

import re

from simulation_platform.schemas import (
    SysMLBehavior,
    SysMLConnection,
    SysMLConstraint,
    SysMLInterface,
    SysMLPart,
    SysMLRequirement,
    SysMLSemanticModel,
)

_PART_DEF = re.compile(r"^\s*part def (\w+);")
_PART_INSTANCE = re.compile(r"^\s*part (\w+) : (\w+);")
_CONNECT = re.compile(r"^\s*connect (\w+) to (\w+);(?:\s*//\s*(\w+))?")
_REQUIREMENT_DEF = re.compile(r"^\s*requirement def (\w+) \{")
_DOC_COMMENT = re.compile(r"^\s*doc /\* (.*) \*/")
_ATTRIBUTE = re.compile(r"^\s*attribute (\w+)\s*:")
_INTERFACE_DEF = re.compile(r"^\s*interface def (\w+);")
_ACTION_DEF = re.compile(r"^\s*action def (\w+);")
_COMMENT_LINE = re.compile(r"^\s*//\s*(.*)$")
_CONSTRAINT_DEF = re.compile(r"^\s*constraint def (\w+) \{")
_BLOCK_END = re.compile(r"^\s*\}\s*$")


def _analyze_architecture(text: str, model: SysMLSemanticModel) -> None:
    instance_to_def: dict[str, str] = {}
    for line in text.splitlines():
        if match := _PART_INSTANCE.match(line):
            instance_name, part_def = match.groups()
            instance_to_def[instance_name] = part_def
            model.parts.append(SysMLPart(part_def=part_def, instance_name=instance_name))
        elif match := _CONNECT.match(line):
            source, target, rel_type = match.groups()
            model.connections.append(
                SysMLConnection(source_instance=source, target_instance=target, relationship_type=rel_type)
            )


def _analyze_requirements(text: str, model: SysMLSemanticModel) -> None:
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if match := _REQUIREMENT_DEF.match(lines[i]):
            name = match.group(1)
            doc: str | None = None
            prop: str | None = None
            i += 1
            while i < len(lines) and not _BLOCK_END.match(lines[i]):
                if doc_match := _DOC_COMMENT.match(lines[i]):
                    doc = doc_match.group(1).strip()
                elif attr_match := _ATTRIBUTE.match(lines[i]):
                    prop = prop or attr_match.group(1)
                i += 1
            model.requirements.append(SysMLRequirement(name=name, doc=doc, property=prop))
        i += 1


def _analyze_interfaces(text: str, model: SysMLSemanticModel) -> None:
    for line in text.splitlines():
        if match := _INTERFACE_DEF.match(line):
            model.interfaces.append(SysMLInterface(name=match.group(1)))


def _analyze_behaviors(text: str, model: SysMLSemanticModel) -> None:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if match := _ACTION_DEF.match(line):
            name = match.group(1)
            comment: str | None = None
            if idx + 1 < len(lines):
                if comment_match := _COMMENT_LINE.match(lines[idx + 1]):
                    comment = comment_match.group(1).strip()
            model.behaviors.append(SysMLBehavior(name=name, comment=comment))


def _analyze_constraints(text: str, model: SysMLSemanticModel) -> None:
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if match := _CONSTRAINT_DEF.match(lines[i]):
            name = match.group(1)
            prop: str | None = None
            i += 1
            while i < len(lines) and not _BLOCK_END.match(lines[i]):
                if attr_match := _ATTRIBUTE.match(lines[i]):
                    prop = prop or attr_match.group(1)
                i += 1
            model.constraints.append(SysMLConstraint(name=name, property=prop))
        i += 1


_ANALYZERS = {
    "Architecture.sysml": _analyze_architecture,
    "Requirements.sysml": _analyze_requirements,
    "Interfaces.sysml": _analyze_interfaces,
    "Behaviors.sysml": _analyze_behaviors,
    "Constraints.sysml": _analyze_constraints,
}


def analyze_sysml_files(files: dict[str, str]) -> SysMLSemanticModel:
    model = SysMLSemanticModel()
    for filename, text in files.items():
        analyzer = _ANALYZERS.get(filename)
        if analyzer is not None:
            analyzer(text, model)
    return model
