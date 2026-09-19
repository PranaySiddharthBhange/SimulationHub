"""Builds the Modelica Generation Contract (and everything the later
deterministic stages need) from the SysML Agent's and Document Agent's own
persisted JSON -- read as plain JSON, not by importing either package, so
this agent stays as decoupled from them as it would be as a separate
service. Same call already made twice (`sysml-agent/storage/
from_document_agent.py`, D10): the only thing shared between agents is the
JSON shape defined in `Agent Contracts.md`.

Legacy Modelica files live under the Document Agent's own
`source/original/**/*.mo` (confirmed against the real datasets, e.g.
`06_legacy_code/07_legacy_tank_demo.mo`), not anywhere the SysML Agent
touches -- so this needs both project directories, mirroring
`build_sysml_graph(document_agent_project_dir_resolver,
sysml_project_dir_resolver)`'s own two-resolver pattern.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from simulation_platform.schemas import ModelicaGenerationContract, VersionRef


@dataclass
class UpstreamBundle:
    contract: ModelicaGenerationContract
    sysml_contract_raw: dict
    sysml_traceability_raw: dict
    sysml_generated_files: dict[str, str]
    legacy_files: dict[str, str]  # filename -> .mo source text

    def engineering_id_by_sysml_element_name(self) -> dict[str, str]:
        """SysML element *name* (e.g. "TankDemo") -> engineering id (e.g.
        "ENT-001"). The generated `.sysml` text only has names -- this is
        the only place that mapping back to an id exists, so anything that
        needs to go from a parsed SysML part back to its engineering id
        (`legacy/legacy_comparator.py`, via the caller) has to go through
        this, not guess from the name.
        """

        return {
            entry["sysml_element"]: entry["engineering_id"]
            for entry in self.sysml_traceability_raw.get("entries", [])
        }


def _load_sysml_generated_files(sysml_dir: Path) -> dict[str, str]:
    generated_dir = sysml_dir / "generated"
    if not generated_dir.exists():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(generated_dir.glob("*.sysml"))}


def _load_legacy_files(document_agent_project_dir: Path) -> dict[str, str]:
    original_dir = document_agent_project_dir / "source" / "original"
    if not original_dir.exists():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(original_dir.rglob("*.mo"))}


def build_upstream_bundle(document_agent_project_dir: Path, sysml_project_dir: Path) -> UpstreamBundle:
    sysml_dir = sysml_project_dir / "sysml"
    sysml_contract_raw = json.loads((sysml_dir / "input" / "generation_contract.json").read_text(encoding="utf-8"))
    traceability_raw = json.loads(
        (sysml_dir / "traceability" / "sysml_traceability.json").read_text(encoding="utf-8")
    )

    legacy_files = _load_legacy_files(document_agent_project_dir)

    contract = ModelicaGenerationContract(
        project_id=sysml_contract_raw["project_id"],
        version=VersionRef(
            knowledge_version=sysml_contract_raw["version"]["knowledge_version"],
            sysml_version=traceability_raw.get("sysml_version"),
        ),
        components=[e["id"] for e in sysml_contract_raw.get("entities", [])],
        properties=[r["id"] for r in sysml_contract_raw.get("requirements", [])],
        interfaces=[i["id"] for i in sysml_contract_raw.get("interfaces", [])],
        behaviors=[b["id"] for b in sysml_contract_raw.get("behaviors", [])],
        control_laws=[cl["id"] for cl in sysml_contract_raw.get("control_laws", [])],
        constraints=[c["id"] for c in sysml_contract_raw.get("constraints", [])],
        legacy_models=sorted(legacy_files.keys()),
    )

    return UpstreamBundle(
        contract=contract,
        sysml_contract_raw=sysml_contract_raw,
        sysml_traceability_raw=traceability_raw,
        sysml_generated_files=_load_sysml_generated_files(sysml_dir),
        legacy_files=legacy_files,
    )


def requirement_bounds(sysml_contract_raw: dict) -> list[dict]:
    """Plain dicts (`subject`/`property`/`min`/`max`/`value`/`unit`) for
    `legacy/legacy_comparator.py`, kept decoupled from the SysML Agent's own
    Pydantic `RequirementItem` type."""

    return [
        {
            "subject": r.get("subject"),
            "property": r.get("property"),
            "min": r.get("min"),
            "max": r.get("max"),
            "value": r.get("value"),
            "unit": r.get("unit"),
        }
        for r in sysml_contract_raw.get("requirements", [])
    ]
