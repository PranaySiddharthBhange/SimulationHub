"""Deterministic generator + validators, no LLM involved. Fixture models a
tank system with three components exercising all three generation paths:
a legacy-reuse MODEL, a from-scratch MODEL stub, and a LIBRARY_COMPONENT.
"""

from __future__ import annotations

import re

from simulation_platform.modelica_gen.generation import generate_modelica_files
from simulation_platform.schemas import (
    LegacyClass,
    LegacyComparison,
    LegacyModel,
    LegacyParameter,
    LegacyRecommendation,
    LegacyVariable,
    ModelicaMapping,
    ModelicaMappingType,
    SysMLConnection,
    SysMLPart,
    SysMLSemanticModel,
)
from simulation_platform.modelica_gen.validation import validate_generation


def _mappings() -> list[ModelicaMapping]:
    return [
        ModelicaMapping(
            sysml_element="REQ-001", mapping_type=ModelicaMappingType.PARAMETER, target="Real",
            reason="requirement bound", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL, target="TankDemo",
            reason="reuse legacy tank", evidence=["EV-2"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Blocks.Interfaces.RealOutput", reason="sensor output", evidence=["EV-3"],
        ),
        ModelicaMapping(
            sysml_element="ENT-003", mapping_type=ModelicaMappingType.MODEL, target="FreshComponent",
            reason="no legacy match", evidence=["EV-4"],
        ),
    ]


def _legacy_comparisons() -> list[LegacyComparison]:
    return [
        LegacyComparison(
            sysml_element="ENT-001", legacy_class="TankDemo_Rev12", legacy_file="07_legacy_tank_demo.mo",
            matches=["h1High"], differences=[], recommendation=LegacyRecommendation.REUSE_AS_IS,
        )
    ]


def _legacy_models() -> list[LegacyModel]:
    return [
        LegacyModel(
            filename="07_legacy_tank_demo.mo",
            classes=[
                LegacyClass(
                    kind="model", name="TankDemo_Rev12",
                    parameters=[LegacyParameter(name="h1High", type="Real", value="0.78", unit="m", line=2)],
                )
            ],
        )
    ]


def _sysml_semantic_model(target_instance: str = "realOutput") -> SysMLSemanticModel:
    return SysMLSemanticModel(
        connections=[
            SysMLConnection(source_instance="tankDemo", target_instance=target_instance, relationship_type="CONNECTED_TO")
        ]
    )


def _sysml_contract_raw() -> dict:
    return {
        "requirements": [
            {"id": "REQ-001", "subject": "TankDemo", "property": "h1High", "min": None, "max": 0.78, "value": None, "unit": "m"}
        ]
    }


def test_generator_produces_expected_files_and_reuses_legacy_class() -> None:
    files, entry_class, class_names, declared_instances = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw()
    )

    assert "TankDemo.mo" in files  # reused-from-legacy class, named after the mapping's own target
    assert 'parameter Real h1High(unit="m") = 0.78;' in files["TankDemo.mo"]
    assert "FreshComponent.mo" in files  # from-scratch stub
    assert "Generated stub" in files["FreshComponent.mo"]
    assert "package.mo" in files and "package.order" in files

    assert entry_class in class_names
    assert "tankDemo" in declared_instances
    assert "realOutput" in declared_instances
    assert "Modelica.Blocks.Interfaces.RealOutput realOutput;" in files[f"{entry_class}.mo"]
    # The requirement bound's actual value/unit must survive into the entry
    # class's parameter -- not just a bare, valueless declaration. The
    # parameter's own name is now readable (from the requirement's real
    # subject/property), not the bare fact id -- found live in OMEdit's
    # variable browser (every parameter showed up as "REQ0001", "REQ0002",
    # ...); see `naming.py`'s `readable_identifier`.
    assert 'parameter Real tankdemoH1High(unit="m") = 0.78;' in files[f"{entry_class}.mo"]


def test_generator_dedupes_class_names_case_insensitively() -> None:
    """Two class names differing only by case ("start"/"START") must not
    collide -- found live on a real dataset (see DECISIONS.md): Windows'
    (and macOS default) case-insensitive filesystem treats them as the
    same file, so whichever mapping saved second silently clobbered the
    other's class definition on disk, even though they were distinct,
    valid dict keys in memory."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL,
            target="start", reason="pushbutton entity", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.MODEL,
            target="START", reason="start-command interface", evidence=["EV-2"],
        ),
    ]
    files, _entry_class, class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )

    assert class_names.count("start") + class_names.count("START") == 1  # only one kept its bare name
    assert any(name in ("START_2", "start_2") for name in class_names)  # the other got deduped
    assert len(files) == len({k.lower() for k in files})  # no two filenames collide case-insensitively


def test_generator_skips_a_stub_already_covered_by_reused_legacy_code() -> None:
    """Confirmed against a real run (tank_003): extraction produced a
    separate `Entity` for a controller's internal "IDLE" state, which then
    got its own separate, EMPTY stub file -- even though the legacy class
    being reused for the controller ALREADY declares
    `type StepState = enumeration(IDLE, FILL);`. No `IDLE.mo` should be
    generated; the entry class should note why instead of silently
    dropping the concept."""

    legacy_models = [
        LegacyModel(
            filename="07_legacy_tank_demo.mo",
            classes=[
                LegacyClass(
                    kind="model", name="TankDemo_Rev12",
                    parameters=[LegacyParameter(name="h1High", type="Real", value="0.78", unit="m", line=2)],
                    type_declarations=["type StepState = enumeration(IDLE, FILL);"],
                )
            ],
        )
    ]
    mappings = _mappings() + [
        ModelicaMapping(
            sysml_element="ENT-0045", mapping_type=ModelicaMappingType.MODEL, target="IDLE",
            reason="ControllerState is a discrete state value", evidence=["EV-9"],
        )
    ]
    files, entry_class, class_names, declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), legacy_models, _sysml_semantic_model(), _sysml_contract_raw()
    )

    assert "IDLE.mo" not in files
    assert "IDLE" not in class_names
    assert "idle" not in {i.lower() for i in declared}
    assert "ENT-0045" in files[f"{entry_class}.mo"]  # explained, not silently dropped
    assert "TankDemo.mo" in files  # the genuinely reused class is unaffected


def test_generator_never_instantiates_an_undefined_type() -> None:
    """A LIBRARY_COMPONENT mapping whose target isn't a real, qualified MSL
    path (e.g. the mapper LLM reused a bare local legacy class name,
    "TankDemo_Rev12", instead of tagging it MODEL) must still get a real
    class generated for it -- found live on a real dataset (see
    DECISIONS.md): treating it as an already-defined library type left a
    dangling instantiation the real compiler correctly rejected as
    "Class ... not found in scope"."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="TankDemo_Rev12", reason="misclassified legacy reuse", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="a real MSL reference", evidence=["EV-2"],
        ),
    ]
    files, entry_class, class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )

    assert "TankDemo_Rev12.mo" in files  # a real class was generated for the bare-name target
    assert "TankDemo_Rev12" in class_names
    assert (
        "Modelica.Fluid.Vessels.OpenTank openTank(redeclare package Medium = "
        "Modelica.Media.Water.StandardWater, height = 1.0, crossArea = 1.0, use_portsData = false);"
        in files[f"{entry_class}.mo"]
    )


