"""Tests against the real SysML v2 pilot parser (jupyter-sysml-kernel).

Skipped automatically when the local conda kernel isn't installed — see
`validation/real_syntax_validator.py` and `DECISIONS.md` for why this can't
be a hard dependency of the package. Run these after `conda create -n sysml
... jupyter-sysml-kernel -c conda-forge` to actually exercise the real
parser; CI/deterministic runs skip them.
"""

from __future__ import annotations

import pytest

from sysml_agent.validation.real_syntax_validator import find_kernel_dir, validate_files_with_real_parser

pytestmark = pytest.mark.skipif(
    find_kernel_dir() is None,
    reason="No local SysML v2 Jupyter kernel found (conda env 'sysml' with jupyter-sysml-kernel not installed).",
)


def test_real_parser_accepts_valid_sysml() -> None:
    files = {"Architecture.sysml": "package Architecture { part def AHU; part ahu : AHU; }"}
    issues = validate_files_with_real_parser(files, timeout=90.0)
    assert issues == []


def test_real_parser_flags_invalid_sysml_with_correct_file_and_line() -> None:
    files = {
        "Architecture.sysml": "package Architecture { part def AHU; part ahu : AHU; }",
        "Broken.sysml": "package Broken { part def AHU\n part def ;;; }",
    }
    issues = validate_files_with_real_parser(files, timeout=90.0)

    assert issues != []
    assert all(issue.file == "Broken.sysml" for issue in issues)
    assert any(issue.line == 2 for issue in issues)
