from __future__ import annotations

import json
from pathlib import Path

from sysml_agent.schemas import (
    RequirementCoverage,
    SysMLElementMapping,
    SysMLGenerationContract,
    SysMLGenerationPlan,
    SysMLManifest,
    SysMLTraceability,
    SysMLTraceEntry,
    SysMLValidationResult,
    ValidationStatus,
    VersionRef,
)
from sysml_agent.storage.from_document_agent import contract_from_semantic_model
from sysml_agent.storage.sysml_store import (
    load_contract,
    load_generated_files,
    load_mappings,
    load_plan,
    publish_version,
    save_contract,
    save_generated_files,
    save_manifest,
    save_mappings,
    save_plan,
    save_traceability,
    save_validation_report,
    sysml_dir,
)


def _minimal_contract() -> SysMLGenerationContract:
    return SysMLGenerationContract(project_id="p1", version=VersionRef(knowledge_version="v0001"))


def test_contract_plan_mapping_files_roundtrip(tmp_path: Path) -> None:
    contract = _minimal_contract()
    save_contract(tmp_path, contract)
    assert load_contract(tmp_path) == contract

    plan = SysMLGenerationPlan(
        project_id="p1", generation_id="gen1", packages=["Architecture"], parts=[], requirements=[],
        interfaces=[], behaviors=[],
    )
    save_plan(tmp_path, plan)
    assert load_plan(tmp_path) == plan

    mappings = [
        SysMLElementMapping(
            engineering_id="ENT-001", engineering_type="entity", sysml_construct="part def",
            sysml_element_name="AHU01", package="Architecture", evidence=["EV-1"],
        )
    ]
    save_mappings(tmp_path, mappings)
    assert load_mappings(tmp_path) == mappings

    files = {"Architecture.sysml": "package Architecture {\n}\n"}
    save_generated_files(tmp_path, files)
    assert load_generated_files(tmp_path) == files


def test_traceability_validation_manifest_and_version_persist(tmp_path: Path) -> None:
    traceability = SysMLTraceability(
        sysml_version="v0001",
        entries=[SysMLTraceEntry(engineering_id="ENT-001", sysml_element="AHU01", file="Architecture.sysml", evidence=["EV-1"])],
    )
    save_traceability(tmp_path, traceability)
    saved = json.loads((sysml_dir(tmp_path) / "traceability" / "sysml_traceability.json").read_text(encoding="utf-8"))
    assert saved["sysml_version"] == "v0001"

    result = SysMLValidationResult(
        generation_id="gen1", status=ValidationStatus.PASSED,
        requirement_coverage=RequirementCoverage(total=0, implemented=0, missing=[]),
    )
    save_validation_report(tmp_path, result)
    assert (sysml_dir(tmp_path) / "validation" / "sysml_validation_report.json").exists()

    manifest = SysMLManifest(sysml_version="v0001", knowledge_version="v0001", files=["Architecture.sysml"])
    save_manifest(tmp_path, manifest)
    assert (sysml_dir(tmp_path) / "generated" / "sysml_manifest.json").exists()

    publish_version(tmp_path, "v0001", parent=None)
    assert (sysml_dir(tmp_path) / "versions" / "v0001" / "version_metadata.json").exists()
    assert (sysml_dir(tmp_path) / "versions" / "current.json").exists()


def test_adapter_converts_document_agent_semantic_model(tmp_path: Path) -> None:
    """Fixture mirrors the JSON shape actually written by the Document Agent's
    `SemanticModel.model_dump_json()` — see engineering_agent/schemas/semantic_model.py."""

    semantic_dir = tmp_path / "semantic"
    semantic_dir.mkdir()
    (semantic_dir / "semantic_model.json").write_text(
        json.dumps(
            {
                "model_version": "v0008",
                "project_id": "iaq_001",
                "entities": [
                    {"entity_id": "ENT-001", "name": "AHU-01", "type": "AirHandlingUnit", "status": "EXPLICIT", "evidence": ["EV-1"], "aliases": []}
                ],
                "relationships": [
                    {"relationship_id": "REL-001", "source": "ENT-001", "target": "ENT-001", "type": "contains", "status": "EXPLICIT", "evidence": ["EV-1"]}
                ],
                "requirements": [
                    {
                        "requirement_id": "REQ-001", "subject": "Zone-01", "property": "CO2", "operator": "<=",
                        "value": None, "min": None, "max": 1000, "unit": "ppm", "condition": None,
                        "status": "CONFIRMED", "evidence": ["EV-1"],
                    }
                ],
                "behaviors": [],
                "constraints": [],
                "evidence": [
                    {"evidence_id": "EV-1", "fact_id": "REQ-001", "type": "EXPLICIT_TEXT", "document_id": "doc_001", "location": {"page": 8}, "quote": "CO2 shall not exceed 1000 ppm."}
                ],
                "conflicts": [], "ambiguities": [], "unknowns": [], "assumptions": [], "decisions": [],
            }
        ),
        encoding="utf-8",
    )

    contract = contract_from_semantic_model(tmp_path)

    assert contract.project_id == "iaq_001"
    assert contract.version.knowledge_version == "v0008"
    assert contract.entities[0].id == "ENT-001"
    assert contract.entities[0].name == "AHU-01"
    assert contract.requirements[0].max == 1000
    assert contract.requirements[0].unit == "ppm"
    assert contract.evidence[0].evidence_id == "EV-1"
    assert contract.interfaces == []
