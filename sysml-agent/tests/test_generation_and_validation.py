"""Deterministic generator + validators, no LLM involved.

Fixture data below is modeled on the CO2/IAQ example worked through in
`SysML V2 Agent.md` — used here purely as a test fixture to prove the
generic generator/validator pipeline behaves correctly on a realistic
shape, not as production logic specific to this one case.
"""

from __future__ import annotations

from sysml_agent.generation.sysml_generator import generate_sysml_files
from sysml_agent.schemas import (
    Comparator,
    EntityItem,
    FactStatus,
    RelationshipItem,
    RequirementItem,
    SysMLConstruct,
    SysMLElementMapping,
    SysMLGenerationContract,
    SysMLGenerationPlan,
    VersionRef,
)
from sysml_agent.traceability.traceability_manager import build_traceability
from sysml_agent.validation.requirement_validator import validate_requirement_coverage
from sysml_agent.validation.structure_validator import validate_structure
from sysml_agent.validation.syntax_validator import validate_syntax
from sysml_agent.validation.traceability_validator import validate_traceability
from sysml_agent.validation.validator import validate_generation


def _co2_contract() -> SysMLGenerationContract:
    return SysMLGenerationContract(
        project_id="iaq_001",
        version=VersionRef(knowledge_version="v0008"),
        entities=[
            EntityItem(id="ENT-001", name="AHU-01", type="AirHandlingUnit", status=FactStatus.EXPLICIT, evidence=["EV-1"]),
            EntityItem(id="ENT-002", name="CO2Sensor-01", type="CO2Sensor", status=FactStatus.EXPLICIT, evidence=["EV-2"]),
        ],
        relationships=[
            RelationshipItem(source="ENT-001", target="ENT-002", type="CONNECTED_TO", evidence=["EV-3"]),
        ],
        requirements=[
            RequirementItem(
                id="REQ-001", subject="Zone-01", property="CO2", operator=Comparator.LTE, max=1000, unit="ppm",
                status=FactStatus.CONFIRMED, evidence=["EV-4"],
            )
        ],
    )


def _co2_plan() -> SysMLGenerationPlan:
    return SysMLGenerationPlan(
        project_id="iaq_001",
        generation_id="gen_0001",
        packages=["Architecture", "Requirements", "Interfaces", "Behaviors", "Constraints"],
        parts=["AHU01", "CO2Sensor01"],
        requirements=["REQ-001"],
        interfaces=[],
        behaviors=[],
    )


def _co2_mappings() -> list[SysMLElementMapping]:
    return [
        SysMLElementMapping(
            engineering_id="ENT-001", engineering_type="entity", sysml_construct=SysMLConstruct.PART_DEF,
            sysml_element_name="AHU01", package="Architecture", evidence=["EV-1"],
        ),
        SysMLElementMapping(
            engineering_id="ENT-002", engineering_type="entity", sysml_construct=SysMLConstruct.PART_DEF,
            sysml_element_name="CO2Sensor01", package="Architecture", evidence=["EV-2"],
        ),
        SysMLElementMapping(
            engineering_id="REQ-001", engineering_type="requirement", sysml_construct=SysMLConstruct.REQUIREMENT_DEF,
            sysml_element_name="CO2Requirement", package="Requirements", evidence=["EV-4"],
        ),
    ]


def test_generator_produces_five_files_with_expected_content() -> None:
    files = generate_sysml_files(_co2_contract(), _co2_mappings())

    assert set(files) == {
        "Architecture.sysml", "Requirements.sysml", "Interfaces.sysml", "Behaviors.sysml", "Constraints.sysml",
    }
    assert "part def AHU01;" in files["Architecture.sysml"]
    assert "part ahu01 : AHU01;" in files["Architecture.sysml"]
    assert "connect ahu01 to co2Sensor01;" in files["Architecture.sysml"]
    assert "requirement def CO2Requirement" in files["Requirements.sysml"]
    assert "1000" in files["Requirements.sysml"]


def test_syntax_validator_catches_unbalanced_braces() -> None:
    assert validate_syntax("Requirements.sysml", "package Requirements {\n    requirement def X {\n}") != []
    assert validate_syntax("Requirements.sysml", "package Requirements {\n}") == []


def test_structure_validator_catches_dangling_relationship_and_bad_package() -> None:
    contract = _co2_contract()
    plan = _co2_plan()
    mappings = _co2_mappings()

    # Break it: point a relationship at an entity id that has no mapping.
    contract.relationships.append(RelationshipItem(source="ENT-001", target="ENT-999", type="SUPPLIES"))
    # Break it again: a mapping references a package the plan never declared.
    mappings.append(
        SysMLElementMapping(
            engineering_id="ENT-003", engineering_type="entity", sysml_construct=SysMLConstruct.PART_DEF,
            sysml_element_name="Damper01", package="NotARealPackage",
        )
    )

    issues = validate_structure(contract, plan, mappings)
    assert any("ENT-999" in issue.element for issue in issues)
    assert any("NotARealPackage" in issue.error for issue in issues)


def test_structure_validator_passes_on_well_formed_input() -> None:
    issues = validate_structure(_co2_contract(), _co2_plan(), _co2_mappings())
    assert issues == []


def test_requirement_coverage_flags_missing_mapping() -> None:
    contract = _co2_contract()
    coverage = validate_requirement_coverage(contract, mappings=[])
    assert coverage.total == 1
    assert coverage.implemented == 0
    assert coverage.missing == ["REQ-001"]

    coverage_ok = validate_requirement_coverage(contract, _co2_mappings())
    assert coverage_ok.missing == []


def test_traceability_validator_flags_mapping_without_evidence() -> None:
    mappings = _co2_mappings()
    mappings.append(
        SysMLElementMapping(
            engineering_id="ENT-004", engineering_type="entity", sysml_construct=SysMLConstruct.PART_DEF,
            sysml_element_name="Damper02", package="Architecture", evidence=[],
        )
    )
    issues = validate_traceability(mappings)
    assert len(issues) == 1
    assert issues[0].element == "ENT-004"


def test_traceability_manager_assigns_correct_files() -> None:
    traceability = build_traceability("v0001", _co2_mappings())
    by_id = {entry.engineering_id: entry for entry in traceability.entries}
    assert by_id["ENT-001"].file == "Architecture.sysml"
    assert by_id["REQ-001"].file == "Requirements.sysml"
    assert by_id["REQ-001"].sysml_element == "CO2Requirement"


def test_full_validation_passes_end_to_end_on_well_formed_input() -> None:
    contract = _co2_contract()
    plan = _co2_plan()
    mappings = _co2_mappings()
    files = generate_sysml_files(contract, mappings)

    result = validate_generation("gen_0001", contract, plan, mappings, files)

    assert result.status.value == "PASSED"
    assert result.requirement_coverage.missing == []
    assert result.syntax_errors == []
    assert result.structural_errors == []
    assert result.traceability_errors == []
