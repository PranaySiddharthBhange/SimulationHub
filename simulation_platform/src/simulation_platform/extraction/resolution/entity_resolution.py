"""Entity resolution. Mirrors `Document Agent.md`, Section 30.

Entities are extracted per-document, so the same physical thing shows up
multiple times under different names (`AHU-01`, `AHU 1`, `AHU_01`). This
merges same-type, high-similarity entities into one canonical record and
flags same-name-but-different-type or borderline-similarity pairs as an
`Ambiguity` instead of guessing — never merge solely on name similarity.
"""

from __future__ import annotations

import re

from rapidfuzz import fuzz

from simulation_platform.extraction.extraction.id_sequence import IdSequence
from simulation_platform.schemas import Ambiguity, Assumption, Entity, ImpactLevel, Relationship

AUTO_MERGE_THRESHOLD = 88.0
POSSIBLE_MATCH_THRESHOLD = 70.0
EXACT_MATCH_THRESHOLD = 100.0

# Instrument/equipment tag codes (LT-101, TK-102, XV-103, PLC-101, ...) are
# short strings dominated by a shared numeric suffix. Plain token_sort_ratio
# scores "LT-101" vs "TK-101" at ~83/100 purely from the shared "101" — well
# above POSSIBLE_MATCH_THRESHOLD — even though LT (level transmitter) and TK
# (tank) are unrelated equipment classes. Verified empirically against the
# Tank golden dataset, which uses this tagging convention heavily (see
# DECISIONS.md). For tag-shaped names, compare the letter prefix only, and
# treat two tags with the same prefix but a different number as genuinely
# different instances — not a possible match — rather than letting the
# shared digits inflate the score.
_TAG_PATTERN = re.compile(r"^([A-Za-z]{1,6})[-_ ]?(\d{1,5})$")

# Real, standard ISA-5.1 / common P&ID tag-letter conventions -- every
# entry here is a prefix actually seen in this pipeline's own real
# datasets (Tank: TK/tank/T, V/XV/valve, LT, PLC, AI/DI/DO, PB, SRC/DRN),
# not a guessed or invented abbreviation list. Used ONLY to recognize when
# two DIFFERENTLY-prefixed tags plausibly name the SAME equipment CLASS
# (e.g. "TK" and "tank" both mean "tank") -- never to auto-merge across a
# genuine instance-number mismatch on its own (see `_similarity`'s own
# docstring for why that's still kept separate).
_TAG_CONCEPT_ALIASES: dict[str, str] = {
    "tk": "tank", "tank": "tank", "t": "tank",
    "v": "valve", "xv": "valve", "valve": "valve",
    "lt": "level_transmitter", "li": "level_transmitter",
    "plc": "controller", "controller": "controller",
    "ai": "analog_input", "ao": "analog_output",
    "di": "digital_input", "do": "digital_output",
    "pb": "pushbutton",
    "src": "source", "drn": "drain",
}


def _normalize(name: str) -> str:
    return re.sub(r"[\s_\-]+", " ", name.strip().lower())


def _tag_parts(name: str) -> tuple[str, str] | None:
    match = _TAG_PATTERN.match(name.strip())
    return (match.group(1).lower(), match.group(2)) if match else None


def _same_tag_concept(prefix_a: str, prefix_b: str) -> bool:
    if prefix_a == prefix_b:
        return False  # identical prefix is handled by the caller directly, not this "different spelling" path
    concept_a = _TAG_CONCEPT_ALIASES.get(prefix_a)
    return concept_a is not None and concept_a == _TAG_CONCEPT_ALIASES.get(prefix_b)


def _is_tag_concept_match(name_a: str, name_b: str) -> bool:
    """True when both names are tag-shaped and recognizably name the same
    equipment CLASS under a different prefix spelling (e.g. "TK-101" vs
    "tank1") -- a much stronger, more targeted signal than an ordinary
    fuzzy-text borderline match, since it isn't just "these strings look
    similar," it's "these are two real, known ways of writing the same
    kind of equipment tag." Used to escalate this specific ambiguity to
    `ImpactLevel.HIGH` (real live interrupt) instead of the generic `LOW`
    a coincidental fuzzy-name match gets -- found live: an ordinary `LOW`
    ambiguity is recorded but never surfaces to a human, which is exactly
    how 6 duplicate entities for 2 real tanks made it all the way through
    to a generated, partially-frozen Modelica model unnoticed."""

    tag_a, tag_b = _tag_parts(name_a), _tag_parts(name_b)
    if not (tag_a and tag_b):
        return False
    return _same_tag_concept(tag_a[0], tag_b[0])


