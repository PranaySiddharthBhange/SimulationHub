"""Layer 1 — Syntax validation. Mirrors `SysML V2 Agent.md`, Section 17.

Not a substitute for the real SysML v2 pilot parser (not installed here) —
this catches the mistakes a template-based generator can actually make:
unbalanced braces, and construct names that aren't legal SysML
identifiers. A real toolchain check should still run before trusting this
output in earnest.
"""

from __future__ import annotations

import re

from simulation_platform.schemas import SyntaxIssue

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CONSTRUCT_DECL = re.compile(
    r"\b(?:part def|part|requirement def|interface def|action def|constraint def)\s+(\w+)"
)


def validate_syntax(filename: str, text: str) -> list[SyntaxIssue]:
    issues: list[SyntaxIssue] = []

    open_braces = text.count("{")
    close_braces = text.count("}")
    if open_braces != close_braces:
        issues.append(
            SyntaxIssue(file=filename, message=f"Unbalanced braces: {open_braces} '{{' vs {close_braces} '}}'.")
        )

    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in _CONSTRUCT_DECL.finditer(line):
            name = match.group(1)
            if not _IDENTIFIER.match(name):
                issues.append(SyntaxIssue(file=filename, line=line_no, message=f"'{name}' is not a legal SysML identifier."))

    return issues
