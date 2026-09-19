"""Everything in the pipeline that does NOT require an LLM call.

This is deliberately comprehensive: it is the "does this actually work"
check that can run with no OPENAI_API_KEY at all. Semantic extraction and
the Deep Agent (which genuinely need a model) are exercised separately in
`test_llm_dependent.py`, which skips itself when no key is configured.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from simulation_platform.extraction.evidence.evidence_manager import load_evidence, save_evidence
from simulation_platform.extraction.extraction.id_sequence import IdSequence
from simulation_platform.extraction.observations.observation_store import append_observations, load_observations
from simulation_platform.extraction.reconciliation.conflict_engine import detect_and_resolve_conflicts
from simulation_platform.extraction.reconciliation.precedence_rules import PrecedencePolicy
from simulation_platform.extraction.resolution.entity_resolution import (
    deduplicate_relationships,
    remap_relationship_endpoints,
    resolve_entities,
)
from simulation_platform.schemas import (
    Ambiguity,
    Assumption,
    Comparator,
    Conflict,
    ConflictStatus,
    Decision,
    DocumentRecord,
    DocumentRole,
    Entity,
    Evidence,
    EvidenceType,
    FactStatus,
    ImpactLevel,
    Observation,
    ObservationType,
    ParseStatus,
    ProjectManifest,
    ProjectStatus,
    Relationship,
    Requirement,
    SemanticModel,
    SourceLocation,
    SourceManifest,
    Unknown,
)
from simulation_platform.extraction.storage.artifacts import (
    load_ambiguities,
    load_decisions,
    load_semantic_model,
    publish_version,
    save_ambiguities,
    save_assumptions,
    save_conflicts,
    save_decisions,
    save_semantic_model,
    save_unknowns,
)
from simulation_platform.extraction.uncertainty.unknown_detector import detect_unknowns


# ---------------------------------------------------------------------------
# Observation store
# ---------------------------------------------------------------------------


def test_observation_store_roundtrip(tmp_path: Path) -> None:
    obs = [
        Observation(
            observation_id="obs_0001",
            document_id="doc_0001",
            type=ObservationType.TEXT,
            content="Zone temperature shall remain between 20 and 24 degC.",
            location=SourceLocation(page=8),
            parser="pdf_parser",
        )
    ]
    append_observations(tmp_path, obs)
    append_observations(tmp_path, obs)  # append-only: calling twice should not clobber the first batch
    loaded = load_observations(tmp_path)
    assert len(loaded) == 2
    assert loaded[0] == obs[0]


# ---------------------------------------------------------------------------
# Entity resolution (rapidfuzz-based, no LLM)
# ---------------------------------------------------------------------------


def test_entity_resolution_merges_near_duplicates_but_not_abbreviations() -> None:
    entities = [
        Entity(entity_id="tmp1", name="AHU-01", type="AirHandlingUnit", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Entity(entity_id="tmp2", name="AHU_01", type="AirHandlingUnit", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
        Entity(entity_id="tmp3", name="Air Handling Unit 1", type="AirHandlingUnit", status=FactStatus.EXPLICIT, evidence=["EV-3"]),
        Entity(entity_id="tmp4", name="Damper-01", type="Damper", status=FactStatus.EXPLICIT, evidence=["EV-4"]),
    ]

    result = resolve_entities(entities, IdSequence())

    # AHU-01 / AHU_01 differ only by punctuation (name-similarity 100) and merge cleanly.
    # "Air Handling Unit 1" is an abbreviation expansion, not a typo/reordering — pure
    # string-similarity correctly does NOT merge it (Section 30: never merge on name
    # similarity alone). Resolving that case needs the LLM-assisted path, tested
    # separately once a model is configured.
    assert len(result.resolved_entities) == 3  # {AHU-01, AHU_01}, "Air Handling Unit 1", Damper-01
    assert result.id_remap["tmp1"] == result.id_remap["tmp2"]
    assert result.id_remap["tmp3"] not in (result.id_remap["tmp1"],)
    assert result.id_remap["tmp4"] != result.id_remap["tmp1"]

    merged_ahu = next(e for e in result.resolved_entities if e.entity_id == result.id_remap["tmp1"])
    assert merged_ahu.aliases == ["AHU_01"]
    assert sorted(merged_ahu.evidence) == ["EV-1", "EV-2"]
    assert result.assumptions == []  # exact normalized match (score 100) needs no recorded assumption


def test_entity_resolution_merges_an_exact_name_type_mismatch_as_a_reviewable_assumption() -> None:
    # An IDENTICAL name (e.g. the same instrument tag, "LT-101") with a type
    # mismatch is almost always a type-label wording difference, not a real
    # tag collision — confirmed live on the real Tank dataset (see
    # DECISIONS.md): ENT-0007 ("LT-101"/"LevelMeasurement") and ENT-0013
    # ("LT-101"/"Level transmitter") were the same physical sensor, but an
    # earlier version of this resolver never merged across a type mismatch
    # at all (only logging a non-blocking ambiguity), which happened 24+
    # times on that one dataset and produced a redundant, empty downstream
    # Modelica stub for every one of those 24+ cases. Now: an EXACT name
    # match auto-merges even across a type wording difference, but stays a
    # reviewable Assumption, never a silent guess. A merely SIMILAR (not
    # exact) name with a type mismatch is still a genuine judgment call —
    # see `test_entity_resolution_flags_fuzzy_name_type_mismatch_as_medium_impact_ambiguity`.
    entities = [
        Entity(entity_id="tmp1", name="Controller-01", type="Controller", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Entity(entity_id="tmp2", name="Controller-01", type="Damper", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    result = resolve_entities(entities, IdSequence())
    assert len(result.resolved_entities) == 1
    assert result.id_remap["tmp1"] == result.id_remap["tmp2"]
    assert len(result.assumptions) == 1
    assert result.assumptions[0].requires_confirmation is True
    assert result.ambiguities == []


def test_entity_resolution_flags_fuzzy_name_type_mismatch_as_medium_impact_ambiguity() -> None:
    entities = [
        Entity(entity_id="tmp1", name="Controller-01", type="Controller", status=FactStatus.EXPLICIT, evidence=[]),
        Entity(entity_id="tmp2", name="Controller_01A", type="Damper", status=FactStatus.EXPLICIT, evidence=[]),
    ]
    result = resolve_entities(entities, IdSequence())
    assert len(result.resolved_entities) == 2
    assert len(result.ambiguities) == 1
    assert result.ambiguities[0].impact == ImpactLevel.MEDIUM


def test_entity_resolution_does_not_confuse_tag_codes_sharing_a_number() -> None:
    # Real bug found running the Document Agent live on the Tank dataset:
    # "LT-101" vs "TK-101" vs "PLC-101" vs "SRC-101" all share the "-101"
    # suffix, which inflated plain token_sort_ratio to ~77-83/100 — well
    # above POSSIBLE_MATCH_THRESHOLD — despite LT/TK/PLC/SRC being unrelated
    # equipment classes. None of these should be merged OR flagged ambiguous.
    entities = [
        Entity(entity_id="tmp1", name="LT-101", type="LevelMeasurement", status=FactStatus.EXPLICIT, evidence=[]),
        Entity(entity_id="tmp2", name="TK-101", type="Tank", status=FactStatus.EXPLICIT, evidence=[]),
        Entity(entity_id="tmp3", name="PLC-101", type="Controller", status=FactStatus.EXPLICIT, evidence=[]),
        Entity(entity_id="tmp4", name="SRC-101", type="BoundarySource", status=FactStatus.EXPLICIT, evidence=[]),
        # Same instrument class, different instance number -> also not a match.
        Entity(entity_id="tmp5", name="LT-102", type="LevelMeasurement", status=FactStatus.EXPLICIT, evidence=[]),
    ]
    result = resolve_entities(entities, IdSequence())
    assert len(result.resolved_entities) == 5  # every tag stays its own entity
    assert result.ambiguities == []
    assert result.id_remap["tmp1"] != result.id_remap["tmp2"] != result.id_remap["tmp3"] != result.id_remap["tmp4"]
    assert result.id_remap["tmp1"] != result.id_remap["tmp5"]


def test_entity_resolution_still_merges_identical_tags() -> None:
    entities = [
        Entity(entity_id="tmp1", name="LT-101", type="LevelMeasurement", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Entity(entity_id="tmp2", name="LT-101", type="LevelMeasurement", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    result = resolve_entities(entities, IdSequence())
    assert len(result.resolved_entities) == 1
    assert result.id_remap["tmp1"] == result.id_remap["tmp2"]


def test_entity_resolution_flags_a_cross_convention_tank_alias_as_ambiguity() -> None:
    """Real bug found running a genuinely full Stage 1+2+3 pipeline live:
    the SAME two physical tanks were extracted as SIX separate entities
    ("TK-101"/"tank1"/"T1" for Tank 1, and the "TK-102"/"tank2"/"T2"
    equivalents), because the tag-number heuristic unconditionally
    returned 0.0 ("definitely different") the moment the NUMBERS differed
    (101 vs 1), without ever checking whether "tk"/"tank"/"t" name the
    SAME real equipment class. This produced a generated Modelica model
    with 6 `OpenTank` instances standing in for 2 real tanks -- most
    frozen/disconnected duplicates, only one real pair actually wired
    into the flow network. Never silently auto-merge across a genuine
    number mismatch (a different number COULD be a real, separate,
    undocumented instance) -- but it must become a real, disclosed
    ambiguity, not a silent duplicate."""

    entities = [
        Entity(entity_id="tmp1", name="TK-101", type="Tank", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Entity(entity_id="tmp2", name="tank1", type="Tank", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
        Entity(entity_id="tmp3", name="T1", type="Tank", status=FactStatus.EXPLICIT, evidence=["EV-3"]),
    ]
    result = resolve_entities(entities, IdSequence())

    # Not silently merged with "TK-101" across the real number mismatch --
    # but "tank1" and "T1" DO share the same number ("1") under the same
    # recognized concept, so those two safely auto-merge with each other
    # (see the dedicated same-number test below); "TK-101" stays its own,
    # separate, still-unresolved entity, flagged via two real ambiguities.
    assert len(result.resolved_entities) == 2
    assert len(result.ambiguities) == 2  # tmp2 vs tmp1, tmp3 vs tmp1
    # A generic fuzzy-range match is recorded at LOW impact and never
    # surfaces to a human -- exactly how this duplicate slipped through
    # undetected before. This specific, targeted signal must be real,
    # visible HIGH impact instead.
    assert all(a.impact == ImpactLevel.HIGH for a in result.ambiguities)


def test_entity_resolution_still_separates_genuinely_different_tag_numbers() -> None:
    """The exact regression this fix must not reintroduce: "TK-101" and
    "TK-102" share the identical recognized prefix ("tk") but are
    genuinely different tank instances -- must stay completely separate,
    with no ambiguity raised either (an IDENTICAL prefix with a different
    number is the standard "next serial number" pattern, not a plausible
    alias)."""

    entities = [
        Entity(entity_id="tmp1", name="TK-101", type="Tank", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Entity(entity_id="tmp2", name="TK-102", type="Tank", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    result = resolve_entities(entities, IdSequence())

    assert len(result.resolved_entities) == 2
    assert result.ambiguities == []
    assert result.id_remap["tmp1"] != result.id_remap["tmp2"]


def test_entity_resolution_auto_merges_a_same_numbered_abbreviation_alias() -> None:
    """Real bug found live: "valve1" and "V1" (the SAME instance number,
    just spelled differently) scored only ~33/100 under plain prefix
    `fuzz.ratio` ("valve" vs "v") -- below even the ambiguity threshold,
    so they silently stayed as two separate entities. Same recognized
    equipment concept AND the same instance number is a safe, unambiguous
    auto-merge -- unlike the cross-number case, there's no risk of
    conflating two genuinely different instances here."""

    entities = [
        Entity(entity_id="tmp1", name="valve1", type="Valve", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Entity(entity_id="tmp2", name="V1", type="Valve", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    result = resolve_entities(entities, IdSequence())

    assert len(result.resolved_entities) == 1
    assert result.id_remap["tmp1"] == result.id_remap["tmp2"]


def test_remap_relationship_endpoints() -> None:
    relationships = [Relationship(relationship_id="REL-1", source="tmp1", target="tmp4", type="controls", status=FactStatus.EXPLICIT)]
    remapped = remap_relationship_endpoints(relationships, {"tmp1": "ENT-0001", "tmp4": "ENT-0002"})
    assert remapped[0].source == "ENT-0001"
    assert remapped[0].target == "ENT-0002"


def test_deduplicate_relationships_merges_a_reversed_symmetric_pair() -> None:
    """Real bug found live: "valve1 -> tank1" and "tank1 -> valve1"
    (the same physical connection, extracted from two different documents
    with source/target reversed) both survived entity-resolution's id
    remapping as two separate `connected_to` facts between the same
    canonical pair -- so the Modelica generator's deterministic connection
    matcher consumed a fresh port on both sides for each one, wiring both
    of the valve's ports to the same tank (a zero-driving-pressure
    self-loop)."""

    relationships = [
        Relationship(relationship_id="REL-1", source="ENT-VALVE", target="ENT-TANK", type="connected_to", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Relationship(relationship_id="REL-2", source="ENT-TANK", target="ENT-VALVE", type="connected_to", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    deduped = deduplicate_relationships(relationships)

    assert len(deduped) == 1
    assert sorted(deduped[0].evidence) == ["EV-1", "EV-2"]


def test_deduplicate_relationships_keeps_directional_types_separate_by_order() -> None:
    """`controls`/`supplies`-style directional facts must never merge just
    because the same two entities are involved in reverse order -- "A
    controls B" and "B controls A" are genuinely different claims."""

    relationships = [
        Relationship(relationship_id="REL-1", source="ENT-A", target="ENT-B", type="controls", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Relationship(relationship_id="REL-2", source="ENT-B", target="ENT-A", type="controls", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    deduped = deduplicate_relationships(relationships)

    assert len(deduped) == 2


def test_deduplicate_relationships_merges_identical_directional_duplicates() -> None:
    """The same directional fact extracted twice (same order, e.g. from two
    documents both mentioning it) is a genuine duplicate and must merge,
    combining evidence."""

    relationships = [
        Relationship(relationship_id="REL-1", source="ENT-A", target="ENT-B", type="controls", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
        Relationship(relationship_id="REL-2", source="ENT-A", target="ENT-B", type="controls", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
    ]
    deduped = deduplicate_relationships(relationships)

    assert len(deduped) == 1
    assert sorted(deduped[0].evidence) == ["EV-1", "EV-2"]


# ---------------------------------------------------------------------------
# Conflict engine + precedence (deterministic)
# ---------------------------------------------------------------------------


def _doc(document_id: str, role: DocumentRole, modified_time: str) -> DocumentRecord:
    return DocumentRecord(
        document_id=document_id,
        path=f"{document_id}.txt",
        filename=f"{document_id}.txt",
        extension=".txt",
        size=1,
        sha256="x",
        modified_time=modified_time,
        role=role,
    )


def test_conflict_engine_resolves_by_precedence_with_approved_email_override() -> None:
    manifest = SourceManifest(
        project_id="p1",
        documents=[
            _doc("doc_register", DocumentRole.ENGINEERING_DATA, "2026-01-01T00:00:00Z"),
            _doc("doc_email", DocumentRole.CORRESPONDENCE, "2026-02-14T00:00:00Z"),
        ],
    )
    req_register = Requirement(
        requirement_id="REQ-A", subject="Zone-01", property="CO2", operator=Comparator.LTE,
        max=1000, unit="ppm", status=FactStatus.EXPLICIT, evidence=["EV-A"],
    )
    req_email = Requirement(
        requirement_id="REQ-B", subject="Zone-01", property="CO2", operator=Comparator.LTE,
        max=900, unit="ppm", status=FactStatus.EXPLICIT, evidence=["EV-B"],
    )
    evidence = [
        Evidence(evidence_id="EV-A", fact_id="REQ-A", type=EvidenceType.EXPLICIT_TEXT, document_id="doc_register",
                  location=SourceLocation(sheet="Requirements"), quote="CO2 max 1000 ppm"),
        Evidence(evidence_id="EV-B", fact_id="REQ-B", type=EvidenceType.EMAIL, document_id="doc_email",
                  location=SourceLocation(section="message 1"),
                  quote="DR-IAQ-05 closed this today: owner intent is 900 ppm ABSOLUTE room concentration."),
    ]

    conflicts = detect_and_resolve_conflicts([req_register, req_email], evidence, manifest, PrecedencePolicy())

    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.status == ConflictStatus.RESOLVED
    assert conflict.superseded_by == "REQ-B"  # approved-decision email outranks the plain register entry
    assert req_email.status == FactStatus.CONFIRMED
    assert req_register.status == FactStatus.CONFLICTED
    # Neither requirement record is deleted or overwritten — both still exist with their original values.
    assert req_register.max == 1000
    assert req_email.max == 900


def test_conflict_engine_ignores_identical_duplicate_requirements() -> None:
    manifest = SourceManifest(project_id="p1", documents=[_doc("doc1", DocumentRole.PROJECT_REQUIREMENT, "2026-01-01T00:00:00Z")])
    req1 = Requirement(requirement_id="REQ-A", subject="Zone-01", property="CO2", operator=Comparator.LTE, max=1000, unit="ppm", status=FactStatus.EXPLICIT, evidence=[])
    req2 = Requirement(requirement_id="REQ-B", subject="zone-01", property="co2", operator=Comparator.LTE, max=1000, unit="ppm", status=FactStatus.EXPLICIT, evidence=[])
    conflicts = detect_and_resolve_conflicts([req1, req2], [], manifest)
    assert conflicts == []


def test_conflict_engine_does_not_confuse_differently_conditioned_requirements() -> None:
    # Real bug found running the Document Agent live on the Tank dataset:
    # "V2/V3 open together: prohibited" (condition="normal auto operation")
    # and "...: allowed" (condition="SHUT") are the same correct behavior
    # under two different named operating conditions, not a disagreement —
    # grouping must include `condition`, not just (subject, property).
    manifest = SourceManifest(project_id="p1", documents=[_doc("doc1", DocumentRole.PROJECT_REQUIREMENT, "2026-01-01T00:00:00Z")])
    req_auto = Requirement(
        requirement_id="REQ-091", subject="V2 and V3", property="commanded open together",
        operator=Comparator.EQ, value="prohibited", condition="normal auto operation",
        status=FactStatus.EXPLICIT, evidence=[],
    )
    req_shut = Requirement(
        requirement_id="REQ-092", subject="V2 and V3", property="commanded open together",
        operator=Comparator.EQ, value="allowed", condition="SHUT",
        status=FactStatus.EXPLICIT, evidence=[],
    )
    conflicts = detect_and_resolve_conflicts([req_auto, req_shut], [], manifest)
    assert conflicts == []
    assert req_auto.status == FactStatus.EXPLICIT  # neither status touched — no conflict to resolve
    assert req_shut.status == FactStatus.EXPLICIT


# ---------------------------------------------------------------------------
# Unknown detection
# ---------------------------------------------------------------------------


def test_unknown_detector_flags_missing_bounds() -> None:
    req_with_value = Requirement(requirement_id="REQ-1", subject="Zone-01", property="CO2", operator=Comparator.LTE, max=1000, unit="ppm", status=FactStatus.EXPLICIT, evidence=[])
    req_missing_value = Requirement(requirement_id="REQ-2", subject="AHU-01", property="supply_temperature", operator=Comparator.EQ, status=FactStatus.EXPLICIT, evidence=[])
    unknowns = detect_unknowns([req_with_value, req_missing_value], [])
    assert len(unknowns) == 1
    assert unknowns[0].entity == "AHU-01"
    assert unknowns[0].property == "supply_temperature"


# ---------------------------------------------------------------------------
# Persistence round-trips
# ---------------------------------------------------------------------------


def test_evidence_manager_roundtrip(tmp_path: Path) -> None:
    evidence = [Evidence(evidence_id="EV-1", fact_id="REQ-1", type=EvidenceType.EXPLICIT_TEXT, document_id="doc1", location=SourceLocation(page=1))]
    save_evidence(tmp_path, evidence)
    assert load_evidence(tmp_path) == evidence


def test_storage_artifacts_roundtrip(tmp_path: Path) -> None:
    conflicts = [Conflict(conflict_id="CONF-1", fact_ids=["REQ-1", "REQ-2"], description="x", status=ConflictStatus.OPEN)]
    ambiguities = [Ambiguity(ambiguity_id="AMB-1", question="q?", candidates=["a", "b"], impact=ImpactLevel.HIGH)]
    unknowns = [Unknown(unknown_id="UNK-1", property="p", entity="e", reason="r")]
    assumptions = [Assumption(assumption_id="A-1", statement="s")]
    decisions = [Decision(decision_id="DEC-1", question_id="AMB-1", question="q?", answer="a")]

    save_conflicts(tmp_path, conflicts)
    save_ambiguities(tmp_path, ambiguities)
    save_unknowns(tmp_path, unknowns)
    save_assumptions(tmp_path, assumptions)
    save_decisions(tmp_path, decisions)

    assert load_ambiguities(tmp_path) == ambiguities
    assert load_decisions(tmp_path) == decisions

    model = SemanticModel(model_version="v0001", project_id="p1", conflicts=conflicts, ambiguities=ambiguities)
    save_semantic_model(tmp_path, model)
    assert load_semantic_model(tmp_path) == model

    publish_version(tmp_path, "v0001", "test publish", parent=None)
    assert (tmp_path / "workspace" / "versions" / "v0001" / "version_metadata.json").exists()
    assert (tmp_path / "workspace" / "versions" / "current.json").exists()


def test_project_store_creates_full_layout(tmp_path: Path) -> None:
    from simulation_platform.extraction.storage.project_store import ProjectStore

    source = tmp_path / "source"
    (source / "sub").mkdir(parents=True)
    (source / "sub" / "a.txt").write_text("hello", encoding="utf-8")

    store = ProjectStore(tmp_path / "projects")
    manifest = store.create_project("proj1", "Project One", source)

    assert manifest.status == ProjectStatus.CREATED
    assert (store.source_original_dir("proj1") / "sub" / "a.txt").read_text(encoding="utf-8") == "hello"
    for sub in ("documents", "workspace/extracted", "workspace/versions", "workspace/reports"):
        assert (store.project_dir("proj1") / sub).is_dir()

    reloaded = store.load_manifest("proj1")
    assert reloaded == manifest
