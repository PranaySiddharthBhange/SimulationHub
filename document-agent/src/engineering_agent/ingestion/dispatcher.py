"""Parser dispatch + failure handling. Mirrors `Document Agent.md`, Sections 9 and 43.

Never silently skips a file: every document ends up `PARSED`, `FAILED`
(with an error recorded), or `UNSUPPORTED` (no parser registered for that
extension). Parsing failures never crash the ingestion run — the project
continues, and `reports/coverage_report.json` (see `evidence/quality`)
reports the resulting incomplete coverage honestly.
"""

from __future__ import annotations

import logging
from pathlib import Path

from engineering_agent.parsers import PARSER_BY_EXTENSION, ParserError
from engineering_agent.schemas import DocumentRecord, Observation, ParseStatus, SourceManifest

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


def process_documents(manifest: SourceManifest, source_original_dir: Path) -> list[Observation]:
    """Dispatch every document in `manifest` to its parser, updating status in place."""

    all_observations: list[Observation] = []
    for document in manifest.documents:
        observations = _process_one(document, source_original_dir)
        all_observations.extend(observations)
    return all_observations


def _process_one(document: DocumentRecord, source_original_dir: Path) -> list[Observation]:
    parser = PARSER_BY_EXTENSION.get(document.extension)
    if parser is None:
        document.parse_status = ParseStatus.UNSUPPORTED
        document.parse_error = f"No parser registered for extension '{document.extension}'."
        logger.warning("Unsupported file: %s (%s)", document.path, document.extension)
        return []

    file_path = source_original_dir / document.path
    last_error: str | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            observations = parser.parse(document, file_path)
        except ParserError as exc:
            last_error = str(exc)
            document.retry_count = attempt + 1
            logger.warning("Parse attempt %d failed for %s: %s", attempt + 1, document.path, exc)
            continue
        document.parse_status = ParseStatus.PARSED
        document.parse_error = None
        return observations

    document.parse_status = ParseStatus.FAILED
    document.parse_error = last_error
    logger.error("Parse failed after %d attempts: %s (%s)", MAX_RETRIES + 1, document.path, last_error)
    return []