def _similarity(name_a: str, name_b: str) -> float:
    tag_a, tag_b = _tag_parts(name_a), _tag_parts(name_b)
    if tag_a and tag_b:
        prefix_a, number_a = tag_a
        prefix_b, number_b = tag_b
        same_concept = _same_tag_concept(prefix_a, prefix_b)
        if number_a != number_b:
            # Found live on a real dataset: this used to unconditionally
            # return 0.0 here ("different instance numbers -> different
            # equipment, whatever the prefix") -- which correctly keeps
            # "TK-101" and "TK-102" apart (same prefix, genuinely
            # different serial numbers), but ALSO wrongly forced "TK-101"
            # and "tank1"/"T1" permanently apart, even though those are
            # informal short forms of the SAME tag using a different
            # numbering convention (a sequential index, not the full
            # instrument tag number). That silent, overconfident "these
            # are different" produced 6 duplicate entities standing in
            # for 2 real tanks in one generated model. Never silently
            # MERGE across a genuine number mismatch either (a different
            # number could be a real, separate, undocumented instance) --
            # only escalate to a disclosed ambiguity when the prefixes
            # recognizably name the same equipment class.
            return POSSIBLE_MATCH_THRESHOLD if same_concept else 0.0
        if same_concept:
            # Same instance number AND a recognized same equipment
            # concept under different spelling (e.g. "valve1" vs "V1") --
            # found live: `fuzz.ratio("valve", "v")` scores only ~33/100,
            # well below even the ambiguity threshold, silently keeping a
            # real alias pair as two separate entities. This is a strong,
            # safe signal to auto-merge -- unlike the cross-number case,
            # there's no risk of conflating two genuinely different
            # instances here.
            return AUTO_MERGE_THRESHOLD
        return float(fuzz.ratio(prefix_a, prefix_b))
    return float(fuzz.token_sort_ratio(_normalize(name_a), _normalize(name_b)))


class EntityResolutionResult:
    def __init__(
        self,
        resolved_entities: list[Entity],
        id_remap: dict[str, str],
        ambiguities: list[Ambiguity],
        assumptions: list[Assumption],
    ):
        self.resolved_entities = resolved_entities
        self.id_remap = id_remap  # original entity_id -> canonical entity_id
        self.ambiguities = ambiguities
        self.assumptions = assumptions


def resolve_entities(entities: list[Entity], id_seq: IdSequence) -> EntityResolutionResult:
    canonical_groups: list[list[Entity]] = []
    ambiguities: list[Ambiguity] = []
    assumptions: list[Assumption] = []

    for entity in entities:
        placed = False
        for group in canonical_groups:
            representative = group[0]
            score = _similarity(entity.name, representative.name)

            if representative.type != entity.type:
                # An EXACT name match ("LT-101" == "LT-101") worded as two different
                # types is not a borderline case -- it's the same real-world tag
                # described two ways across documents (confirmed live: ENT-0007
                # "LT-101"/"LevelMeasurement" and ENT-0013 "LT-101"/"Level
                # transmitter" were the same physical sensor -- this pattern alone
                # occurred 24+ times on the real Tank dataset, per the type-mismatch
                # ambiguity this branch used to log unconditionally instead of ever
                # merging). Leaving them permanently separate produced a redundant,
                # empty downstream Modelica stub for every one of those 24+ cases.
                # Auto-merge on an exact name match regardless of type wording, but
                # keep it a reviewable Assumption, never a silent guess. A merely
                # SIMILAR (not exact) name with a type mismatch is still a genuine
                # judgment call -- that stays an Ambiguity, not auto-merged.
                if score >= EXACT_MATCH_THRESHOLD:
                    assumptions.append(
                        Assumption(
                            assumption_id=f"A-{len(assumptions) + 1:04d}",
                            statement=(
                                f"'{entity.name}' ({entity.type}) is treated as the same entity as "
                                f"'{representative.name}' ({representative.type}) — identical name, "
                                f"different type wording across documents."
                            ),
                            status="PROPOSED",
                            requires_confirmation=True,
                            affects=[entity.entity_id, representative.entity_id],
                        )
                    )
                    group.append(entity)
                    placed = True
                    break
                if score >= POSSIBLE_MATCH_THRESHOLD:
                    ambiguities.append(
                        Ambiguity(
                            ambiguity_id=f"AMB-{len(ambiguities) + 1:04d}",
                            question=(
                                f"'{entity.name}' ({entity.type}) and '{representative.name}' "
                                f"({representative.type}) look similar but have different types — same entity?"
                            ),
                            candidates=["SAME_ENTITY", "DIFFERENT_ENTITY"],
                            impact=ImpactLevel.MEDIUM,
                            affects=[entity.entity_id, representative.entity_id],
                        )
                    )
                continue

            if score >= AUTO_MERGE_THRESHOLD:
                if score < EXACT_MATCH_THRESHOLD:
                    assumptions.append(
                        Assumption(
                            assumption_id=f"A-{len(assumptions) + 1:04d}",
                            statement=(
                                f"'{entity.name}' is treated as the same {entity.type} as "
                                f"'{representative.name}' (name-similarity {score:.0f}/100)."
                            ),
                            status="PROPOSED",
                            requires_confirmation=True,
                            affects=[entity.entity_id, representative.entity_id],
                        )
                    )
                group.append(entity)
                placed = True
                break
            if score >= POSSIBLE_MATCH_THRESHOLD:
                ambiguities.append(
                    Ambiguity(
                        ambiguity_id=f"AMB-{len(ambiguities) + 1:04d}",
                        question=f"Is '{entity.name}' the same {entity.type} as '{representative.name}'?",
                        candidates=["SAME_ENTITY", "DIFFERENT_ENTITY"],
                        impact=(
                            ImpactLevel.HIGH if _is_tag_concept_match(entity.name, representative.name)
                            else ImpactLevel.LOW
                        ),
                        affects=[entity.entity_id, representative.entity_id],
                    )
                )

        if not placed:
            canonical_groups.append([entity])

    resolved_entities: list[Entity] = []
    id_remap: dict[str, str] = {}
    for group in canonical_groups:
        canonical_id = id_seq.next("ENT")
        primary = group[0]
        merged_aliases = sorted({alias for member in group for alias in (*member.aliases, member.name)} - {primary.name})
        merged_evidence = sorted({ev for member in group for ev in member.evidence})
        resolved_entities.append(
            Entity(
                entity_id=canonical_id,
                name=primary.name,
                type=primary.type,
                status=primary.status,
                evidence=merged_evidence,
                aliases=merged_aliases,
            )
        )
        for member in group:
            id_remap[member.entity_id] = canonical_id

    return EntityResolutionResult(resolved_entities, id_remap, ambiguities, assumptions)