def test_generator_adds_default_medium_redeclaration_for_fluid_components() -> None:
    """A bare `Modelica.Fluid.*` instantiation compiles the generated file
    itself cleanly but fails inside the Modelica Standard Library's own
    implementation -- found live on a real dataset (see DECISIONS.md):
    `Modelica.Fluid.Vessels.OpenTank` declares its working fluid as a
    `replaceable package Medium = Modelica.Media.Interfaces.PartialMedium`,
    an abstract default with no concrete substance data, and the real
    compiler rejected it with "Constant openTank.Medium.singleState is
    used without having been given a value." Every `Modelica.Fluid`
    component needs a concrete `Medium` redeclaration; a non-`Fluid` MSL
    reference must be left untouched. A `Modelica.Fluid` class with no
    known mandatory parameters of its own gets the Medium fix only."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="tank", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Blocks.Interfaces.RealOutput", reason="sensor output", evidence=["EV-2"],
        ),
        ModelicaMapping(
            sysml_element="ENT-003", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Interfaces.FluidPort_a", reason="port", evidence=["EV-3"],
        ),
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )

    entry_text = files[f"{entry_class}.mo"]
    assert (
        "Modelica.Fluid.Vessels.OpenTank openTank(redeclare package Medium = "
        "Modelica.Media.Water.StandardWater, height = 1.0, crossArea = 1.0, use_portsData = false);"
        in entry_text
    )
    assert "Modelica.Blocks.Interfaces.RealOutput realOutput;" in entry_text  # non-Fluid MSL ref untouched
    assert (
        "Modelica.Fluid.Interfaces.FluidPort_a fluidPort_a"
        "(redeclare package Medium = Modelica.Media.Water.StandardWater);"
        in entry_text
    )  # a Fluid class with no registered mandatory parameters gets Medium only


def test_generator_adds_placeholder_values_for_valve_and_pump_mandatory_parameters() -> None:
    """`Modelica.Fluid.Valves.ValveIncompressible` (`dp_nominal`,
    `m_flow_nominal`) and `Modelica.Fluid.Machines.PrescribedPump`
    (`N_nominal`) each declare their own mandatory parameters with no MSL
    default, on top of the generic `Medium` requirement -- `dp_nominal`
    found live in OMEdit (see DECISIONS.md D46); `PrescribedPump` checked
    proactively against the same MSL source once the pattern was clear
    (same discipline as D37's pre-emptive compiler-agent fix)."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="valve", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Machines.PrescribedPump", reason="pump", evidence=["EV-2"],
        ),
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )
    entry_text = files[f"{entry_class}.mo"]
    assert (
        "Modelica.Fluid.Valves.ValveIncompressible valveIncompressible(redeclare package Medium = "
        "Modelica.Media.Water.StandardWater, dp_nominal = 100000, m_flow_nominal = 1.0, opening = 1.0);"
        in entry_text
    )
    assert (
        "Modelica.Fluid.Machines.PrescribedPump prescribedPump(redeclare package Medium = "
        "Modelica.Media.Water.StandardWater, N_nominal = 1500);"
        in entry_text
    )


def test_generator_deduplicates_instance_and_class_names_on_collision() -> None:
    """Two different SysML entities mapped to the same LIBRARY_COMPONENT
    target class (or the same new MODEL class name) must not collide --
    found live on a real dataset (see DECISIONS.md): two independently
    mapped tanks both rendered as `openTank`, and the real compiler
    correctly rejected the resulting duplicate declaration."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-101", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="tank 1", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-102", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="tank 2", evidence=["EV-2"],
        ),
        ModelicaMapping(
            sysml_element="ENT-103", mapping_type=ModelicaMappingType.MODEL,
            target="Valve", reason="valve 1, no legacy match", evidence=["EV-3"],
        ),
        ModelicaMapping(
            sysml_element="ENT-104", mapping_type=ModelicaMappingType.MODEL,
            target="Valve", reason="valve 2, no legacy match", evidence=["EV-4"],
        ),
    ]
    files, entry_class, class_names, declared_instances = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )

    assert declared_instances == {"openTank", "openTank_2", "valve", "valve_2"}
    assert class_names.count("Valve") == 1 and "Valve_2" in class_names
    assert "Valve.mo" in files and "Valve_2.mo" in files
    entry_text = files[f"{entry_class}.mo"]
    assert "openTank(redeclare package Medium = Modelica.Media.Water.StandardWater, height = 1.0, crossArea = 1.0, use_portsData = false);" in entry_text
    assert "openTank_2(redeclare package Medium = Modelica.Media.Water.StandardWater, height = 1.0, crossArea = 1.0, use_portsData = false);" in entry_text


def test_generator_keeps_algorithm_and_equation_sections_separate_on_legacy_reuse() -> None:
    """`:=` assignments must render under `algorithm`, never `equation` --
    found live on a real dataset (see DECISIONS.md): merging them produced
    a real compiler error."""

    legacy_model = LegacyModel(
        filename="07_legacy_tank_demo.mo",
        classes=[
            LegacyClass(
                kind="model", name="TankDemo_Rev12",
                parameters=[LegacyParameter(name="h1High", type="Real", value="0.78", unit="m", line=2)],
                algorithm_statements=["when edge(startCmd) then stopped := false; end when;"],
                equations=["der(tank1Level) = 1 - tank1Level;"],
            )
        ],
    )
    files, _entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), [legacy_model], _sysml_semantic_model(), _sysml_contract_raw()
    )

    text = files["TankDemo.mo"]
    algorithm_index = text.index("algorithm")
    equation_index = text.index("equation")
    assert algorithm_index < equation_index  # matches the original source's own section order
    assert ":=" in text[algorithm_index:equation_index]
    assert ":=" not in text[equation_index:]


def test_generator_renders_a_non_numeric_requirement_bound_as_a_string_parameter() -> None:
    """A requirement whose bound is free text (e.g. a named-mode
    description) can't be a Modelica `Real` -- found live on a real
    dataset (see DECISIONS.md), where this was emitted as a bare, unquoted
    non-numeric literal and failed the real compiler outright."""

    contract_raw = {
        "requirements": [
            {"id": "REQ-001", "subject": "TankDemo", "property": "mode", "min": None, "max": None,
             "value": "valid START command when process is idle or paused", "unit": None}
        ]
    }
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), contract_raw
    )
    text = files[f"{entry_class}.mo"]
    assert 'parameter String tankdemoMode = "valid START command when process is idle or paused";' in text
    assert "parameter Real tankdemoMode" not in text


def test_generator_gives_a_placeholder_value_when_no_requirement_bound_is_found() -> None:
    """A bare `parameter Real X;` (no value at all) passes this agent's own
    `checkModel()`-based compile check, but real Modelica translation --
    found live in OMEdit, not this agent's own check (see DECISIONS.md) --
    rejects it: "Parameter ... has neither value nor start value, and is
    fixed during initialization." Every `fixed=true` parameter (the
    default) needs a value to be simulatable; a placeholder must not be
    silently indistinguishable from a real one."""

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), {"requirements": []}
    )
    text = files[f"{entry_class}.mo"]
    # No matching requirement record -- falls back to the mapper's own
    # rationale text ("requirement bound") for a readable name, not the
    # bare fact id (see `_readable_identifier`'s fallback chain).
    assert "parameter Real requirementBound= 0.0;" in text
    assert "PLACEHOLDER" in text
    assert "parameter Real REQ001;" not in text


def test_generator_gives_a_placeholder_equation_to_a_never_assigned_legacy_variable() -> None:
    """A legacy variable never assigned anywhere in the reused class --
    found live on a real dataset (see DECISIONS.md D50): the original
    source itself never gives `startCmd`/`stopCmd`/`shutCmd`, or a
    `discrete` sequencer state like `seq`, a value either (they're meant
    to be driven by a sequencer/HMI this standalone fragment doesn't
    include) -- must not be silently left structurally undetermined.
    `discrete`/`start=` must also survive reuse, not just the `unit=`
    modifier the original renderer preserved. A state variable governed
    by its own `der(...)` equation (e.g. a tank level) must NOT also get
    a placeholder -- found live as a real regression in this same fix
    (see DECISIONS.md D50): the first version only checked for a direct
    assignment, so a `start=`-carrying level already fully determined by
    its ODE got a second, conflicting constant equation on top of it."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL, target="Controller1",
            reason="reuse legacy controller", evidence=["EV-1"],
        ),
    ]
    legacy_comparisons = [
        LegacyComparison(
            sysml_element="ENT-001", legacy_class="Controller_Rev1", legacy_file="controller.mo",
            matches=[], differences=[], recommendation=LegacyRecommendation.REUSE_AS_IS,
        )
    ]
    legacy_models = [
        LegacyModel(
            filename="controller.mo",
            classes=[
                LegacyClass(
                    kind="model", name="Controller_Rev1",
                    variables=[
                        LegacyVariable(name="shutCmd", type="Boolean", line=1),
                        LegacyVariable(name="seq", type="StepState", is_discrete=True, start_value="StepState.IDLE", line=2),
                        LegacyVariable(name="stopped", type="Boolean", line=3),
                        LegacyVariable(name="tank1Level", type="Real", start_value="h0", line=4),
                    ],
                    algorithm_statements=["when edge(shutCmd) then stopped := true; end when;"],
                    equations=["der(tank1Level) = qFill;"],
                )
            ],
        )
    ]

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), {"requirements": []}
    )
    text = files["Controller1.mo"]

    assert "discrete StepState seq(start=StepState.IDLE);" in text
    # No scheduled command was given in this fixture -- both fall back to
    # the same inert default as before, just proposed (and disclosed via
    # `pending_decisions`, checked in a separate test) rather than baked in
    # unconditionally.
    assert "shutCmd = false;  // PROPOSED, pending confirmation" in text
    assert "seq = StepState.IDLE;  // PROPOSED, pending confirmation" in text
    # `stopped` IS assigned (inside the algorithm's `when` clause) -- must
    # not get a fabricated placeholder equation of its own.
    assert "stopped = " not in text
    # `tank1Level` IS governed by its own `der(...)` equation -- must not
    # also get a conflicting constant placeholder.
    assert "tank1Level = " not in text
    assert "der(tank1Level) = qFill;" in text


