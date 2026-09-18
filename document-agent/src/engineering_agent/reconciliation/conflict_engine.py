"""Conflict detection and resolution. Mirrors `Document Agent.md`, Sections 31 and 33.

Groups requirements that constrain the same (subject, property, condition)
and, when their bounds actually disagree, resolves the conflict by source
precedence — but never deletes the losing claim. Every requirement record
survives; only its `status` changes (`CONFIRMED` for the winner,
`CONFLICTED` for the rest), and a `Conflict` record preserves the full trail.

Real bug found running the Document Agent live on the Tank dataset:
grouping used to ignore `condition` entirely, so "V2/V3 open together:
prohibited (condition='normal auto operation')" and "...: allowed
(condition='SHUT')" were compared as competing claims about the same rule
and flagged as a false conflict — they are the same correct behavior under
two different named operating conditions, not a disagreement. Two
requirements only compete when they share subject, property, AND
condition.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from engineering_agent.schemas import (
    Conflict,
    ConflictStatus,
    DocumentRole,
    Evidence,
    FactStatus,
    Requirement,
    SourceManifest,
)

from .precedence_rules import PrecedencePolicy


def _bounds_key(req: Requirement) -> tuple:
    return (req.operator.value, req.value, req.min, req.max, req.unit)


def _group_key(req: Requirement) -> tuple[str, str, str]:
    condition = (req.condition or "").strip().lower()
    return (req.subject.strip().lower(), req.property.strip().lower(), condition)


@dataclass
class _Scored:
    requirement: Requirement
    score: int
    modified_time: str


def detect_and_resolve_conflicts(
    requirements: list[Requirement],
    evidence: list[Evidence],
    manifest: SourceManifest,
    policy: PrecedencePolicy | None = None,
) -> list[Conflict]:
    policy = policy or PrecedencePolicy()
    evidence_by_id = {ev.evidence_id: ev for ev in evidence}
    doc_by_id = {doc.document_id: doc for doc in manifest.documents}

    groups: dict[tuple[str, str, str], list[Requirement]] = defaultdict(list)
    for req in requirements:
        groups[_group_key(req)].append(req)

    conflicts: list[Conflict] = []
    conflict_counter = 0

    for (subject, prop, condition), group in groups.items():
        distinct_bounds = {_bounds_key(req) for req in group}
        if len(distinct_bounds) <= 1:
            continue  # corroborating evidence for the same bound, not a conflict

        scored: list[_Scored] = []
        for req in group:
            best_score = 0
            latest_modified_time = ""
            for ev_id in req.evidence:
                ev = evidence_by_id.get(ev_id)
                if ev is None:
                    continue
                doc = doc_by_id.get(ev.document_id)
                role = doc.role if doc else DocumentRole.UNKNOWN
                best_score = max(best_score, policy.score(role, ev.quote or ""))
                if doc is not None:
                    latest_modified_time = max(latest_modified_time, doc.modified_time)
            scored.append(_Scored(req, best_score, latest_modified_time))

        scored.sort(key=lambda s: (s.score, s.modified_time), reverse=True)
        winner = scored[0]
        is_unique_winner = len(scored) == 1 or scored[0].score > scored[1].score

        for entry in scored:
            entry.requirement.status = (
                FactStatus.CONFIRMED if entry is winner and is_unique_winner else FactStatus.CONFLICTED
            )

        conflict_counter += 1
        conflicts.append(
            Conflict(
                conflict_id=f"CONF-{conflict_counter:04d}",
                fact_ids=[req.requirement_id for req in group],
                description=(
                    f"Conflicting values for {subject}.{prop}"
                    + (f" (condition: {condition})" if condition else "")
                    + ": "
                    + ", ".join(f"{req.requirement_id}={_bounds_key(req)}" for req in group)
                ),
                status=ConflictStatus.RESOLVED if is_unique_winner else ConflictStatus.OPEN,
                superseded_by=winner.requirement.requirement_id if is_unique_winner else None,
                resolved_value=str(_bounds_key(winner.requirement)) if is_unique_winner else None,
            )
        )

    return conflicts
