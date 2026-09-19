"""Rule-based file classification. Mirrors `Document Agent.md`, Section 8.

Classification is rules-first: the golden datasets (and most real engineering
projects) organize files into role-bearing folders. An LLM classifier can be
layered on top for files that don't match any rule, but every file the rules
below recognize is classified deterministically, with no LLM call.
"""

from __future__ import annotations

import re

from simulation_platform.schemas import DocumentRecord, DocumentRole, InformationType, SourceManifest

# Folder-name keyword -> role. Matched against any path segment, case-insensitive.
_FOLDER_ROLE_RULES: list[tuple[re.Pattern[str], DocumentRole]] = [
    (re.compile(r"requirement"), DocumentRole.PROJECT_REQUIREMENT),
    (re.compile(r"engineering_data|engineering[-_ ]register"), DocumentRole.ENGINEERING_DATA),
    (re.compile(r"architecture|diagram"), DocumentRole.ARCHITECTURE),
    (re.compile(r"design_note|design[-_ ]review"), DocumentRole.DESIGN_NOTE),
    (re.compile(r"correspondence|email"), DocumentRole.CORRESPONDENCE),
    (re.compile(r"legacy"), DocumentRole.LEGACY_IMPLEMENTATION),
    (re.compile(r"datasheet"), DocumentRole.DATASHEET),
    (re.compile(r"commissioning|acceptance|validation|runbook"), DocumentRole.COMMISSIONING),
    (re.compile(r"dataset|measurement"), DocumentRole.MEASUREMENT),
]

# Extension -> default information types, used when folder rules don't already imply one.
_EXTENSION_INFO_TYPES: dict[str, list[InformationType]] = {
    ".mo": [InformationType.LEGACY_IMPLEMENTATION, InformationType.CONTROL_LOGIC],
    ".puml": [InformationType.ARCHITECTURE],
    ".png": [InformationType.ARCHITECTURE],
    ".jpg": [InformationType.ARCHITECTURE],
    ".jpeg": [InformationType.ARCHITECTURE],
    ".eml": [InformationType.CORRESPONDENCE],
    ".csv": [InformationType.MEASUREMENT_DATA],
}

_ROLE_INFO_TYPES: dict[DocumentRole, list[InformationType]] = {
    DocumentRole.PROJECT_REQUIREMENT: [InformationType.REQUIREMENTS, InformationType.CONSTRAINTS],
    DocumentRole.ENGINEERING_DATA: [InformationType.REQUIREMENTS, InformationType.CONSTRAINTS],
    DocumentRole.DESIGN_NOTE: [InformationType.CONTROL_LOGIC],
    DocumentRole.CORRESPONDENCE: [InformationType.CORRESPONDENCE],
    DocumentRole.LEGACY_IMPLEMENTATION: [InformationType.LEGACY_IMPLEMENTATION, InformationType.CONTROL_LOGIC],
    DocumentRole.DATASHEET: [InformationType.REFERENCE_DATA],
    DocumentRole.COMMISSIONING: [InformationType.COMMISSIONING_DATA],
    DocumentRole.MEASUREMENT: [InformationType.MEASUREMENT_DATA],
    DocumentRole.ARCHITECTURE: [InformationType.ARCHITECTURE],
}


def classify_role(path: str) -> DocumentRole:
    lowered = path.lower()
    for pattern, role in _FOLDER_ROLE_RULES:
        if pattern.search(lowered):
            return role
    return DocumentRole.UNKNOWN


def classify_information_types(document: DocumentRecord, role: DocumentRole) -> list[InformationType]:
    info_types = set(_ROLE_INFO_TYPES.get(role, []))
    info_types.update(_EXTENSION_INFO_TYPES.get(document.extension, []))
    return sorted(info_types, key=lambda t: t.value)


def classify_documents(manifest: SourceManifest) -> SourceManifest:
    """Classify every document in place and return the same manifest."""

    for doc in manifest.documents:
        doc.role = classify_role(doc.path)
        doc.information_types = classify_information_types(doc, doc.role)
    return manifest