def _controller_legacy_fixture():
    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL, target="Controller1",
            reason="reuse legacy controller", evidence=["EV-1"],
        ),
    ]
    legacy_comparisons = [
        LegacyComparison(
            sysml_element="ENT-001", legacy_class="Controller_Rev1", legacy_file="controller.mo",
            matches=[], differences=[], recommendation=LegacyRecommendation.REUSE_AS_IS,
        )
    ]
    legacy_models = [
        LegacyModel(
            filename="controller.mo",
            classes=[
                LegacyClass(
                    kind="model", name="Controller_Rev1",
                    variables=[LegacyVariable(name="startCmd", type="Boolean", line=1)],
                    algorithm_statements=["when edge(startCmd) then stopped := false; end when;"],
                )
            ],
        )
    ]
    return mappings, legacy_comparisons, legacy_models


def test_generator_proposes_a_real_pulse_for_a_variable_matching_a_scheduled_command() -> None:
    """Found live on the real Tank dataset: a test procedure specified an
    exact operator command schedule ("at 20s START, at 280s START, ...")
    with a benchmark ground-truth trace, but `startCmd` was left frozen
    `false` for the whole simulation -- structurally valid, physically
    inert (no tank level ever moved). When the project's own documents give
    a real schedule for a never-assigned variable, propose a real
    time-driven pulse instead of the inert default, and disclose it via
    `pending_decisions` rather than applying it unconditionally."""

    mappings, legacy_comparisons, legacy_models = _controller_legacy_fixture()
    sysml_contract_raw = {
        "requirements": [],
        "scheduled_commands": [
            {"id": "CMD-001", "command_name": "START", "time_value": 20.0},
            {"id": "CMD-002", "command_name": "START", "time_value": 280.0},
        ],
    }
    pending: list[dict] = []

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), sysml_contract_raw,
        pending_decisions=pending,
    )
    text = files["Controller1.mo"]

    assert "startCmd = (time >= 20.0 and time < 21.0) or (time >= 280.0 and time < 281.0);" in text
    assert "PROPOSED, pending confirmation" in text
    assert len(pending) == 1
    assert pending[0]["variable"] == "startCmd"
    assert pending[0]["suggested_value"] == "(time >= 20.0 and time < 21.0) or (time >= 280.0 and time < 281.0)"


def test_generator_applies_a_user_confirmed_override_without_a_placeholder_label() -> None:
    """Once a human confirms a value (via `command_overrides`), it's applied
    as final -- no longer flagged as pending, no longer labeled a
    placeholder at all."""

    mappings, legacy_comparisons, legacy_models = _controller_legacy_fixture()
    sysml_contract_raw = {
        "requirements": [],
        "scheduled_commands": [{"id": "CMD-001", "command_name": "START", "time_value": 20.0}],
    }
    pending: list[dict] = []

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), sysml_contract_raw,
        command_overrides={"startCmd": "(time >= 20.0 and time < 21.0)"},
        pending_decisions=pending,
    )
    text = files["Controller1.mo"]

    assert "startCmd = (time >= 20.0 and time < 21.0);  // user-approved" in text
    assert "PROPOSED" not in text
    assert "PLACEHOLDER" not in text
    assert pending == []  # already confirmed -- never raised as pending
    assert entry_class  # sanity: generation completed


