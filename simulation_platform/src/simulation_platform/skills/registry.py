"""Registry tying skill content to the prompts that should carry it.
Skills are plain text, appended to a system prompt -- never called as a
function, never consulted by deterministic code (see module docstrings on
the individual skill files, and the distinction from `tools/` data).

Physical-domain skills are all included unconditionally for now rather
than domain-detected and selected -- simpler and safer than a keyword
heuristic that might mis-classify and silently omit the one skill that
would have mattered; revisit only if token cost becomes a real constraint
at a scale well beyond this hackathon's $2/stage budget.
"""

from __future__ import annotations

from .co2_ventilation import SKILL as CO2_VENTILATION_SKILL
from .fluid_tank_systems import SKILL as FLUID_TANK_SYSTEMS_SKILL
from .magnetic_circuit import SKILL as MAGNETIC_CIRCUIT_SKILL
from .modelica_modeling import SKILL as MODELICA_MODELING_SKILL
from .sysml_v2_modeling import SKILL as SYSML_V2_MODELING_SKILL

PHYSICAL_DOMAIN_SKILLS = [
    FLUID_TANK_SYSTEMS_SKILL,
    CO2_VENTILATION_SKILL,
    MAGNETIC_CIRCUIT_SKILL,
]


def with_sysml_skills(system_prompt: str) -> str:
    """Appends the SysML v2 meta-skill and all physical-domain skills to a
    Stage 2 (SysML reasoning/generation) system prompt."""

    return "\n\n".join([system_prompt, SYSML_V2_MODELING_SKILL, *PHYSICAL_DOMAIN_SKILLS])


def with_modelica_skills(system_prompt: str) -> str:
    """Appends the Modelica meta-skill and all physical-domain skills to a
    Stage 3 (Modelica reasoning/generation) system prompt."""

    return "\n\n".join([system_prompt, MODELICA_MODELING_SKILL, *PHYSICAL_DOMAIN_SKILLS])
