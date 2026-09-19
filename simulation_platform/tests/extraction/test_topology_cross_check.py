"""Deterministic-only tests for `topology_cross_check.py` -- the LLM call
itself (`extract_holistic_topology`) isn't exercised here (needs
OPENAI_API_KEY); this covers `cross_check_topology`, the part that
actually decides what counts as a real discrepancy between the
independent holistic re-derivation and the already-resolved per-document
extraction.
"""

from __future__ import annotations

from simulation_platform.extraction.extraction.id_sequence import IdSequence
from simulation_platform.extraction.consolidation.topology_cross_check import (
    HolisticTopology,
    _HolisticComponent,
    _HolisticConnection,
    cross_check_topology,
)
from simulation_platform.schemas import Entity, FactStatus, ImpactLevel, Relationship


def _entity(entity_id: str, name: str) -> Entity:
    return Entity(entity_id=entity_id, name=name, type="Tank", status=FactStatus.EXPLICIT, evidence=["EV-1"])


def test_cross_check_flags_a_component_the_detailed_extraction_has_no_match_for() -> None:
    """The core case this whole mechanism exists for: an independent,
    holistic read of the source text notices a real component that the
    narrower, per-document extraction never produced an entity for --
    exactly the kind of silent gap no amount of patching a KNOWN bug
    signature would catch, since it's a NEW one."""

    holistic = HolisticTopology(components=[_HolisticComponent(name="Pump-2", type="Pump", evidence_observation_ids=["obs_1"])])
    canonical_entities = [_entity("ENT-001", "TK-101")]

    ambiguities = cross_check_topology(holistic, canonical_entities, [], IdSequence())

    assert len(ambiguities) == 1
    assert ambiguities[0].impact == ImpactLevel.HIGH
    assert "Pump-2" in ambiguities[0].question


def test_cross_check_does_not_flag_a_component_that_matches_via_the_same_tag_alias_logic() -> None:
    """"tank1" and "TK 1" name the SAME real tank under two different
    tagging conventions -- the agent must recognize that itself, the same
    way `entity_resolution.py` already does (this reuses that exact
    matching function), not raise a false "missing component" alarm just
    because the spelling differs."""

    holistic = HolisticTopology(components=[_HolisticComponent(name="tank1", type="Tank", evidence_observation_ids=["obs_1"])])
    canonical_entities = [_entity("ENT-001", "TK 1")]

    ambiguities = cross_check_topology(holistic, canonical_entities, [], IdSequence())

    assert ambiguities == []


def test_cross_check_flags_a_connection_the_detailed_extraction_never_captured() -> None:
    holistic = HolisticTopology(
        components=[
            _HolisticComponent(name="TK-101", type="Tank", evidence_observation_ids=["obs_1"]),
            _HolisticComponent(name="V-101", type="Valve", evidence_observation_ids=["obs_2"]),
        ],
        connections=[_HolisticConnection(source="TK-101", target="V-101", evidence_observation_ids=["obs_3"])],
    )
    canonical_entities = [_entity("ENT-001", "TK-101"), _entity("ENT-002", "V-101")]

    ambiguities = cross_check_topology(holistic, canonical_entities, [], IdSequence())

    assert len(ambiguities) == 1
    assert ambiguities[0].impact == ImpactLevel.HIGH
    assert set(ambiguities[0].affects) == {"ENT-001", "ENT-002"}


def test_cross_check_does_not_flag_a_connection_that_already_exists() -> None:
    holistic = HolisticTopology(
        components=[
            _HolisticComponent(name="TK-101", type="Tank", evidence_observation_ids=["obs_1"]),
            _HolisticComponent(name="V-101", type="Valve", evidence_observation_ids=["obs_2"]),
        ],
        connections=[_HolisticConnection(source="TK-101", target="V-101", evidence_observation_ids=["obs_3"])],
    )
    canonical_entities = [_entity("ENT-001", "TK-101"), _entity("ENT-002", "V-101")]
    canonical_relationships = [
        Relationship(relationship_id="REL-1", source="ENT-001", target="ENT-002", type="connected_to", status=FactStatus.EXPLICIT)
    ]

    ambiguities = cross_check_topology(holistic, canonical_entities, canonical_relationships, IdSequence())

    assert ambiguities == []


def test_cross_check_does_not_double_report_a_connection_whose_endpoint_is_already_unmatched() -> None:
    """An unmatched component is already its own ambiguity -- the
    connection touching it must not ALSO produce a second, redundant
    ambiguity about the same root cause."""

    holistic = HolisticTopology(
        components=[_HolisticComponent(name="TK-101", type="Tank", evidence_observation_ids=["obs_1"])],
        connections=[_HolisticConnection(source="TK-101", target="Pump-2", evidence_observation_ids=["obs_2"])],
    )
    canonical_entities = [_entity("ENT-001", "TK-101")]

    ambiguities = cross_check_topology(holistic, canonical_entities, [], IdSequence())

    assert len(ambiguities) == 1
    assert "Pump-2" in ambiguities[0].question  # only the missing-component ambiguity, no connection one