def _sequencer_legacy_fixture():
    """A never-assigned discrete `StepState seq` -- the exact population an
    LLM-synthesized `StateMachine` targets (see `mapping/
    state_machine_synthesizer.py`), alongside a `tank1Level` real state
    variable already governed by its own `der(...)` (so it's a valid
    `condition_variable` reference, never a fabricated one)."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL, target="Sequencer1",
            reason="reuse legacy sequencer", evidence=["EV-1"],
        ),
    ]
    legacy_comparisons = [
        LegacyComparison(
            sysml_element="ENT-001", legacy_class="Sequencer_Rev1", legacy_file="sequencer.mo",
            matches=[], differences=[], recommendation=LegacyRecommendation.REUSE_AS_IS,
        )
    ]
    legacy_models = [
        LegacyModel(
            filename="sequencer.mo",
            classes=[
                LegacyClass(
                    kind="model", name="Sequencer_Rev1",
                    type_declarations=["type StepState = enumeration(IDLE, FILL, DONE);"],
                    variables=[
                        LegacyVariable(name="seq", type="StepState", is_discrete=True, start_value="StepState.IDLE", line=1),
                        LegacyVariable(name="tank1Level", type="Real", line=2),
                    ],
                    equations=["der(tank1Level) = 0.1;"],
                )
            ],
        )
    ]
    return mappings, legacy_comparisons, legacy_models


def test_generator_renders_a_verified_state_machine_for_a_never_assigned_sequencer_variable() -> None:
    """The core case this feature exists for: `seq` is never assigned in the
    reused legacy source (meant to be driven by a sequencer this fragment
    doesn't include), and an LLM-synthesized `StateMachine` -- referencing
    only real behavior/requirement ids and a real, already-declared
    variable name -- renders as an actual transition chain, not the old
    inert default."""

    mappings, legacy_comparisons, legacy_models = _sequencer_legacy_fixture()
    sysml_contract_raw = {
        "requirements": [{"id": "REQ-010", "subject": "S", "property": "wait", "operator": "==", "value": 30.0}],
        "behaviors": [
            {
                "id": "BEH-001", "trigger_property": "Tank 1 level", "trigger_operator": ">=",
                "trigger_value": 0.78, "action_type": "transition", "action_target": "seq",
            },
        ],
    }
    state_machines = [
        {
            "state_machine_id": "SM-001",
            "target_type_hint": "StepState",
            "states": ["IDLE", "FILL", "DONE"],
            "initial_state": "IDLE",
            "transitions": [
                {
                    "from_state": "IDLE", "to_state": "FILL", "trigger_behavior_id": "BEH-001",
                    "condition_variable": "tank1Level", "reason": "fill begins once the level check triggers",
                },
                {
                    "from_state": "FILL", "to_state": "DONE", "wait_parameter_id": "REQ-010",
                    "reason": "hold for the required wait duration",
                },
            ],
        }
    ]

    files, _entry, _classes, _declared = generate_modelica_files(
        "seq_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), sysml_contract_raw,
        state_machines=state_machines,
    )
    text = files["Sequencer1.mo"]

    assert "discrete Real seqEnteredAt(start=0);" in text
    # Chained into ONE when/elsewhen clause, both guards reading pre(...) --
    # found live via a real `omc` compile: two separate `when` clauses each
    # assigning `seq` over-determined the system, and a guard reading the
    # raw (non-`pre`) state/timer produced a real discrete algebraic loop.
    assert "when pre(seq) == StepState.IDLE and tank1Level >= 0.78 then" in text
    assert "seq = StepState.FILL;" in text
    assert "elsewhen pre(seq) == StepState.FILL and time - pre(seqEnteredAt) >= 30.0 then" in text
    assert "seq = StepState.DONE;" in text
    assert text.count("end when;") >= 1 and "when pre(seq)" in text and "elsewhen pre(seq)" in text
    assert text.count("seqEnteredAt = time;") == 2  # reset on every transition, not just the first
    assert "PROPOSED, pending confirmation" not in text  # a real state machine, not the old inert fallback


def test_generator_rejects_a_state_machine_with_an_invented_state_name() -> None:
    """A proposed state name that isn't one of the enum's REAL declared
    literals is rejected wholesale -- falls back to the existing, honest
    placeholder-equation path rather than emitting `seq :=
    StepState.TRANSFER` for a literal that doesn't exist."""

    mappings, legacy_comparisons, legacy_models = _sequencer_legacy_fixture()
    sysml_contract_raw = {"requirements": [], "behaviors": []}
    state_machines = [
        {
            "state_machine_id": "SM-001", "target_type_hint": "StepState",
            "states": ["IDLE", "FILL", "TRANSFER"],  # "TRANSFER" is not a real literal of StepState
            "initial_state": "IDLE",
            "transitions": [{"from_state": "IDLE", "to_state": "TRANSFER", "wait_parameter_id": "REQ-XXX"}],
        }
    ]

    files, _entry, _classes, _declared = generate_modelica_files(
        "seq_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), sysml_contract_raw,
        state_machines=state_machines,
    )
    text = files["Sequencer1.mo"]

    assert "StepState.TRANSFER" not in text
    assert "seq = StepState.IDLE;  // PROPOSED, pending confirmation" in text


def test_generator_discloses_a_state_machine_transition_it_cannot_verify() -> None:
    """A transition referencing a behavior id that was never actually
    extracted is dropped with an honest comment, never rendered as a real
    `when` block with a guessed condition."""

    mappings, legacy_comparisons, legacy_models = _sequencer_legacy_fixture()
    sysml_contract_raw = {"requirements": [], "behaviors": []}
    state_machines = [
        {
            "state_machine_id": "SM-001", "target_type_hint": "StepState",
            "states": ["IDLE", "FILL", "DONE"], "initial_state": "IDLE",
            "transitions": [
                {
                    "from_state": "IDLE", "to_state": "FILL", "trigger_behavior_id": "BEH-NONEXISTENT",
                    "condition_variable": "tank1Level",
                },
            ],
        }
    ]

    files, _entry, _classes, _declared = generate_modelica_files(
        "seq_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), sysml_contract_raw,
        state_machines=state_machines,
    )
    text = files["Sequencer1.mo"]

    assert "state machine transition IDLE -> FILL skipped" in text
    assert "when seq ==" not in text


def test_generator_adds_inner_fluid_system_when_a_fluid_component_is_present() -> None:
    """`Modelica.Fluid.*` components use an `outer system` reference for
    ambient conditions -- without a matching `inner` declaration, real
    Modelica translation only emits a warning and silently auto-generates
    one (found live in OMEdit; see DECISIONS.md). A model with no Fluid
    component must not get one it doesn't need."""

    fluid_mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="tank", evidence=["EV-1"],
        ),
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", fluid_mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )
    assert "inner Modelica.Fluid.System system;" in files[f"{entry_class}.mo"]

    non_fluid_mappings = [
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Blocks.Interfaces.RealOutput", reason="sensor output", evidence=["EV-2"],
        ),
    ]
    files2, entry_class2, _class_names2, _declared2 = generate_modelica_files(
        "tank_001", non_fluid_mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )
    assert "inner Modelica.Fluid.System system;" not in files2[f"{entry_class2}.mo"]


