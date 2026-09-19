"""Deterministic generator + validators, no LLM involved.

Fixture data below is modeled on the CO2/IAQ example worked through in
`SysML V2 Agent.md` — used here purely as a test fixture to prove the
generic generator/validator pipeline behaves correctly on a realistic
shape, not as production logic specific to this one case.
"""

from __future__ import annotations

from simulation_platform.sysml_gen.generation.sysml_generator import generate_sysml_files
from simulation_platform.schemas import (
    Comparator,
    ControlLawItem,
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
from simulation_platform.sysml_gen.traceability.traceability_manager import build_traceability
from simulation_platform.sysml_gen.validation.requirement_validator import validate_requirement_coverage
from simulation_platform.sysml_gen.validation.structure_validator import validate_structure
from simulation_platform.sysml_gen.validation.syntax_validator import validate_syntax
from simulation_platform.sysml_gen.validation.traceability_validator import validate_traceability
from simulation_platform.sysml_gen.validation.validator import validate_generation


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


def test_generator_renders_a_control_law_as_a_constraint_def() -> None:
    """A continuous/proportional control law is distinct from a behavior's
    discrete if/then rule -- it maps to `constraint def`, alongside regular
    constraints, not a sixth file."""

    contract = _co2_contract()
    contract.control_laws = [
        ControlLawItem(
            id="CTL-001", law_type="PROPORTIONAL", controlled_property="fan_speed", input_property="co2_excess",
            gain_p=0.5, setpoint=800, setpoint_unit="ppm", status=FactStatus.EXPLICIT, evidence=["EV-5"],
        )
    ]
    mappings = _co2_mappings() + [
        SysMLElementMapping(
            engineering_id="CTL-001", engineering_type="control_law", sysml_construct=SysMLConstruct.CONSTRAINT_DEF,
            sysml_element_name="FanSpeedControlLaw", package="Constraints", evidence=["EV-5"],
        )
    ]
    files = generate_sysml_files(contract, mappings)

    body = files["Constraints.sysml"]
    assert "constraint def FanSpeedControlLaw" in body
    assert "fan_speed : ScalarValues::Real;" in body
    assert "co2_excess : ScalarValues::Real;" in body
    assert "PROPORTIONAL" in body
    assert "gain_p=0.5" in body
    assert "setpoint=800" in body and "ppm" in body


def test_generator_avoids_a_reserved_sysml_keyword_as_an_attribute_name() -> None:
    """Found live on a real Stage 2 run against real documents: a
    requirement's own extracted `property` text was literally "flow" (as
    in "V1 nominal flow value"), rendered as a bare `attribute flow :
    ...;` -- a real SysML v2 reserved word (confirmed directly against the
    real ANTLR parser, see `sysml_generator.py`'s own
    `_SYSML_RESERVED_ATTRIBUTE_NAMES`). The real parser rejected it with
    "no viable alternative at input 'attribute'", and it survived 6 real
    auto-repair attempts before escalating to human review, since the
    repair LLM kept proposing syntactically-plausible fixes that didn't
    address the actual root cause."""

    contract = _co2_contract()
    contract.requirements = [
        RequirementItem(
            id="REQ-002", subject="V1", property="flow", operator=Comparator.LTE, max=0.006, unit="m3/s",
            status=FactStatus.CONFIRMED, evidence=["EV-6"],
        )
    ]
    mappings = _co2_mappings()[:2] + [
        SysMLElementMapping(
            engineering_id="REQ-002", engineering_type="requirement", sysml_construct=SysMLConstruct.REQUIREMENT_DEF,
            sysml_element_name="V1FlowRequirement", package="Requirements", evidence=["EV-6"],
        )
    ]
    files = generate_sysml_files(contract, mappings)
    body = files["Requirements.sysml"]

    assert "attribute flow_value : ScalarValues::Real;" in body
    assert "attribute flow :" not in body
    assert validate_syntax("Requirements.sysml", body) == []


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
