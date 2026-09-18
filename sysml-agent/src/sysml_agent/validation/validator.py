"""Deterministic validation orchestrator — Layers 1-4. Mirrors `SysML V2
Agent.md`, Section 17. Layer 5 (semantic — "did we preserve engineering
meaning?") is an LLM review and lives separately in `semantic_validator.py`,
since it genuinely needs a model and shouldn't block the deterministic gate.
"""

from __future__ import annotations

import logging

from sysml_agent.schemas import (
    SysMLElementMapping,
    SysMLGenerationContract,
    SysMLGenerationPlan,
    SysMLValidationResult,
    ValidationStatus,
)

from .real_syntax_validator import RealParserUnavailable, validate_files_with_real_parser
from .requirement_validator import validate_requirement_coverage
from .structure_validator import validate_structure
from .syntax_validator import validate_syntax
from .traceability_validator import validate_traceability

logger = logging.getLogger(__name__)


def _collect_syntax_errors(generated_files: dict[str, str], use_real_parser: bool, real_parser_timeout: float):
    """Prefers the real SysML v2 pilot parser (ANTLR-based, catches everything
    a real compiler would); falls back to the regex-based checker when the
    local toolchain isn't installed. Never silently skips validation."""

    if use_real_parser:
        try:
            return validate_files_with_real_parser(generated_files, timeout=real_parser_timeout)
        except RealParserUnavailable as exc:
            logger.warning("Real SysML v2 parser unavailable (%s); falling back to regex syntax checker.", exc)

    return [issue for filename, text in generated_files.items() for issue in validate_syntax(filename, text)]


def validate_generation(
    generation_id: str,
    contract: SysMLGenerationContract,
    plan: SysMLGenerationPlan,
    mappings: list[SysMLElementMapping],
    generated_files: dict[str, str],
    use_real_parser: bool = False,
    real_parser_timeout: float = 60.0,
) -> SysMLValidationResult:
    syntax_errors = _collect_syntax_errors(generated_files, use_real_parser, real_parser_timeout)
    structural_errors = validate_structure(contract, plan, mappings)
    coverage = validate_requirement_coverage(contract, mappings)
    traceability_errors = validate_traceability(mappings)

    status = (
        ValidationStatus.PASSED
        if not (syntax_errors or structural_errors or traceability_errors or coverage.missing)
        else ValidationStatus.FAILED
    )

    return SysMLValidationResult(
        generation_id=generation_id,
        status=status,
        syntax_errors=syntax_errors,
        structural_errors=structural_errors,
        requirement_coverage=coverage,
        traceability_errors=traceability_errors,
        semantic_errors=[],
    )
