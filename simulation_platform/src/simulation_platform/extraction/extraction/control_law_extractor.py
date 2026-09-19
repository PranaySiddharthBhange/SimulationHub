"""Control law extraction -- continuous/proportional control relationships,
distinct from `behavior_extractor.py`'s discrete IF/THEN interlocks. See
`schemas/control_law.py`."""

from __future__ import annotations

from pydantic import BaseModel

from simulation_platform.prompts.control_law_extraction import SYSTEM_PROMPT as _SYSTEM_PROMPT
from simulation_platform.schemas import ControlLaw, ControlLawType, DocumentRecord, FactStatus, Observation

from .id_sequence import IdSequence
from .llm import run_structured_extraction


class _ExtractedControlLaw(BaseModel):
    law_type: ControlLawType
    controlled_property: str
    input_property: str
    gain_p: float | None = None
    gain_i: float | None = None
    gain_d: float | None = None
    setpoint: float | str | None = None
    setpoint_unit: str | None = None
    status: FactStatus = FactStatus.EXPLICIT
    evidence_observation_ids: list[str]


class _ControlLawExtractionResult(BaseModel):
    control_laws: list[_ExtractedControlLaw]


def extract_control_laws(document: DocumentRecord, observations: list[Observation], id_seq: IdSequence) -> list[ControlLaw]:
    result = run_structured_extraction(_SYSTEM_PROMPT, document, observations, _ControlLawExtractionResult)
    return [
        ControlLaw(
            control_law_id=id_seq.next("CTL"),
            law_type=item.law_type,
            controlled_property=item.controlled_property,
            input_property=item.input_property,
            gain_p=item.gain_p,
            gain_i=item.gain_i,
            gain_d=item.gain_d,
            setpoint=item.setpoint,
            setpoint_unit=item.setpoint_unit,
            status=item.status,
            evidence=item.evidence_observation_ids,
        )
        for item in result.control_laws
    ]
