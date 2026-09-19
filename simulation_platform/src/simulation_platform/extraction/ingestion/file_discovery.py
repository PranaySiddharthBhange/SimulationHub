"""File discovery. Mirrors `Document Agent.md`, Section 7."""

from __future__ import annotations

import hashlib
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

from simulation_platform.schemas import DocumentRecord, SourceManifest


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_files(project_id: str, source_original_dir: Path) -> SourceManifest:
    """Walk `source/original/` and produce a `SourceManifest` with one record per file."""

    documents: list[DocumentRecord] = []
    for index, path in enumerate(sorted(source_original_dir.rglob("*"))):
        if not path.is_file():
            continue
        rel_path = path.relative_to(source_original_dir)
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(path.name)
        documents.append(
            DocumentRecord(
                document_id=f"doc_{index:04d}",
                path=str(rel_path).replace("\\", "/"),
                filename=path.name,
                extension=path.suffix.lower(),
                size=stat.st_size,
                sha256=_sha256(path),
                modified_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                mime_type=mime_type,
            )
        )
    return SourceManifest(project_id=project_id, documents=documents)
