"""In-memory retrieval over one project's published knowledge.

Mirrors `Document Agent.md`, Section 44 (Retrieval API). Downstream agents
never read `projects/<id>/` directly — they call these methods (exposed as
tools in `retrieval.tools`), which is what actually enforces that rule.

Backed by the JSON/JSONL files on disk rather than SQLite for this build —
same API, swappable backing store later without touching any caller.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from engineering_agent.ingestion.manifest import load_source_manifest
from engineering_agent.observations.observation_store import load_observations
from engineering_agent.schemas import DocumentRecord, Entity, Evidence, Observation, Requirement, SemanticModel
from engineering_agent.storage.artifacts import load_ambiguities, load_decisions, load_semantic_model


class ProjectKnowledge:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.manifest = load_source_manifest(project_dir)
        self.observations = load_observations(project_dir)
        self.model: SemanticModel = load_semantic_model(project_dir) or SemanticModel(
            model_version="v0000", project_id=self.manifest.project_id
        )

        self._doc_by_id = {doc.document_id: doc for doc in self.manifest.documents}
        self._entity_by_id = {ent.entity_id: ent for ent in self.model.entities}
        self._requirement_by_id = {req.requirement_id: req for req in self.model.requirements}
        self._evidence_by_id = {ev.evidence_id: ev for ev in self.model.evidence}

    # -- search --------------------------------------------------------

    def search_files(self, query: str) -> list[DocumentRecord]:
        q = query.lower()
        return [doc for doc in self.manifest.documents if q in doc.path.lower() or q in doc.filename.lower()]

    def search_entities(self, query: str) -> list[Entity]:
        q = query.lower()
        return [
            ent
            for ent in self.model.entities
            if q in ent.name.lower() or any(q in alias.lower() for alias in ent.aliases) or q in ent.type.lower()
        ]

    def search_requirements(self, query: str) -> list[Requirement]:
        q = query.lower()
        return [req for req in self.model.requirements if q in req.subject.lower() or q in req.property.lower()]

    # -- direct lookups --------------------------------------------------

    def get_entity(self, entity_id: str) -> Entity | None:
        return self._entity_by_id.get(entity_id)

    def get_requirement(self, requirement_id: str) -> Requirement | None:
        return self._requirement_by_id.get(requirement_id)

    def get_evidence(self, fact_id: str) -> list[Evidence]:
        return [ev for ev in self.model.evidence if ev.fact_id == fact_id]

    def get_source_section(self, document_id: str) -> list[Observation]:
        return [obs for obs in self.observations if obs.document_id == document_id]

    def get_conflicts(self) -> list[dict]:
        return [c.model_dump() for c in self.model.conflicts]

    def get_ambiguities(self) -> list[dict]:
        return [a.model_dump() for a in load_ambiguities(self.project_dir)]

    def get_unknowns(self) -> list[dict]:
        return [u.model_dump() for u in self.model.unknowns]

    def get_decisions(self) -> list[dict]:
        return [d.model_dump() for d in load_decisions(self.project_dir)]

    # -- datasets ---------------------------------------------------------

    def get_dataset_statistics(self, file: str) -> dict | None:
        for obs in self.observations:
            if obs.type.value == "DATASET_SUMMARY" and obs.location.file == file:
                import json

                return json.loads(obs.content)
        return None

    def get_dataset_rows(self, file: str, start: int = 0, end: int | None = None) -> list[dict]:
        frame = pd.read_csv(self.project_dir / "source" / "original" / file)
        return frame.iloc[start:end].to_dict(orient="records")
