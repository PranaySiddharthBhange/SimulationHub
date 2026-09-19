"""Independent, holistic topology cross-check (Stage 1).

Every other Stage 1 extractor deliberately sees only one document's
observations at a time (`extraction/extraction/llm.py`'s own rule) --
essential for avoiding the large-single-call truncation risk, but it also
means no per-document extraction pass can ever catch a duplicate or a
connection spanning two different documents, or independently notice a
component the per-document pass simply missed.

This runs ONE additional, deliberately narrow (topology only -- components
and connections, nothing else) holistic pass across every document's
observations together, then deterministically compares it against the
assembled, already-resolved per-document extraction. Agreement is real
confidence; disagreement is a generalizable signal that catches WHATEVER
kind of gap actually occurred -- not just the specific bug signatures this
platform has already found and patched -- surfaced as a real `Ambiguity`
through the existing human-review path, never silently dropped.
"""

from __future__ import annotations

import os

from pydantic import BaseModel

from simulation_platform.extraction.config.settings import SETTINGS
from simulation_platform.extraction.extraction.id_sequence import IdSequence
from simulation_platform.extraction.extraction.llm import ExtractionUnavailable, render_observations
# Reuses the SAME tag-aware fuzzy-matching this platform already verified
# against the real Tank dataset's naming conventions, rather than
# reinventing a second, potentially-inconsistent similarity metric here.
from simulation_platform.extraction.resolution.entity_resolution import POSSIBLE_MATCH_THRESHOLD, _similarity
from simulation_platform.schemas import Ambiguity, Entity, ImpactLevel, Observation, Relationship


class _HolisticComponent(BaseModel):
    name: str
    type: str
    evidence_observation_ids: list[str] = []


class _HolisticConnection(BaseModel):
    source: str  # a `_HolisticComponent.name` from this SAME response
    target: str
    evidence_observation_ids: list[str] = []


class HolisticTopology(BaseModel):
    components: list[_HolisticComponent] = []
    connections: list[_HolisticConnection] = []


def extract_holistic_topology(observations: list[Observation]) -> HolisticTopology:
    """The one Stage 1 LLM call that sees every document's observations at
    once -- see this module's own docstring and `prompts/
    topology_extraction.py` for why that's deliberate and safe here (kept
    narrow to topology only, unlike a full "extract everything
    holistically" call, which is exactly the shape that has truncated on
    a real dataset before)."""

    if not observations:
        return HolisticTopology()

    # Read live, not from a frozen settings snapshot -- same reasoning as
    # `extraction/extraction/llm.py::run_structured_extraction`.
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ExtractionUnavailable(
            "Holistic topology extraction requires OPENAI_API_KEY -- set it in .env before running extraction."
        )

    from langchain_openai import ChatOpenAI

    from simulation_platform.prompts.topology_extraction import SYSTEM_PROMPT

    model = ChatOpenAI(model=SETTINGS.extraction_model, api_key=api_key, temperature=0)
    # `method="function_calling"` -- same fix as every other structured-output
    # call site in this platform (see `extraction/extraction/llm.py`).
    structured_model = model.with_structured_output(HolisticTopology, method="function_calling")

    user_prompt = (
        "Observations from EVERY document in this project, combined (cite the bracketed [obs_id] "
        f"as evidence -- never invent an id):\n\n{render_observations(observations)}"
    )
    result = structured_model.invoke(
        [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
    )
    return result  # type: ignore[return-value]


def cross_check_topology(
    holistic: HolisticTopology,
    canonical_entities: list[Entity],
    canonical_relationships: list[Relationship],
    id_seq: IdSequence,
) -> list[Ambiguity]:
    """Compares the independent holistic re-derivation against the
    already-resolved, canonical per-document extraction.

    Only the "holistic found something the detailed extraction has no
    reasonable match for" direction is flagged -- the severe, previously
    undetectable failure mode (a real component or connection silently
    absent from the entire downstream pipeline). The reverse direction
    (something the detailed extraction has that the holistic pass didn't
    independently corroborate) is deliberately NOT flagged: the holistic
    pass is narrow and cheap by design, and many legitimately-extracted
    entities (signals, non-physical concepts) are outside its scope on
    purpose -- flagging that direction too would mostly be noise a human
    would quickly learn to ignore, undermining the ones that matter."""

    entity_names = {entity.entity_id: entity.name for entity in canonical_entities}

    def _best_match(name: str) -> tuple[str | None, float]:
        best_id, best_score = None, 0.0
        for entity_id, entity_name in entity_names.items():
            score = _similarity(name, entity_name)
            if score > best_score:
                best_id, best_score = entity_id, score
        return best_id, best_score

    ambiguities: list[Ambiguity] = []
    resolved_by_holistic_name: dict[str, str] = {}

    component_by_name = {component.name: component for component in holistic.components}
    connection_endpoint_names = {
        name for connection in holistic.connections for name in (connection.source, connection.target)
    }
    # A connection endpoint the holistic pass never ALSO listed in
    # `components` (an incomplete-but-real LLM response, not assumed away)
    # is still a real name that has to resolve to something -- treat it
    # exactly like an unlisted component instead of silently letting the
    # connection built on it fall through both checks unflagged.
    names_needing_resolution = list(component_by_name) + sorted(connection_endpoint_names - component_by_name.keys())

    for name in names_needing_resolution:
        matched_id, score = _best_match(name)
        if score >= POSSIBLE_MATCH_THRESHOLD:
            resolved_by_holistic_name[name] = matched_id
            continue
        component_type = component_by_name[name].type if name in component_by_name else "unspecified"
        ambiguities.append(
            Ambiguity(
                ambiguity_id=id_seq.next("TOPO"),
                question=(
                    f"An independent, holistic re-read of every document together identified a "
                    f"component ('{name}', type={component_type}) that does not closely match any "
                    "entity produced by the detailed per-document extraction. This could be a real "
                    "component the detailed extraction missed, or a false positive from the "
                    "holistic pass."
                ),
                candidates=[
                    "real component the detailed extraction missed -- add it",
                    "false positive from the holistic pass -- not a real component",
                ],
                impact=ImpactLevel.HIGH,
                affects=[],
            )
        )

    canonical_pairs: set[frozenset[str]] = {
        frozenset({rel.source, rel.target}) for rel in canonical_relationships
    }

    for connection in holistic.connections:
        source_id = resolved_by_holistic_name.get(connection.source)
        target_id = resolved_by_holistic_name.get(connection.target)
        if source_id is None or target_id is None:
            continue  # already flagged as a missing-component ambiguity above -- don't double-report
        if frozenset({source_id, target_id}) in canonical_pairs:
            continue
        ambiguities.append(
            Ambiguity(
                ambiguity_id=id_seq.next("TOPO"),
                question=(
                    f"An independent, holistic re-read of every document together found a connection "
                    f"between '{connection.source}' and '{connection.target}' that the detailed "
                    "per-document extraction never captured as a relationship between the matching "
                    "entities."
                ),
                candidates=[
                    "real connection the detailed extraction missed -- add it",
                    "false positive from the holistic pass -- not a real connection",
                ],
                impact=ImpactLevel.HIGH,
                affects=[source_id, target_id],
            )
        )

    return ambiguities