def remap_relationship_endpoints(relationships: list[Relationship], id_remap: dict[str, str]) -> list[Relationship]:
    """Rewrite `source`/`target` on every relationship to point at canonical (post-merge) entity ids."""

    for relationship in relationships:
        relationship.source = id_remap.get(relationship.source, relationship.source)
        relationship.target = id_remap.get(relationship.target, relationship.target)
    return relationships


# Relationship types that are inherently SYMMETRIC in meaning -- "A
# connected_to B" and "B connected_to A" state the identical physical
# fact, so they dedupe as an UNORDERED pair. Every other type defaults to
# directional (the safe default: never silently conflate two directional
# facts that genuinely differ by order, e.g. "A controls B" is not "B
# controls A").
_SYMMETRIC_RELATIONSHIP_TYPES = {"connected_to", "mutually_exclusive"}


def deduplicate_relationships(relationships: list[Relationship]) -> list[Relationship]:
    """Runs AFTER `remap_relationship_endpoints` -- merges relationship
    records that describe the exact same real fact (combining their
    evidence) into one. Entity resolution's own id remapping collapses
    NAME aliases, but does nothing about the resulting duplicate
    RELATIONSHIP records that now all point at the same canonical entity
    pair: the same real physical connection is often extracted once per
    document that mentions it, sometimes with source/target reversed.

    Found live on a real dataset: a valve's own two ports both ended up
    connected to the SAME tank in the generated Modelica model, because
    "valve1 -> tank1" and "tank1 -> valve1" (reversed, extracted from two
    different documents) both survived id-remapping as two separate
    `connected_to` facts between the same two canonical entities --
    `modelica_gen/generation/modelica_generator.py`'s deterministic
    connection matcher has no way to know they're the same real link, so
    it consumed a fresh port on both sides for each one."""

    merged_by_key: dict[tuple, Relationship] = {}
    order: list[tuple] = []
    for rel in relationships:
        key = (
            (rel.type, frozenset({rel.source, rel.target}))
            if rel.type in _SYMMETRIC_RELATIONSHIP_TYPES
            else (rel.type, rel.source, rel.target)
        )
        existing = merged_by_key.get(key)
        if existing is None:
            merged_by_key[key] = rel
            order.append(key)
        else:
            existing.evidence = sorted(set(existing.evidence) | set(rel.evidence))

    return [merged_by_key[key] for key in order]

