"""Runtime configuration for the SysML v2 Creator Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    projects_root: Path
    openai_api_key: str | None
    planning_model: str
    mapping_model: str
    validation_model: str
    llm_budget_usd: float
    price_per_1k_input_usd: float
    price_per_1k_output_usd: float
    use_real_syntax_parser: bool
    real_parser_timeout_seconds: float

    @classmethod
    def load(cls) -> "Settings":
        root = Path(os.environ.get("SYSML_AGENT_PROJECTS_ROOT", "./projects")).resolve()
        return cls(
            projects_root=root,
            openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
            # "gpt-5.1-mini" does not exist for this account (only "gpt-5.1", no
            # mini variant) — same bug found and fixed in the Document Agent's
            # config/settings.py; fixed here too before it ever gets exercised live.
            planning_model=os.environ.get("SYSML_AGENT_PLANNING_MODEL", "gpt-5.4-mini"),
            mapping_model=os.environ.get("SYSML_AGENT_MAPPING_MODEL", "gpt-5.4-mini"),
            validation_model=os.environ.get("SYSML_AGENT_VALIDATION_MODEL", "gpt-5.4-mini"),
            # Hard spending cap for one generation run. See
            # observability/budget_guard.py for why the price-per-token
            # defaults are a placeholder, not billing data.
            llm_budget_usd=float(os.environ.get("SYSML_AGENT_BUDGET_USD", "2.0")),
            price_per_1k_input_usd=float(os.environ.get("SYSML_AGENT_PRICE_PER_1K_INPUT_USD", "0.00025")),
            price_per_1k_output_usd=float(os.environ.get("SYSML_AGENT_PRICE_PER_1K_OUTPUT_USD", "0.001")),
            # Real SysML v2 parser via the local jupyter-sysml-kernel (see
            # validation/real_syntax_validator.py). Gracefully skipped with a
            # note if the kernel isn't installed — this flag just lets you
            # turn it off even when it is (e.g. for speed).
            use_real_syntax_parser=os.environ.get("SYSML_AGENT_USE_REAL_PARSER", "true").lower() != "false",
            real_parser_timeout_seconds=float(os.environ.get("SYSML_AGENT_REAL_PARSER_TIMEOUT_SECONDS", "90.0")),
        )

    def project_dir(self, project_id: str) -> Path:
        return self.projects_root / project_id


SETTINGS = Settings.load()
