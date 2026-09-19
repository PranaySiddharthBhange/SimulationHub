"""Tests against the real SysML v2 pilot parser (jupyter-sysml-kernel).

Skipped automatically when the local conda kernel isn't installed — see
`validation/real_syntax_validator.py` and `DECISIONS.md` for why this can't
be a hard dependency of the package. Run these after `conda create -n sysml
... jupyter-sysml-kernel -c conda-forge` to actually exercise the real
parser; CI/deterministic runs skip them.
"""

from __future__ import annotations

import pytest

from simulation_platform.sysml_gen.validation.real_syntax_validator import find_kernel_dir, validate_files_with_real_parser

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


def test_real_parser_rejects_flow_port_and_loop_as_bare_attribute_names() -> None:
    """The exact live discovery behind `sysml_generator.py`'s
    `_SYSML_RESERVED_ATTRIBUTE_NAMES` -- a real Stage 2 run generated
    `attribute flow : ...;` (from a requirement whose extracted `property`
    text was literally "flow") and the real parser rejected it. Batch-
    tested against ~150 other candidate words at the time; only these
    three failed. Kept as a real-parser regression test so a future
    grammar/kernel update that changes this set is caught here, not on a
    live customer run six repair attempts deep.

    Each reserved word gets its OWN file -- found live while writing this
    test: putting all three in one file let ANTLR's error-recovery after
    the first bad line partially swallow/misattribute a later one (`loop`
    silently vanished from the reported issues when it followed `flow`/
    `port` in the same file, even though it fails on its own) -- a real
    parser-recovery quirk, not evidence `loop` is actually fine."""

    def _one_attribute_file(name: str) -> dict[str, str]:
        return {"Test.sysml": f"package Test {{ constraint def C1 {{ attribute {name} : ScalarValues::Real; }} }}"}

    for reserved in ("flow", "port", "loop"):
        assert validate_files_with_real_parser(_one_attribute_file(reserved), timeout=90.0) != []

    assert validate_files_with_real_parser(_one_attribute_file("flow_value"), timeout=90.0) == []
