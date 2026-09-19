"""Observation store. Mirrors `Document Agent.md`, Section 18.

Observations are immutable and append-only: `observations.jsonl` is never
rewritten in place, only appended to as new source versions are ingested.
"""

from __future__ import annotations

from pathlib import Path

from simulation_platform.schemas import Observation


def observations_path(project_dir: Path) -> Path:
    return project_dir / "workspace" / "extracted" / "observations.jsonl"


def append_observations(project_dir: Path, observations: list[Observation]) -> None:
    path = observations_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for obs in observations:
            fh.write(obs.model_dump_json() + "\n")


def load_observations(project_dir: Path) -> list[Observation]:
    path = observations_path(project_dir)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return [Observation.model_validate_json(line) for line in fh if line.strip()]
