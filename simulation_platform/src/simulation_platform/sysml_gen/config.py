"""Stage 2 (SysML v2 Generation) settings -- a thin, stage-scoped view over
the platform's one shared `simulation_platform.config.SETTINGS`. Kept as
its own dataclass (same field names as before the platform consolidation)
so none of this stage's internal code needs to change; only where the
values come from changed -- one shared root `.env`, not
`SYSML_AGENT_*`-prefixed vars read independently.

`projects_root`, `openai_api_key`, and `llm_budget_usd` (plus the
`project_dir()` method that used `projects_root`) were removed here in
this session's dead-config cleanup -- found live: all three were read
from `PlatformSettings` but never actually consumed anywhere in
`sysml_gen/`. Real project-dir resolution goes through `pipeline.py`'s own
`Workspace`, the real API key is read live from the environment in
`sysml_gen/llm.py`, and the real Stage 2 budget enforcement is
`pipeline.py`'s `_stage_budget_guard`, built directly from
`PlatformSettings.stage2_budget_usd`.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulation_platform.config import PlatformSettings


@dataclass(frozen=True)
class Settings:
    planning_model: str
    mapping_model: str
    validation_model: str
    repair_model: str
    price_per_1k_input_usd: float
    price_per_1k_output_usd: float
    use_real_syntax_parser: bool
    real_parser_timeout_seconds: float
    max_repair_attempts: int
    repair_budget_usd: float

    @classmethod
    def load(cls) -> "Settings":
        # Read live, not from the module-level `simulation_platform.config.SETTINGS`
        # snapshot -- otherwise a test can never observe a live env override
        # once that singleton was already computed at import time (same fix
        # already made for the OPENAI_API_KEY check in llm.py, same reason).
        PLATFORM_SETTINGS = PlatformSettings.load()
        return cls(
            planning_model=PLATFORM_SETTINGS.stage2_planning_model,
            mapping_model=PLATFORM_SETTINGS.stage2_mapping_model,
            validation_model=PLATFORM_SETTINGS.stage2_validation_model,
            repair_model=PLATFORM_SETTINGS.stage2_repair_model,
            price_per_1k_input_usd=PLATFORM_SETTINGS.price_per_1k_input_usd,
            price_per_1k_output_usd=PLATFORM_SETTINGS.price_per_1k_output_usd,
            use_real_syntax_parser=PLATFORM_SETTINGS.use_real_sysml_parser,
            real_parser_timeout_seconds=PLATFORM_SETTINGS.sysml_parser_timeout_seconds,
            max_repair_attempts=PLATFORM_SETTINGS.max_repair_attempts,
            repair_budget_usd=PLATFORM_SETTINGS.stage2_repair_budget_usd,
        )


SETTINGS = Settings.load()
