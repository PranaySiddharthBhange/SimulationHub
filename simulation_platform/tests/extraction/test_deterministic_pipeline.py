"""Exercises discovery -> classification -> parsing -> indexing against all four
golden datasets. Deliberately does NOT touch semantic extraction (Section 25
onward), which requires OPENAI_API_KEY — see `test_smoke_iaq.py`-style
integration tests for that, run manually once a key is configured.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from simulation_platform.extraction.ingestion.dispatcher import process_documents
from simulation_platform.extraction.ingestion.file_classifier import classify_documents
from simulation_platform.extraction.ingestion.file_discovery import discover_files
from simulation_platform.extraction.indexes.index_builder import (
    build_file_index,
    build_information_type_index,
    build_topic_index,
)
from simulation_platform.schemas import DocumentRole, ParseStatus
from simulation_platform.extraction.storage.project_store import ProjectStore

TEST_CASES_ROOT = Path(__file__).resolve().parents[3] / "test cases"

DATASETS = [
    ("iaq_001", "iaq_sysmlv2_full_dataset/iaq_sysmlv2_full_dataset"),
    ("magnetic_circuit_001", "magnetic_circuit_sysmlv2_full_dataset/magnetic_circuit_sysmlv2_full_dataset"),
    ("nacl_evaporation_001", "nacl_evaporation_sysmlv2_full_dataset/nacl_evaporation_sysmlv2_full_dataset"),
    ("tank_001", "tank_sysmlv2_full_dataset/tank_sysmlv2_full_dataset"),
]


@pytest.fixture()
def store(tmp_path: Path) -> ProjectStore:
    return ProjectStore(tmp_path)


@pytest.mark.parametrize("project_id,relative_source", DATASETS)
def test_deterministic_ingestion(
    store: ProjectStore, monkeypatch: pytest.MonkeyPatch, project_id: str, relative_source: str
) -> None:
    # This test's whole point is to run without an LLM — force that regardless
    # of a real .env key being present, so it stays fast, free, and deterministic.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    source_dir = TEST_CASES_ROOT / relative_source
    assert source_dir.is_dir(), f"golden dataset missing: {source_dir}"

    store.create_project(project_id, project_id, source_dir)
    source_original = store.source_original_dir(project_id)

    manifest = discover_files(project_id, source_original)
    assert len(manifest.documents) > 5, "expected multiple files in the golden dataset"

    classify_documents(manifest)
    assert any(doc.role == DocumentRole.PROJECT_REQUIREMENT for doc in manifest.documents)
    assert any(doc.role == DocumentRole.LEGACY_IMPLEMENTATION for doc in manifest.documents)
    assert all(doc.role != DocumentRole.UNKNOWN for doc in manifest.documents), (
        "every file in the golden datasets sits under a recognized role-bearing folder"
    )

    observations = process_documents(manifest, source_original)

    parsed = [d for d in manifest.documents if d.parse_status == ParseStatus.PARSED]
    failed = [d for d in manifest.documents if d.parse_status == ParseStatus.FAILED]
    unsupported = [d for d in manifest.documents if d.parse_status == ParseStatus.UNSUPPORTED]

    # Every file resolves to PARSED, FAILED, or UNSUPPORTED — never silently skipped.
    assert len(parsed) + len(failed) + len(unsupported) == len(manifest.documents)
    assert len(observations) > 0

    # Only the vision-dependent image parser is expected to fail without an API key.
    unexpected_failures = [d for d in failed if d.extension not in (".png", ".jpg", ".jpeg")]
    assert not unexpected_failures, f"unexpected parse failures: {[(d.path, d.parse_error) for d in unexpected_failures]}"

    file_index = build_file_index(manifest, observations)
    topic_index = build_topic_index(manifest, observations)
    info_index = build_information_type_index(manifest)

    assert len(file_index) == len(manifest.documents)
    assert topic_index, "expected at least one topic to be detected"
    assert info_index, "expected at least one information type to be populated"

    print(
        f"\n{project_id}: {len(manifest.documents)} files, {len(parsed)} parsed, "
        f"{len(failed)} failed (expected: images only), {len(observations)} observations, "
        f"topics={sorted(topic_index)}"
    )