def test_generator_connects_a_tank_to_a_valve_via_real_ports() -> None:
    """A SysML connection between two known Fluid classes (OpenTank's
    `ports[nPorts]` array, ValveIncompressible's fixed `port_a`/`port_b`)
    now becomes a real `connect()`, not just a comment -- found live in
    OMEdit (see DECISIONS.md D47): with no real wiring, every Fluid port
    was structurally unconnected and the solver reported "Too few
    equations". The tank's `nPorts` must be sized to match, and the
    valve's still-open `port_b` must get its own boundary condition."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="tank", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="valve", evidence=["EV-2"],
        ),
    ]
    sysml_semantic_model = SysMLSemanticModel(
        parts=[
            SysMLPart(instance_name="tank1", part_def="Tank1"),
            SysMLPart(instance_name="valve1", part_def="Valve1"),
        ],
        connections=[SysMLConnection(source_instance="tank1", target_instance="valve1", relationship_type="CONNECTED_TO")],
    )
    engineering_id_by_name = {"Tank1": "ENT-001", "Valve1": "ENT-002"}

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], sysml_semantic_model, {"requirements": []}, engineering_id_by_name
    )
    text = files[f"{entry_class}.mo"]

    assert (
        "Modelica.Fluid.Vessels.OpenTank openTank(redeclare package Medium = Modelica.Media.Water.StandardWater, "
        "height = 1.0, crossArea = 1.0, use_portsData = false, nPorts = 1);"
        in text
    )
    assert "connect(openTank.ports[1], valveIncompressible.port_a);" in text
    assert "connect(valveIncompressible.port_b, valveIncompressible_port_b_boundary.ports[1]);" in text
    assert (
        "Modelica.Fluid.Sources.Boundary_pT valveIncompressible_port_b_boundary"
        "(redeclare package Medium = Modelica.Media.Water.StandardWater, nPorts = 1, p = 151325);"
        in text
    )


def test_generator_adds_boundary_sources_for_a_completely_unconnected_valve() -> None:
    """A two-port Fluid component with *no* SysML connection at all still
    has two always-present, structurally unconnected ports -- both need a
    boundary condition, not just a port left over from a partial wiring."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="valve", evidence=["EV-1"],
        ),
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )
    text = files[f"{entry_class}.mo"]

    assert "connect(valveIncompressible.port_a, valveIncompressible_port_a_boundary.ports[1]);" in text
    assert "connect(valveIncompressible.port_b, valveIncompressible_port_b_boundary.ports[1]);" in text


def test_generator_discloses_the_auto_boundary_pressure_as_a_grounded_pending_decision() -> None:
    """Found live in this session's own gap audit: the staggered auto-
    boundary pressure was applied unconditionally with no `pending_
    decisions` entry -- a human running the pipeline was never told an
    auto-boundary was inserted. Now disclosed, but `grounded=True` (never
    sent through the LLM parameter-value refiner, which could easily
    reintroduce the exact symmetric-pressure bug this staggering exists to
    prevent) -- and a confirmed override with real plant data is honored."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="valve", evidence=["EV-1"],
        ),
    ]
    pending: list[dict] = []

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}, pending_decisions=pending,
    )

    boundary_pending = [p for p in pending if p["class_name"] == "Modelica.Fluid.Sources.Boundary_pT"]
    assert len(boundary_pending) == 2  # one per open port
    assert all(p["grounded"] is True for p in boundary_pending)
    assert any(p["variable"] == "valveIncompressible_port_a_boundary.p" for p in boundary_pending)

    files2, entry_class2, _classes2, _declared2 = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []},
        command_overrides={"valveIncompressible_port_a_boundary.p": "150000"},
    )
    text2 = files2[f"{entry_class2}.mo"]
    assert "p = 150000" in text2
    assert "(user-approved pressure)" in text2


def test_generator_staggers_boundary_pressures_to_avoid_a_symmetric_network() -> None:
    """A valve bounded on *both* ends by the identical default `Boundary_pT`
    pressure has zero driving pressure differential -- an outright
    mathematically indeterminate flow direction, found live in a real
    `simulate()` run (see DECISIONS.md D52) as an unresolved
    `relativeFlowCoefficient`, not a missing-value problem. Every
    auto-boundary in the model must get its own distinct placeholder
    pressure, never sharing one with another auto-boundary."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="valve", evidence=["EV-1"],
        ),
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )
    text = files[f"{entry_class}.mo"]

    pressures = set(re.findall(r"Boundary_pT \S+\([^)]*p = (\d+)\)", text))
    assert len(pressures) == 2  # both auto-boundaries got a distinct pressure, not the same one


def test_generator_does_not_leak_a_port_when_the_other_endpoint_has_none_left() -> None:
    """Found live on a real dataset (see DECISIONS.md D49): the connect()
    resolver popped the *source* endpoint's port before checking whether
    the *target* endpoint had one available at all -- when the target
    turned out to be already fully connected, the loop skipped that
    connection but never returned the already-popped source port, silently
    losing it. No `connect()` and no boundary source were ever generated
    for it, leaving a real Fluid port structurally unconnected exactly as
    if this whole fix didn't exist -- confirmed live as a real, still-
    present "Too few equations" solver error even after every known
    mandatory-parameter gap (D42/D45/D46/D48) was already fixed."""

    mappings = [
        ModelicaMapping(sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
                         target="Modelica.Fluid.Valves.ValveIncompressible", reason="valveA", evidence=["EV-1"]),
        ModelicaMapping(sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
                         target="Modelica.Fluid.Valves.ValveIncompressible", reason="valveC", evidence=["EV-2"]),
        ModelicaMapping(sysml_element="ENT-003", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
                         target="Modelica.Fluid.Valves.ValveIncompressible", reason="valveD", evidence=["EV-3"]),
        ModelicaMapping(sysml_element="ENT-004", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
                         target="Modelica.Fluid.Valves.ValveIncompressible", reason="valveB", evidence=["EV-4"]),
    ]
    sysml_semantic_model = SysMLSemanticModel(
        parts=[
            SysMLPart(instance_name="valveA", part_def="ValveA"),
            SysMLPart(instance_name="valveC", part_def="ValveC"),
            SysMLPart(instance_name="valveD", part_def="ValveD"),
            SysMLPart(instance_name="valveB", part_def="ValveB"),
        ],
        connections=[
            SysMLConnection(source_instance="valveA", target_instance="valveC", relationship_type="CONNECTED_TO"),
            SysMLConnection(source_instance="valveA", target_instance="valveD", relationship_type="CONNECTED_TO"),
            # valveA (instance "valveIncompressible") now has both ports
            # used -- this third connection's target is fully exhausted.
            SysMLConnection(source_instance="valveB", target_instance="valveA", relationship_type="CONNECTED_TO"),
        ],
    )
    engineering_id_by_name = {"ValveA": "ENT-001", "ValveC": "ENT-002", "ValveD": "ENT-003", "ValveB": "ENT-004"}

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], sysml_semantic_model, {"requirements": []}, engineering_id_by_name
    )
    text = files[f"{entry_class}.mo"]

    # valveB (the source of the failed 3rd connection, instance
    # "valveIncompressible_4") must keep both of its own ports -- neither
    # popped-and-lost, each gets its own boundary source.
    assert "connect(valveIncompressible_4.port_a, valveIncompressible_4_port_a_boundary.ports[1]);" in text
    assert "connect(valveIncompressible_4.port_b, valveIncompressible_4_port_b_boundary.ports[1]);" in text


