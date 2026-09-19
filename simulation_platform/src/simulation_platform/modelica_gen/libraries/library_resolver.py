"""Library Resolver. Mirrors `Modelica Agent.md`, Section 13.

    Engineering concept -> candidate Modelica classes -> compatibility
    check -> unambiguous match? yes: select. no: ask human.

Purely deterministic keyword matching against the fixed catalog in
`library_catalog.py` -- never lets an LLM invent a library class name.
When more than one keyword matches (or a keyword's own candidate list has
more than one entry), the result is `ambiguous=True` and every candidate is
returned, which is exactly HITL-2 in `Modelica Agent.md`, Section 26: "Two
Modelica library components appear compatible. Ask which library/component
should be used if the choice has engineering consequences."
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.tools.library_catalog import COMPONENT_KEYWORD_CATALOG, LibraryCandidate


class LibraryResolution(BaseModel):
    sysml_element: str
    matched_keywords: list[str]
    candidates: list[LibraryCandidate]
    ambiguous: bool


def resolve_component(sysml_element_name: str, type_hint: str | None = None) -> LibraryResolution:
    haystack = f"{sysml_element_name} {type_hint or ''}".lower()

    matched_keywords: list[str] = []
    candidates: list[LibraryCandidate] = []
    for keyword, keyword_candidates in COMPONENT_KEYWORD_CATALOG.items():
        if keyword in haystack:
            matched_keywords.append(keyword)
            candidates.extend(keyword_candidates)

    return LibraryResolution(
        sysml_element=sysml_element_name,
        matched_keywords=matched_keywords,
        candidates=candidates,
        ambiguous=len(candidates) > 1,
    )
