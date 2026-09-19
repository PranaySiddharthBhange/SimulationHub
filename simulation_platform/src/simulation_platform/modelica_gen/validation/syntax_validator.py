"""Layer 1 -- Syntax validation. Mirrors `Modelica Agent.md`, Section 22.

Not a substitute for the real OpenModelica compiler (see
`compiler/openmodelica_client.py`, which the SysML Agent's equivalent real
parser precedent already showed is worth wiring in when the toolchain is
installed) -- this catches what a template-based generator can actually get
wrong on its own: unbalanced braces/parens, a class/`end` mismatch, and
illegal identifiers.
"""

from __future__ import annotations

import re

from simulation_platform.schemas import ModelicaValidationIssue, ValidationLayer

_CLASS_OPEN = re.compile(r"^\s*(?:model|block|connector|record|package|class)\s+(\w+)")
_CLASS_END = re.compile(r"^\s*end\s+(\w+)\s*;")
_IDENTIFIER = re.compile(r"^[A-Za-z_]\w*$")


def validate_syntax(filename: str, text: str) -> list[ModelicaValidationIssue]:
    issues: list[ModelicaValidationIssue] = []

    open_braces, close_braces = text.count("{"), text.count("}")
    if open_braces != close_braces:
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.SYNTAX, element=filename,
                message=f"Unbalanced braces: {open_braces} '{{' vs {close_braces} '}}'.",
            )
        )

    open_parens, close_parens = text.count("("), text.count(")")
    if open_parens != close_parens:
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.SYNTAX, element=filename,
                message=f"Unbalanced parentheses: {open_parens} '(' vs {close_parens} ')'.",
            )
        )

    stack: list[str] = []
    for line in text.splitlines():
        if match := _CLASS_OPEN.match(line):
            name = match.group(1)
            if not _IDENTIFIER.match(name):
                issues.append(
                    ModelicaValidationIssue(
                        layer=ValidationLayer.SYNTAX, element=filename,
                        message=f"'{name}' is not a legal Modelica identifier.",
                    )
                )
            stack.append(name)
        elif match := _CLASS_END.match(line):
            end_name = match.group(1)
            if not stack:
                issues.append(
                    ModelicaValidationIssue(
                        layer=ValidationLayer.SYNTAX, element=filename,
                        message=f"'end {end_name};' has no matching open class declaration.",
                    )
                )
            elif stack[-1] != end_name:
                issues.append(
                    ModelicaValidationIssue(
                        layer=ValidationLayer.SYNTAX, element=filename,
                        message=f"'end {end_name};' does not match the open class '{stack[-1]}'.",
                    )
                )
            else:
                stack.pop()

    for unclosed in stack:
        issues.append(
            ModelicaValidationIssue(
                layer=ValidationLayer.SYNTAX, element=filename,
                message=f"Class '{unclosed}' is never closed with a matching 'end' statement.",
            )
        )

    return issues
