"""Runtime configuration for the Engineering Knowledge / Document Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Loads a `.env` file from the current working directory (or a parent of it)
# into os.environ, if one exists. Never overrides a variable already set in
# the real environment.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    projects_root: Path
    openai_api_key: str | None
    extraction_model: str
    agent_model: str
    extraction_budget_usd: float
    price_per_1k_input_usd: float
    price_per_1k_output_usd: float

    @classmethod
    def load(cls) -> "Settings":
        root = Path(os.environ.get("ENGINEERING_AGENT_PROJECTS_ROOT", "./projects")).resolve()
        return cls(
            projects_root=root,
            openai_api_key=os.environ.get("OPENAI_API_KEY") or None,
            extraction_model=os.environ.get("ENGINEERING_AGENT_EXTRACTION_MODEL", "gpt-5.4-mini"),
            agent_model=os.environ.get("ENGINEERING_AGENT_MODEL", "gpt-5.1"),
            # Hard spending cap for one ingestion run. See observability/budget_guard.py
            # for why the price-per-token defaults are a placeholder, not billing data.
            extraction_budget_usd=float(os.environ.get("ENGINEERING_AGENT_BUDGET_USD", "2.0")),
            price_per_1k_input_usd=float(os.environ.get("ENGINEERING_AGENT_PRICE_PER_1K_INPUT_USD", "0.00025")),
            price_per_1k_output_usd=float(os.environ.get("ENGINEERING_AGENT_PRICE_PER_1K_OUTPUT_USD", "0.001")),
        )

    def project_dir(self, project_id: str) -> Path:
        return self.projects_root / project_id


SETTINGS = Settings.load()
