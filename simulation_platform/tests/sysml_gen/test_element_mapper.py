"""Deterministic-only tests for `element_mapper.py`'s backstops -- the LLM
call itself (`_map_category`) isn't exercised here (needs OPENAI_API_KEY).
"""

from __future__ import annotations

from simulation_platform.schemas import EntityItem, FactStatus, SysMLConstruct, SysMLElementMapping
from simulation_platform.sysml_gen.mapping.element_mapper import _backfill_evidence, _deduplicate_names


def _entity(entity_id: str, evidence: list[str]) -> EntityItem:
    return EntityItem(id=entity_id, name=entity_id, type="Tank", status=FactStatus.EXPLICIT, evidence=evidence)


def _mapping(engineering_id: str, evidence: list[str]) -> SysMLElementMapping:
    return SysMLElementMapping(
        engineering_id=engineering_id, engineering_type="entity", sysml_construct=SysMLConstruct.PART_DEF,
        sysml_element_name=f"Part_{engineering_id}", package="Architecture", evidence=evidence,
    )


def test_backfill_evidence_copies_the_source_items_evidence_when_the_mapping_left_it_empty() -> None:
    """Found live on a real dataset: 413 of 420 real mappings came back
    with `evidence: []` even though every source item was given its own
    real evidence ids as prompt input -- the prompt instruction alone
    wasn't reliable enough, so this backstop guarantees it deterministically."""

    items = [_entity("ENT-001", ["EV-1", "EV-2"])]
    mappings = [_mapping("ENT-001", evidence=[])]

    result = _backfill_evidence(mappings, items)

    assert result[0].evidence == ["EV-1", "EV-2"]


def test_backfill_evidence_never_overwrites_evidence_the_model_actually_gave() -> None:
    items = [_entity("ENT-001", ["EV-1", "EV-2"])]
    mappings = [_mapping("ENT-001", evidence=["EV-9"])]

    result = _backfill_evidence(mappings, items)

    assert result[0].evidence == ["EV-9"]


def test_backfill_evidence_leaves_a_mapping_empty_when_the_source_item_has_no_evidence_either() -> None:
    """Never fabricates evidence that was never extracted in the first place."""

    items = [_entity("ENT-001", [])]
    mappings = [_mapping("ENT-001", evidence=[])]

    result = _backfill_evidence(mappings, items)

    assert result[0].evidence == []


def test_deduplicate_names_renames_a_collision_against_earlier_claimed_names() -> None:
    claimed = {("TK101", "Architecture")}
    mappings = [_mapping("ENT-002", evidence=["EV-1"])]
    mappings[0] = mappings[0].model_copy(update={"sysml_element_name": "TK101"})

    result = _deduplicate_names(mappings, claimed)

    assert result[0].sysml_element_name == "TK101_2"
