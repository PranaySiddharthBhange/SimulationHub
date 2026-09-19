"""Source precedence. Mirrors `Document Agent.md`, Section 32.

This is an example policy, not a universal engineering rule — it is
configurable per project (pass a custom `role_precedence` / keyword list to
`PrecedencePolicy`). The default below encodes one real pattern seen in the
golden datasets: a `CORRESPONDENCE` email that references a closed design
decision (e.g. "DR-IAQ-05 closed this today...") outranks even a formal
`PROJECT_REQUIREMENT`, because it documents the *latest approved* answer —
while an un-flagged email ranks below the formal documents, and
`LEGACY_IMPLEMENTATION` ranks lowest of all, matching the "STALE"-labelled
legacy Modelica models in the datasets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from simulation_platform.schemas import DocumentRole

_DEFAULT_ROLE_PRECEDENCE: dict[DocumentRole, int] = {
    DocumentRole.PROJECT_REQUIREMENT: 100,
    DocumentRole.COMMISSIONING: 90,
    DocumentRole.ENGINEERING_DATA: 80,
    DocumentRole.ARCHITECTURE: 65,
    DocumentRole.DESIGN_NOTE: 60,
    DocumentRole.CORRESPONDENCE: 50,
    DocumentRole.DATASHEET: 40,
    DocumentRole.MEASUREMENT: 30,
    DocumentRole.LEGACY_IMPLEMENTATION: 10,
    DocumentRole.UNKNOWN: 0,
}

_APPROVED_DECISION_KEYWORDS = re.compile(
    r"\b(closed|approved|decision|confirm(?:ed)?|DR-|CR-|freeze[sd]?|rejected)\b", re.IGNORECASE
)

APPROVED_CORRESPONDENCE_BONUS = 55  # pushes an approved-decision email above PROJECT_REQUIREMENT (100)


@dataclass
class PrecedencePolicy:
    role_precedence: dict[DocumentRole, int] = field(default_factory=lambda: dict(_DEFAULT_ROLE_PRECEDENCE))

    def score(self, role: DocumentRole, evidence_quote: str) -> int:
        base = self.role_precedence.get(role, 0)
        if role is DocumentRole.CORRESPONDENCE and _APPROVED_DECISION_KEYWORDS.search(evidence_quote or ""):
            return base + APPROVED_CORRESPONDENCE_BONUS
        return base
