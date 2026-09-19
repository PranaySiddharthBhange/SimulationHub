from __future__ import annotations

import json
from pathlib import Path

from simulation_platform.schemas import (
    CompileResult,
    CompileStatus,
    LegacyComparison,
    LegacyRecommendation,
    ModelicaGenerationContract,
    ModelicaGenerationPlan,
    ModelicaManifest,
    ModelicaMapping,
    ModelicaMappingType,
    ModelicaTraceability,
    ModelicaTraceEntity,
    ModelicaValidationResult,
    ValidationStatus,
    VersionRef,
)
from simulation_platform.modelica_gen.storage import build_upstream_bundle, requirement_bounds
from simulation_platform.modelica_gen.storage.modelica_store import (
    load_contract,
    load_legacy_comparisons,
    load_mappings,
    load_plan,
    modelica_dir,
    publish_version,
    save_compile_result,
    save_contract,
    save_generated_files,
    save_legacy_comparisons,
    save_manifest,
    save_mappings,
    save_plan,
    save_traceability,
    save_validation_report,
)

from .conftest import seed_upstream_project


def test_contract_plan_mapping_files_roundtrip(tmp_path: Path) -> None:
    contract = ModelicaGenerationContract(project_id="p1", version=VersionRef(knowledge_version="v0001"))
    save_contract(tmp_path, contract)
    assert load_contract(tmp_path) == contract

    plan = ModelicaGenerationPlan(
        project_id="p1", generation_id="gen1", packages=["System"], components=[], properties=[],
        behaviors=[], constraints=[],
    )
    save_plan(tmp_path, plan)
    assert load_plan(tmp_path) == plan

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL, target="Tank",
            reason="test", evidence=["EV-1"],
        )
    ]
    save_mappings(tmp_path, mappings)
    assert load_mappings(tmp_path) == mappings

    comparisons = [
        LegacyComparison(
            sysml_element="TankDemo", legacy_class="TankDemo_Rev12", legacy_file="07_legacy_tank_demo.mo",
            matches=["h1High"], differences=[], recommendation=LegacyRecommendation.REUSE_AS_IS,
        )
    ]
    save_legacy_comparisons(tmp_path, comparisons)
    assert load_legacy_comparisons(tmp_path) == comparisons

    files = {"TankSystem.mo": "model TankSystem\nend TankSystem;\n"}
    save_generated_files(tmp_path, files)


def test_traceability_manifest_compile_and_version_persist(tmp_path: Path) -> None:
    traceability = ModelicaTraceability(
        modelica_version="v0001", sysml_version="v0004", knowledge_version="v0008",
        entities=[ModelicaTraceEntity(engineering_id="ENT-001", sysml_element="TankDemo", modelica_class="TankDemo", file="TankDemo.mo")],
    )
    save_traceability(tmp_path, traceability)
    saved = json.loads((modelica_dir(tmp_path) / "traceability" / "modelica_traceability.json").read_text(encoding="utf-8"))
    assert saved["modelica_version"] == "v0001"

    result = ModelicaValidationResult(modelica_version="v0001", status=ValidationStatus.PASSED)
    save_validation_report(tmp_path, result)
    assert (modelica_dir(tmp_path) / "validation" / "modelica_validation_report.json").exists()

    manifest = ModelicaManifest(
        modelica_version="v0001", sysml_version="v0004", knowledge_version="v0008",
        entry_class="TankSystem", classes=["TankSystem"], files=["TankSystem.mo"],
    )
    save_manifest(tmp_path, manifest)
    assert (modelica_dir(tmp_path) / "generated" / "modelica_manifest.json").exists()

    compile_result = CompileResult(
        execution_id="exec_1", status=CompileStatus.PASSED, backend="openmodelica",
        backend_version="1.27.1", duration_seconds=1.0,
    )
    save_compile_result(tmp_path, compile_result)
    assert (modelica_dir(tmp_path) / "compile" / "compile_result.json").exists()

    publish_version(tmp_path, "v0001", parent=None)
    assert (modelica_dir(tmp_path) / "versions" / "v0001" / "version_metadata.json").exists()
    assert (modelica_dir(tmp_path) / "versions" / "current.json").exists()


def test_build_upstream_bundle_reads_sysml_and_legacy_files(tmp_path: Path) -> None:
    document_agent_project_dir, sysml_project_dir = seed_upstream_project(tmp_path)

    bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)

    assert bundle.contract.project_id == "tank_001"
    assert bundle.contract.version.knowledge_version == "v0008"
    assert bundle.contract.version.sysml_version == "v0004"
    assert bundle.contract.components == ["ENT-001"]
    assert bundle.contract.properties == ["REQ-001"]
    assert bundle.contract.legacy_models == ["07_legacy_tank_demo.mo"]

    assert "Architecture.sysml" in bundle.sysml_generated_files
    assert "07_legacy_tank_demo.mo" in bundle.legacy_files

    bounds = requirement_bounds(bundle.sysml_contract_raw)
    assert bounds == [{"subject": "TankDemo", "property": "h1High", "min": None, "max": 0.78, "value": None, "unit": "m"}]

    assert bundle.engineering_id_by_sysml_element_name() == {
        "TankDemo": "ENT-001", "TankDemoRequirement": "REQ-001",
    }


def test_build_upstream_bundle_with_no_legacy_files(tmp_path: Path) -> None:
    document_agent_project_dir, sysml_project_dir = seed_upstream_project(tmp_path, include_legacy=False)

    bundle = build_upstream_bundle(document_agent_project_dir, sysml_project_dir)
    assert bundle.contract.legacy_models == []
    assert bundle.legacy_files == {}
