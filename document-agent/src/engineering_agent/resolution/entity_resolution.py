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

from engineering_agent.extraction.id_sequence import IdSequence
from engineering_agent.schemas import Ambiguity, Assumption, Entity, ImpactLevel, Relationship

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


def _normalize(name: str) -> str:
    return re.sub(r"[\s_\-]+", " ", name.strip().lower())


def _tag_parts(name: str) -> tuple[str, str] | None:
    match = _TAG_PATTERN.match(name.strip())
    return (match.group(1).lower(), match.group(2)) if match else None


def _similarity(name_a: str, name_b: str) -> float:
    tag_a, tag_b = _tag_parts(name_a), _tag_parts(name_b)
    if tag_a and tag_b:
        prefix_a, number_a = tag_a
        prefix_b, number_b = tag_b
        if number_a != number_b:
            return 0.0  # different instance numbers -> different equipment, whatever the prefix
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
                # Deliberately MEDIUM even for an exact name match ("LT-101" == "LT-101"
                # worded as two different types) — tried HIGH first, but on the real Tank
                # dataset that alone produced 24+ HIGH-impact ambiguities (independent
                # per-document extraction routinely re-words the same tag's type), which
                # forces a HITL pause on essentially every multi-document project. Section
                # 37's HIGH bar is for genuine judgment calls, not "the same tag got
                # described two ways" — that's a real ambiguity worth recording, not one
                # that should block the pipeline. See DECISIONS.md / AI-LOG.md.
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
                        impact=ImpactLevel.LOW,
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

