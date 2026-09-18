"""Index builders. Mirrors `Document Agent.md`, Sections 19-24.

Indexes are navigation structures, not the semantic truth. `file_index`,
`information_type_index`, and `topic_index` are built right after
classification/parsing, deterministically. `entity_index`,
`requirement_index`, `relationship_index`, and `evidence_index` are built
after semantic extraction, from the `SemanticModel`.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from engineering_agent.schemas import Observation, SemanticModel, SourceManifest

# Deterministic keyword -> topic tagging. Extend as new domains are added;
# this never invents a topic that isn't literally present in the text.
_TOPIC_KEYWORDS: dict[str, str] = {
    r"\bco2\b": "CO2_CONTROL",
    r"\btemperature\b|\bdegc\b": "TEMPERATURE_CONTROL",
    r"\boccupan": "OCCUPANCY",
    r"\bflux\b|\bmagnetic\b|\breluctance\b": "MAGNETIC_CIRCUIT",
    r"\bnacl\b|\bevaporat": "EVAPORATION_PROCESS",
    r"\btank\b|\blevel\b": "TANK_LEVEL_CONTROL",
    r"\bvalve\b|\bpump\b": "FLUID_ACTUATION",
    r"\bcommissioning\b|\bacceptance\b": "COMMISSIONING",
}
_COMPILED_TOPIC_KEYWORDS = [(re.compile(pattern, re.IGNORECASE), topic) for pattern, topic in _TOPIC_KEYWORDS.items()]


def build_file_index(manifest: SourceManifest, observations: list[Observation]) -> dict[str, dict]:
    obs_by_doc: dict[str, list[Observation]] = defaultdict(list)
    for obs in observations:
        obs_by_doc[obs.document_id].append(obs)

    index: dict[str, dict] = {}
    for doc in manifest.documents:
        topics = _topics_in_text("\n".join(o.content for o in obs_by_doc.get(doc.document_id, [])))
        index[doc.document_id] = {
            "path": doc.path,
            "role": doc.role.value,
            "topics": sorted(topics),
            "contains": [t.value for t in doc.information_types],
        }
    return index


def build_topic_index(manifest: SourceManifest, observations: list[Observation]) -> dict[str, dict]:
    obs_by_doc: dict[str, list[Observation]] = defaultdict(list)
    for obs in observations:
        obs_by_doc[obs.document_id].append(obs)

    topic_docs: dict[str, set[str]] = defaultdict(set)
    for doc in manifest.documents:
        text = "\n".join(o.content for o in obs_by_doc.get(doc.document_id, []))
        for topic in _topics_in_text(text):
            topic_docs[topic].add(doc.document_id)
    return {topic: {"documents": sorted(doc_ids)} for topic, doc_ids in topic_docs.items()}


def build_information_type_index(manifest: SourceManifest) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for doc in manifest.documents:
        for info_type in doc.information_types:
            index[info_type.value].append(doc.document_id)
    return dict(index)


def build_entity_index(model: SemanticModel) -> dict[str, dict]:
    return {
        entity.entity_id: {"name": entity.name, "type": entity.type, "evidence": entity.evidence}
        for entity in model.entities
    }


def build_requirement_index(model: SemanticModel) -> dict[str, dict]:
    evidence_by_id = {ev.evidence_id: ev for ev in model.evidence}
    index: dict[str, dict] = {}
    for req in model.requirements:
        index[req.requirement_id] = {
            "sources": [
                {"document_id": evidence_by_id[eid].document_id, **evidence_by_id[eid].location.model_dump(exclude_none=True)}
                for eid in req.evidence
                if eid in evidence_by_id
            ]
        }
    return index


def build_relationship_index(model: SemanticModel) -> dict[str, dict]:
    return {
        rel.relationship_id: {"source": rel.source, "target": rel.target, "type": rel.type, "evidence": rel.evidence}
        for rel in model.relationships
    }


def build_evidence_index(model: SemanticModel) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for ev in model.evidence:
        index[ev.fact_id].append(ev.evidence_id)
    return dict(index)


def _topics_in_text(text: str) -> set[str]:
    return {topic for pattern, topic in _COMPILED_TOPIC_KEYWORDS if pattern.search(text)}


def save_index(project_dir: Path, name: str, data: dict) -> None:
    path = project_dir / "index" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_index(project_dir: Path, name: str) -> dict:
    path = project_dir / "index" / f"{name}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
