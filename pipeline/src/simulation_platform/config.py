"""ONE shared configuration for the whole platform, read from ONE root
`.env` — replaces the three independent per-stage `.env` files (document-
agent/sysml-agent/modelica-agent each had their own `ENGINEERING_AGENT_*`
/ `SYSML_AGENT_*` / `MODELICA_AGENT_*` prefixed vars, validated
independently, no shared total).

Each stage keeps its own thin `config.py`/`config/settings.py` (same
dataclass field names as before, so none of that stage's internal code
needs to change) but derives every value from this shared, single-source
`PlatformSettings` instead of independently re-reading `os.environ`. A
`STAGE_<N>_*` env var name is preferred; the old per-agent name is still
read as a fallback so an existing `.env` from any of the three original
packages keeps working if copied in verbatim during migration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Discovers the nearest `.env` upward from the current working directory
# (python-dotenv's default search) -- never overrides a variable already
# set in the real environment.
load_dotenv()


class ConfigError(RuntimeError):
    """Raised when the platform's own .env is internally inconsistent."""


def _float(name: str, default: float, legacy_name: str | None = None) -> float:
    if legacy_name and legacy_name in os.environ:
        return float(os.environ[legacy_name])
    return float(os.environ.get(name, default))


def _str(name: str, default: str, legacy_name: str | None = None) -> str:
    if legacy_name and legacy_name in os.environ:
        return os.environ[legacy_name]
    return os.environ.get(name, default)


def _bool(name: str, default: bool, legacy_name: str | None = None) -> bool:
    raw = None
    if legacy_name and legacy_name in os.environ:
        raw = os.environ[legacy_name]
    elif name in os.environ:
        raw = os.environ[name]
    if raw is None:
        return default
    return raw.strip().lower() != "false"


