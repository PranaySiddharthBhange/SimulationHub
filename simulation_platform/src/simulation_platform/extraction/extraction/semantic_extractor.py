"""Semantic extraction orchestration. Mirrors `Document Agent.md`, Section 25.

Runs one document's observations through entity -> relationship ->
requirement -> behavior -> constraint extraction, in that order (later
stages reference entities the earlier stage just found), and builds the
`Evidence` records that tie every extracted fact back to its observation.
Never sends more than one document's observations to a single LLM call.
"""

from __future__ import annotations

from simulation_platform.schemas import (
    DocumentRecord,
    Evidence,
    EvidenceType,
    Observation,
    SemanticModel,
    SourceManifest,
)

from .behavior_extractor import extract_behaviors
from .constraint_extractor import extract_constraints
from .control_law_extractor import extract_control_laws
from .entity_extractor import extract_entities
from .id_sequence import IdSequence
from .relationship_extractor import extract_relationships
from .requirement_extractor import extract_requirements
from .schedule_extractor import extract_scheduled_commands

_OBS_TYPE_TO_EVIDENCE_TYPE = {
    "TEXT": EvidenceType.EXPLICIT_TEXT,
    "TABLE": EvidenceType.TABLE_CELL,
    "CELL": EvidenceType.TABLE_CELL,
    "JSON_VALUE": EvidenceType.JSON_VALUE,
    "CODE": EvidenceType.CODE,
    "DIAGRAM_RELATION": EvidenceType.DIAGRAM_RELATION,
    "EMAIL_MESSAGE": EvidenceType.EMAIL,
}


def extract_semantic_model(
    project_id: str,
    manifest: SourceManifest,
    observations: list[Observation],
    model_version: str = "v0001",
) -> SemanticModel:
    obs_by_doc: dict[str, list[Observation]] = {}
    for obs in observations:
        obs_by_doc.setdefault(obs.document_id, []).append(obs)

    obs_by_id = {obs.observation_id: obs for obs in observations}

    id_seq = IdSequence()
    model = SemanticModel(model_version=model_version, project_id=project_id)

    for document in manifest.documents:
        doc_observations = obs_by_doc.get(document.document_id, [])
        if not doc_observations:
            continue

        entities = extract_entities(document, doc_observations, id_seq)
        relationships = extract_relationships(document, doc_observations, entities, id_seq)
        requirements = extract_requirements(document, doc_observations, id_seq)
        behaviors = extract_behaviors(document, doc_observations, id_seq)
        constraints = extract_constraints(document, doc_observations, id_seq)
        control_laws = extract_control_laws(document, doc_observations, id_seq)
        scheduled_commands = extract_scheduled_commands(document, doc_observations, id_seq)

        model.entities.extend(entities)
        model.relationships.extend(relationships)
        model.requirements.extend(requirements)
        model.behaviors.extend(behaviors)
        model.constraints.extend(constraints)
        model.control_laws.extend(control_laws)
        model.scheduled_commands.extend(scheduled_commands)

        for fact in (
            *entities, *relationships, *requirements, *behaviors, *constraints, *control_laws, *scheduled_commands,
        ):
            fact_id = _fact_id(fact)
            observation_ids = fact.evidence  # extractors populate this with cited observation ids
            evidence_ids: list[str] = []
            for obs_id in observation_ids:
                obs = obs_by_id.get(obs_id)
                if obs is None:
                    continue  # LLM cited an id that doesn't exist — drop rather than fabricate evidence
                evidence_record = Evidence(
                    evidence_id=id_seq.next("EV"),
                    fact_id=fact_id,
                    type=_OBS_TYPE_TO_EVIDENCE_TYPE.get(obs.type.value, EvidenceType.EXPLICIT_TEXT),
                    document_id=obs.document_id,
                    location=obs.location,
                    quote=obs.content[:500],
                )
                model.evidence.append(evidence_record)
                evidence_ids.append(evidence_record.evidence_id)
            # Replace observation-id citations with real evidence-record ids, per Agent Contracts.md.
            fact.evidence = evidence_ids

    return model


def _fact_id(fact) -> str:
    for attr in (
        "entity_id", "relationship_id", "requirement_id", "behavior_id", "constraint_id", "control_law_id",
        "command_id",
    ):
        if hasattr(fact, attr):
            return getattr(fact, attr)
    raise TypeError(f"Unrecognized fact type: {type(fact)!r}")
