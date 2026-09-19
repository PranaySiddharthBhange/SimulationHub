"""Stage 1 (Document Indexing) settings -- a thin, stage-scoped view over
the platform's one shared `simulation_platform.config.SETTINGS`. Kept as
its own dataclass (same field names as before the platform consolidation)
so none of this stage's internal code needs to change; only where the
values come from changed -- one shared root `.env`, not
`ENGINEERING_AGENT_*`-prefixed vars read independently.

Only `extraction_model` is kept -- found live in this session's own gap
audit: every other field this dataclass used to carry (`projects_root`,
`openai_api_key`, `agent_model`, `extraction_budget_usd`,
`price_per_1k_input_usd`, `price_per_1k_output_usd`) was read from
`PlatformSettings` here but never actually consumed anywhere else in
`extraction/` -- real project-dir resolution goes through `ProjectStore`
(constructed from `pipeline.py`'s own `Workspace`), the real API key is
read live from the environment in `extraction/extraction/llm.py`, and the
real budget enforcement is `pipeline.py`'s `_stage_budget_guard`, built
directly from `PlatformSettings.stage1_budget_usd`. Keeping dead fields
that mirror live ones elsewhere just invites the two to silently drift.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulation_platform.config import PlatformSettings


@dataclass(frozen=True)
class Settings:
    extraction_model: str

    @classmethod
    def load(cls) -> "Settings":
        # Read live, not from the module-level `simulation_platform.config.SETTINGS`
        # snapshot -- otherwise a test can never observe a live env override
        # once that singleton was already computed at import time.
        return cls(extraction_model=PlatformSettings.load().stage1_extraction_model)


SETTINGS = Settings.load()
