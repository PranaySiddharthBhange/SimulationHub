"""Domain and meta-skills: reasoning-context TEXT appended to LLM prompts,
never called as functions and never consulted by deterministic code (that
kind of data lives in `tools/`, e.g. `tools/library_catalog.py`).

Use `registry.with_sysml_skills(...)` / `registry.with_modelica_skills(...)`
to attach the right skill text to a stage's system prompt.
"""

from .co2_ventilation import SKILL as CO2_VENTILATION_SKILL
from .fluid_tank_systems import SKILL as FLUID_TANK_SYSTEMS_SKILL
from .magnetic_circuit import SKILL as MAGNETIC_CIRCUIT_SKILL
from .modelica_modeling import SKILL as MODELICA_MODELING_SKILL
from .registry import PHYSICAL_DOMAIN_SKILLS, with_modelica_skills, with_sysml_skills
from .sysml_v2_modeling import SKILL as SYSML_V2_MODELING_SKILL

__all__ = [
    "CO2_VENTILATION_SKILL",
    "FLUID_TANK_SYSTEMS_SKILL",
    "MAGNETIC_CIRCUIT_SKILL",
    "MODELICA_MODELING_SKILL",
    "SYSML_V2_MODELING_SKILL",
    "PHYSICAL_DOMAIN_SKILLS",
    "with_sysml_skills",
    "with_modelica_skills",
]