def test_generator_gives_a_placeholder_to_a_bare_signal_connector_instance() -> None:
    """A standalone `Modelica.Blocks.Interfaces.RealOutput` instance (a
    connector *type*, not a value-computing component) has nothing feeding
    it a value -- found live in a real `simulate()` run (see DECISIONS.md
    D52): "Variable realOutput does not have any remaining equation to be
    solved in." This pipeline doesn't wire signal-level connect()s, so any
    such instance is unconditionally left undetermined otherwise."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Blocks.Interfaces.RealOutput", reason="sensor output", evidence=["EV-1"],
        ),
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}
    )
    text = files[f"{entry_class}.mo"]
    assert "realOutput = 0.0;  // PLACEHOLDER: bare signal connector, nothing drives it" in text


def test_generator_does_not_fabricate_connect_for_unknown_component_classes() -> None:
    """A connection between two components that aren't known Fluid classes
    (e.g. legacy-reuse/MODEL stubs) must still render only as a comment --
    this agent doesn't know their port names, and a guessed one would very
    likely fail to compile while looking confidently correct."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.MODEL, target="Controller1",
            reason="no legacy match", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.MODEL, target="Controller2",
            reason="no legacy match", evidence=["EV-2"],
        ),
    ]
    sysml_semantic_model = SysMLSemanticModel(
        parts=[
            SysMLPart(instance_name="controller1", part_def="Controller1"),
            SysMLPart(instance_name="controller2", part_def="Controller2"),
        ],
        connections=[SysMLConnection(source_instance="controller1", target_instance="controller2", relationship_type="CONNECTED_TO")],
    )

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, [], [], sysml_semantic_model, {"requirements": []}
    )
    text = files[f"{entry_class}.mo"]

    assert "connect(" not in text
    assert "// connect: controller1 -> controller2  (CONNECTED_TO)" in text


def test_generator_normalizes_caret_units_to_modelica_convention() -> None:
    """Modelica unit strings don't use `^` for exponents ("m3/s", not
    "m^3/s") -- found live on a real dataset where the source document's
    unit was written the human way. The generator must fix this at the
    point it renders Modelica syntax, not rely on the validator to shrug
    it off."""

    contract_raw = {
        "requirements": [
            {"id": "REQ-001", "subject": "TankDemo", "property": "flow", "min": None, "max": 0.006, "value": None, "unit": "m^3/s"}
        ]
    }
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), contract_raw
    )
    assert 'unit="m3/s"' in files[f"{entry_class}.mo"]
    assert "m^3/s" not in files[f"{entry_class}.mo"]


def test_generator_applies_modify_legacy_override() -> None:
    comparisons = [
        LegacyComparison(
            sysml_element="ENT-001", legacy_class="TankDemo_Rev12", legacy_file="07_legacy_tank_demo.mo",
            matches=[], differences=["SysML requires 0.7 m for h1High, legacy model uses 0.78"],
            recommendation=LegacyRecommendation.MODIFY_LEGACY, overrides={"h1High": "0.7"},
        )
    ]
    files, _entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), comparisons, _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw()
    )
    assert "= 0.7;" in files["TankDemo.mo"]


def _behavior_equation_mapping(**overrides) -> ModelicaMapping:
    fields = {
        "sysml_element": "BEH-001",
        "mapping_type": ModelicaMappingType.EQUATION,
        "target": "n/a",
        "reason": "close valve when tank level exceeds threshold",
        "evidence": ["EV-9"],
    }
    fields.update(overrides)
    return ModelicaMapping(**fields)


def _sysml_contract_raw_with_behavior() -> dict:
    contract = _sysml_contract_raw()
    contract["behaviors"] = [{"id": "BEH-001", "trigger_operator": ">", "trigger_value": 8}]
    return contract


def test_generator_renders_a_real_when_block_for_a_resolved_behavior_equation() -> None:
    """ENT-001 -> instance "tankDemo", ENT-002 -> instance "realOutput" (see
    `test_generator_produces_expected_files_and_reuses_legacy_class`) -- both
    real, declared components, so the mapper's claimed references resolve
    and a real `when` block must render, not just the fallback comment."""

    mappings = _mappings() + [
        _behavior_equation_mapping(
            trigger_variable="ENT-001.level", action_variable="ENT-002.opening", action_value="0",
        )
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_behavior()
    )
    body = files[f"{entry_class}.mo"]
    assert "when tankDemo.level > 8 then" in body
    assert "realOutput.opening = 0;" in body
    assert "end when;" in body


def test_generator_falls_back_to_comment_when_behavior_fields_are_left_null() -> None:
    """The mapper leaving trigger/action null (its documented "not confident"
    signal) must render the same honest comment as before -- no regression
    for the common, unresolved case."""

    mappings = _mappings() + [_behavior_equation_mapping()]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_behavior()
    )
    body = files[f"{entry_class}.mo"]
    assert "end when;" not in body  # no real when-block rendered (the comment text itself legitimately says "when")
    assert "// close valve when tank level exceeds threshold" in body


def test_generator_falls_back_to_comment_when_the_claimed_component_id_does_not_exist() -> None:
    """The safety net: even if the mapper confidently fills in trigger/action/
    value, a reference to a component id that was never actually declared
    must NOT render as real code -- it would be a wrong-but-confident
    `when` clause wired to nothing, exactly what this check exists to catch."""

    mappings = _mappings() + [
        _behavior_equation_mapping(
            trigger_variable="ENT-999.level", action_variable="ENT-002.opening", action_value="0",
        )
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_behavior()
    )
    body = files[f"{entry_class}.mo"]
    assert "end when;" not in body
    assert "// close valve when tank level exceeds threshold" in body


def _control_law_mapping(**overrides) -> ModelicaMapping:
    fields = {
        "sysml_element": "CTL-001",
        "mapping_type": ModelicaMappingType.EQUATION,
        "target": "n/a",
        "reason": "fan speed proportional to CO2 excess",
        "evidence": ["EV-9"],
    }
    fields.update(overrides)
    return ModelicaMapping(**fields)


def _sysml_contract_raw_with_control_law() -> dict:
    contract = _sysml_contract_raw()
    contract["control_laws"] = [{"id": "CTL-001", "law_type": "PROPORTIONAL"}]
    return contract


def test_generator_renders_a_real_equation_for_a_resolved_proportional_control_law() -> None:
    mappings = _mappings() + [
        _control_law_mapping(
            control_law_type="PROPORTIONAL", control_input_variable="ENT-001.co2",
            control_output_variable="ENT-002.fanSpeed", control_gain_p=0.5, control_setpoint=800.0,
        )
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_control_law()
    )
    body = files[f"{entry_class}.mo"]
    assert "realOutput.fanSpeed = 0.5 * (tankDemo.co2 - 800.0);" in body
    assert "// fan speed proportional to CO2 excess" in body