@dataclass(frozen=True)
class PlatformSettings:
    projects_root: Path

    total_budget_usd: float
    stage1_budget_usd: float
    stage2_budget_usd: float
    stage3_budget_usd: float
    price_per_1k_input_usd: float
    price_per_1k_output_usd: float

    # Separate from stage2/stage3_budget_usd above (which cover routine
    # planning/mapping/validation) and NOT included in the TOTAL_BUDGET_USD
    # sum-check below -- an additional, independent hard cap on the
    # auto-repair loop's cumulative spend for one generation run, so a
    # stuck repair loop can't silently eat into the budget meant for
    # forward progress.
    stage2_repair_budget_usd: float
    stage3_repair_budget_usd: float

    # Stage 4 (independent result validation, see `skills/stage4_validation.py`)
    # is a single review call, not a repair loop -- kept separate from the
    # stage1+2+3 == total sum-check below, same as the two repair budgets above.
    stage4_budget_usd: float

    stage1_backend: str
    stage1_extraction_model: str
    # Retained for compatibility with older project configuration. Local
    # Stage 1 remains text-only and skips image-only files; cloud Stage 1
    # handles visual evidence when selected.
    stage1_vision_model: str
    # `mapping_model` is the ONE model each of Stage 2/3 actually uses --
    # this fork replaced the old separate planning/mapping/validation/
    # repair calls with a single call per stage. The other six fields this
    # comment used to sit above (`stage{1,2,3}_{agent,topology,planning,
    # validation,repair}_model`) were leftovers from that older design,
    # confirmed unused anywhere outside their own definition here, and
    # have been removed.
    stage2_mapping_model: str
    stage3_mapping_model: str

    use_real_sysml_parser: bool
    sysml_parser_timeout_seconds: float
    use_real_compiler: bool
    omc_timeout_seconds: float

    max_repair_attempts: int

    # Re-added per the user's explicit choice: Stage 1 (document
    # understanding) stays on the local Ollama models -- cheap, high-
    # volume, works well enough. Merging + SysML/Modelica generation
    # (stages 2/3 in `reasoner_pipeline.py`) switch to OpenAI, matching
    # what worked earlier in this same session, before the local-model
    # fork existed -- entity resolution/renaming and real equation/
    # condition reasoning need it. `None` when unset -- callers must fail
    # clean, never fall back to a local model silently for a stage the
    # user asked to run on OpenAI.
    openai_api_key: str | None
    openai_model: str
    # Merging is the one step that has to read ALL of Stage 1's
    # per-document notes at once and correctly bind an explicit deprecation
    # statement (e.g. "the archived demo's 0.78 m/10 s values should not be
    # used") to the RIGHT number pair, not just recall that such a statement
    # exists. Found live: `gpt-5.4-mini` gets the reasoning pattern right but
    # binds it to the wrong value -- a harder cross-document entity-binding
    # task than Stage 2/3's single-document code generation. Defaults to the
    # non-mini sibling; independently overridable so cost/quality can be
    # tuned per step instead of forcing one model choice on all of them.
    merge_model: str

    @classmethod
    def load(cls) -> "PlatformSettings":
        stage1 = _float("STAGE_1_BUDGET_USD", 2.0, "ENGINEERING_AGENT_BUDGET_USD")
        stage2 = _float("STAGE_2_BUDGET_USD", 2.0, "SYSML_AGENT_BUDGET_USD")
        stage3 = _float("STAGE_3_BUDGET_USD", 2.0, "MODELICA_AGENT_BUDGET_USD")
        total = _float("TOTAL_BUDGET_USD", stage1 + stage2 + stage3)
        stage1_backend = _str("STAGE_1_BACKEND", "ollama").strip().lower()
        if stage1_backend not in {"ollama", "openai"}:
            raise ConfigError("STAGE_1_BACKEND must be one of: ollama, openai")
        # Validated at load time (platform startup), per new direction.txt
        # §27 -- refuse to run rather than silently letting per-stage caps
        # add up to more than the declared total.
        if stage1 + stage2 + stage3 > total + 1e-9:
            raise ConfigError(
                f"Stage budgets sum to ${stage1 + stage2 + stage3:.2f} "
                f"(stage1=${stage1:.2f} + stage2=${stage2:.2f} + stage3=${stage3:.2f}), "
                f"exceeding TOTAL_BUDGET_USD=${total:.2f}. "
                "Lower a stage budget or raise TOTAL_BUDGET_USD in .env."
            )

        return cls(
            projects_root=Path(os.environ.get("PROJECTS_ROOT", "./projects")).resolve(),
            total_budget_usd=total,
            stage1_budget_usd=stage1,
            stage2_budget_usd=stage2,
            stage3_budget_usd=stage3,
            price_per_1k_input_usd=_float("PRICE_PER_1K_INPUT_USD", 0.00025),
            price_per_1k_output_usd=_float("PRICE_PER_1K_OUTPUT_USD", 0.001),
            # Gemma 3 4B is the configured local model. Context sizing and
            # all prompts remain unchanged.
            stage1_backend=stage1_backend,
            stage1_extraction_model=_str("STAGE_1_EXTRACTION_MODEL", "gemma3:4b", "ENGINEERING_AGENT_EXTRACTION_MODEL"),
            stage1_vision_model=_str("STAGE_1_VISION_MODEL", "gemma3:4b"),
            stage2_mapping_model=_str("STAGE_2_MAPPING_MODEL", "gemma3:4b", "SYSML_AGENT_MAPPING_MODEL"),
            stage3_mapping_model=_str("STAGE_3_MAPPING_MODEL", "gemma3:4b", "MODELICA_AGENT_MAPPING_MODEL"),
            use_real_sysml_parser=_bool("USE_REAL_SYSML_PARSER", True, "SYSML_AGENT_USE_REAL_PARSER"),
            sysml_parser_timeout_seconds=_float("SYSML_PARSER_TIMEOUT_SECONDS", 90.0, "SYSML_AGENT_REAL_PARSER_TIMEOUT_SECONDS"),
            use_real_compiler=_bool("USE_REAL_COMPILER", True, "MODELICA_AGENT_USE_REAL_COMPILER"),
            omc_timeout_seconds=_float("OMC_TIMEOUT_SECONDS", 120.0, "MODELICA_AGENT_OMC_TIMEOUT_SECONDS"),
            # Four repairs after the initial generation display and execute as 1/5..5/5.
            max_repair_attempts=int(_float("MAX_REPAIR_ATTEMPTS", 4.0)),
            stage2_repair_budget_usd=_float("STAGE_2_REPAIR_BUDGET_USD", 1.0),
            stage3_repair_budget_usd=_float("STAGE_3_REPAIR_BUDGET_USD", 1.0),
            stage4_budget_usd=_float("STAGE_4_BUDGET_USD", 1.0),
            openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
            openai_model=_str("OPENAI_MODEL", "gpt-5.4"),
            merge_model=_str("MERGE_MODEL", "gpt-5.4"),
        )

    def project_dir(self, project_id: str) -> Path:
        return self.projects_root / project_id


SETTINGS = PlatformSettings.load()