def test_generator_renders_a_pi_control_law_with_a_real_integrator_state() -> None:
    mappings = _mappings() + [
        _control_law_mapping(
            control_law_type="PI", control_input_variable="ENT-001.co2", control_output_variable="ENT-002.fanSpeed",
            control_gain_p=0.5, control_gain_i=0.1, control_setpoint=800.0,
        )
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_control_law()
    )
    body = files[f"{entry_class}.mo"]
    assert "Real controlIntegral1(start=0);" in body
    assert "der(controlIntegral1) = (tankDemo.co2 - 800.0);" in body
    assert "realOutput.fanSpeed = 0.5 * (tankDemo.co2 - 800.0) + 0.1 * controlIntegral1;" in body


def test_generator_falls_back_to_comment_when_control_law_gain_is_missing() -> None:
    """The extractor was explicitly told never to invent a gain -- a control
    law with no stated gain_p must stay an honest comment, not a fabricated
    equation with a made-up coefficient."""

    mappings = _mappings() + [
        _control_law_mapping(
            control_law_type="PROPORTIONAL", control_input_variable="ENT-001.co2",
            control_output_variable="ENT-002.fanSpeed",
        )
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_control_law()
    )
    body = files[f"{entry_class}.mo"]
    assert "fanSpeed =" not in body
    assert "// fan speed proportional to CO2 excess" in body


def test_generator_falls_back_to_comment_when_control_law_component_id_does_not_exist() -> None:
    mappings = _mappings() + [
        _control_law_mapping(
            control_law_type="PROPORTIONAL", control_input_variable="ENT-999.co2",
            control_output_variable="ENT-002.fanSpeed", control_gain_p=0.5, control_setpoint=800.0,
        )
    ]
    files, entry_class, _class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw_with_control_law()
    )
    body = files[f"{entry_class}.mo"]
    assert "fanSpeed =" not in body
    assert "// fan speed proportional to CO2 excess" in body


def test_full_validation_passes_on_well_formed_input() -> None:
    files, _entry_class, class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw()
    )
    component_mappings = [m for m in _mappings() if m.mapping_type.value in ("MODEL", "BLOCK", "LIBRARY_COMPONENT")]
    bounds = [{"subject": "TankDemo", "property": "h1High", "min": None, "max": 0.78, "value": None, "unit": "m"}]

    result = validate_generation("v0001", files, class_names, [], component_mappings, bounds)

    assert result.status.value == "PASSED"
    assert result.issues == []


def test_validation_catches_the_same_entity_mapped_to_two_separate_component_instances() -> None:
    """The topology-conservation check: real bug found live -- unresolved
    entity/mapping duplication produced 6 tank instances standing in for 2
    real tanks. Two LIBRARY_COMPONENT/MODEL/BLOCK mappings sharing one
    `sysml_element` means the same canonical real-world entity would be
    instantiated twice -- must fail structural validation."""

    mappings = _mappings() + [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Vessels.OpenTank", reason="duplicate mapping for the same tank",
        ),
    ]
    files, _entry_class, class_names, _declared = generate_modelica_files(
        "tank_001", mappings, _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw()
    )
    component_mappings = [m for m in mappings if m.mapping_type.value in ("MODEL", "BLOCK", "LIBRARY_COMPONENT")]

    result = validate_generation("v0001", files, class_names, [], component_mappings, [])

    assert result.status.value == "FAILED"
    assert any("ENT-001" in issue.element and "more than one component-creating mapping" in issue.message for issue in result.issues)


def test_validation_does_not_flag_a_connection_to_an_undeclared_instance() -> None:
    """A SysML connection whose endpoint never became a declared Modelica
    instance is rendered as a `// connect: ...` comment (see
    `generation/modelica_generator.py`), never a real `connect()` call --
    so it's not a dangling reference in the actual generated syntax, and
    must not fail validation. Found live (see DECISIONS.md): the previous
    version of this check flagged exactly this as a false positive on a
    real dataset."""

    files, _entry_class, class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(),
        _sysml_semantic_model(target_instance="ghostInstance"), _sysml_contract_raw(),
    )
    component_mappings = [m for m in _mappings() if m.mapping_type.value in ("MODEL", "BLOCK", "LIBRARY_COMPONENT")]

    result = validate_generation("v0001", files, class_names, [], component_mappings, [])

    assert result.status.value == "PASSED"
    assert "// connect: tankDemo -> ghostInstance" in files[f"{_entry_class}.mo"]


def test_validation_catches_min_greater_than_max() -> None:
    files, _entry_class, class_names, _declared = generate_modelica_files(
        "tank_001", _mappings(), _legacy_comparisons(), _legacy_models(), _sysml_semantic_model(), _sysml_contract_raw()
    )
    bounds = [{"subject": "TankDemo", "property": "h1High", "min": 5.0, "max": 1.0, "value": None, "unit": "m"}]

    result = validate_generation("v0001", files, class_names, [], [], bounds)

    assert result.status.value == "FAILED"
    assert any("greater than max" in issue.message for issue in result.issues)


def test_generator_connects_a_series_electrical_chain_with_one_shared_ground() -> None:
    """A potential-based domain (Electrical/Magnetic) is NOT Fluid --
    exactly one shared reference per connected network, not one boundary
    per open port. Two components in series form ONE connected network
    with TWO leftover ports (each component's far end) -- only one gets
    the shared ground; the other must be honestly disclosed, never
    silently dropped."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Electrical.Analog.Basic.Resistor", reason="winding resistance", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Electrical.Analog.Basic.Inductor", reason="winding inductance", evidence=["EV-2"],
        ),
    ]
    sysml_semantic_model = SysMLSemanticModel(
        parts=[
            SysMLPart(instance_name="r1", part_def="R1"),
            SysMLPart(instance_name="l1", part_def="L1"),
        ],
        connections=[SysMLConnection(source_instance="r1", target_instance="l1", relationship_type="CONNECTED_TO")],
    )
    engineering_id_by_name = {"R1": "ENT-001", "L1": "ENT-002"}

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "mag_001", mappings, [], [], sysml_semantic_model, {"requirements": []}, engineering_id_by_name
    )
    body = files[f"{entry_class}.mo"]

    assert "connect(resistor.p, inductor.p);" in body  # the one real connection between them
    ground_declarations = [line for line in body.splitlines() if "Basic.Ground " in line]
    assert len(ground_declarations) == 1  # exactly one shared reference for the whole network, not two
    # "inductor" sorts before "resistor" -- it's the chosen anchor for the shared ground.
    assert "connect(inductor.n, inductor_reference_1.p);" in body
    assert "resistor.n left unconnected" in body  # the OTHER open end is disclosed, not silently dropped


def test_generator_does_not_fabricate_a_connection_for_the_four_port_coil() -> None:
    """`ElectroMagneticConverter` (the coil) has FOUR ports across two
    connector kinds at once -- deliberately excluded from the plain
    two-port matcher rather than guessed at."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Magnetic.FluxTubes.Basic.ElectroMagneticConverter", reason="coil", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-002", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance", reason="core", evidence=["EV-2"],
        ),
    ]
    sysml_semantic_model = SysMLSemanticModel(
        parts=[
            SysMLPart(instance_name="coil1", part_def="Coil1"),
            SysMLPart(instance_name="core1", part_def="Core1"),
        ],
        connections=[SysMLConnection(source_instance="coil1", target_instance="core1", relationship_type="CONNECTED_TO")],
    )
    engineering_id_by_name = {"Coil1": "ENT-001", "Core1": "ENT-002"}

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "mag_001", mappings, [], [], sysml_semantic_model, {"requirements": []}, engineering_id_by_name
    )
    body = files[f"{entry_class}.mo"]

    assert "connect(electroMagneticConverter" not in body  # never guessed a port on the 4-port class
    assert "// connect: coil1 -> core1" in body  # falls back to the generic comment, honestly


def test_generator_declares_the_fields_a_behavior_references_on_a_from_scratch_stub() -> None:
    """Found live: a from-scratch MODEL/BLOCK stub with no legacy match
    previously declared NOTHING at all, so a real behavior referencing one
    of its fields (`trigger_variable`/`action_variable`) produced a
    guaranteed "field not found" compile error -- not a placeholder-value
    problem, a genuinely missing symbol. The assigned field (the action)
    needs no equation of its own (the behavior's own equation governs it);
    the read-only field (the trigger, a sensed quantity this from-scratch
    stub has no real physics for) gets the same disclosed propose-then-
    confirm treatment as a never-assigned legacy variable."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-CTRL", mapping_type=ModelicaMappingType.MODEL, target="Controller",
            reason="from-scratch controller", evidence=["EV-1"],
        ),
        ModelicaMapping(
            sysml_element="ENT-TANK", mapping_type=ModelicaMappingType.MODEL, target="TankB5",
            reason="from-scratch tank level source", evidence=["EV-2"],
        ),
        ModelicaMapping(
            sysml_element="BEH-001", mapping_type=ModelicaMappingType.EQUATION, target="",
            reason="heater on above target level", evidence=["EV-3"],
            trigger_variable="ENT-TANK.level", action_variable="ENT-CTRL.heaterOn", action_value="true",
        ),
    ]
    sysml_contract_raw = {
        "requirements": [],
        "behaviors": [
            {
                "id": "BEH-001", "trigger_property": "tank level", "trigger_operator": ">=",
                "trigger_value": 0.5, "action_type": "set", "action_target": "heater",
            }
        ],
    }
    pending: list[dict] = []

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "nacl_001", mappings, [], [], SysMLSemanticModel(), sysml_contract_raw, pending_decisions=pending,
    )

    assert "Boolean heaterOn;" in files["Controller.mo"]
    assert "heaterOn = " not in files["Controller.mo"]  # assigned by the real behavior equation, not here

    tank_text = files["TankB5.mo"]
    assert "Real level;" in tank_text
    assert "level = 0.0;  // PROPOSED, pending confirmation" in tank_text
    assert any(p["variable"] == "TankB5.level" for p in pending)

    entry_text = files[f"{entry_class}.mo"]
    assert "when tankB5.level >= 0.5 then" in entry_text
    assert "controller.heaterOn = true;" in entry_text


def test_generator_raises_a_pending_decision_for_a_generic_library_placeholder() -> None:
    """`_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS` (e.g. `ValveIncompressible`'s
    `opening=1.0`) compiles and simulates fine, but has no connection to
    the actual problem -- raised as a pending decision (grounded=False, so
    `mapping/parameter_value_suggester.py` will refine it) rather than
    silently baked in, same as any other never-confirmed value."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="control valve", evidence=["EV-1"],
        ),
    ]
    pending: list[dict] = []

    files, entry_class, _classes, _declared = generate_modelica_files(
        "valve_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}, pending_decisions=pending,
    )

    # The valve's own two open ports also raise their own (correctly
    # `grounded=True`, since staggered pressure is a deliberate numerical
    # technique, not a value to refine) auto-boundary pending decisions --
    # filter down to the library-placeholder-parameter ones this test
    # actually cares about.
    placeholder_pending = [p for p in pending if p["class_name"] == "Modelica.Fluid.Valves.ValveIncompressible"]
    variables = {p["variable"] for p in placeholder_pending}
    assert any(v.endswith(".opening") for v in variables)
    assert any(v.endswith(".dp_nominal") for v in variables)
    assert all(p.get("grounded") is False for p in placeholder_pending)
    entry_text = files[f"{entry_class}.mo"]
    assert "opening = 1.0" in entry_text  # unconfirmed -- generic default still applied provisionally


def test_generator_applies_a_confirmed_override_for_a_library_placeholder() -> None:
    """Once a human confirms a real value (via `command_overrides`, keyed
    `"{instance}.{parameter}"`), it's used instead of the generic
    default -- no pending decision raised again for it."""

    mappings = [
        ModelicaMapping(
            sysml_element="ENT-001", mapping_type=ModelicaMappingType.LIBRARY_COMPONENT,
            target="Modelica.Fluid.Valves.ValveIncompressible", reason="control valve", evidence=["EV-1"],
        ),
    ]
    pending: list[dict] = []

    files, entry_class, _classes, _declared = generate_modelica_files(
        "valve_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []},
        command_overrides={"valveIncompressible.dp_nominal": "50000"}, pending_decisions=pending,
    )

    entry_text = files[f"{entry_class}.mo"]
    assert "dp_nominal = 50000" in entry_text
    assert not any(p["variable"] == "valveIncompressible.dp_nominal" for p in pending)
    assert any(p["variable"] == "valveIncompressible.opening" for p in pending)  # still unconfirmed


def test_generator_raises_a_pending_decision_for_a_parameter_with_no_bound() -> None:
    """A PARAMETER mapping with no matching requirement bound previously
    baked in a silent `0.0` -- now raised as a pending decision too, and a
    confirmed override is applied instead."""

    mappings = [
        ModelicaMapping(
            sysml_element="REQ-999", mapping_type=ModelicaMappingType.PARAMETER, target="Real",
            reason="unresolved requirement bound", evidence=["EV-1"],
        ),
    ]
    pending: list[dict] = []

    files, entry_class, _classes, _declared = generate_modelica_files(
        "param_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []}, pending_decisions=pending,
    )
    text = files[f"{entry_class}.mo"]

    # No matching requirement record -- falls back to the mapper's own
    # rationale text ("unresolved requirement bound") for a readable
    # name, not the bare fact id.
    assert "parameter Real unresolvedRequirementBound= 0.0;" in text
    assert "PLACEHOLDER, pending confirmation" in text
    assert len(pending) == 1 and pending[0]["variable"] == "unresolvedRequirementBound" and pending[0]["grounded"] is False

    files2, entry_class2, _classes2, _declared2 = generate_modelica_files(
        "param_001", mappings, [], [], SysMLSemanticModel(), {"requirements": []},
        command_overrides={"unresolvedRequirementBound": "2.5"},
    )
    text2 = files2[f"{entry_class2}.mo"]
    assert "parameter Real unresolvedRequirementBound= 2.5;  // unresolved requirement bound (user-approved)" in text2
