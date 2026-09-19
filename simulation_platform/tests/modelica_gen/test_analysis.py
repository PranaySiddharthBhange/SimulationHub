"""Step 1 -- Analyze SysML/legacy Modelica. Deterministic, no LLM.

The legacy fixture below is the real `07_legacy_tank_demo.mo` content from
the Tank golden dataset (see `document-agent/projects/tank_003/source/
original/06_legacy_code/`), not a simplified stand-in -- proving the
parameter-modifier regex actually handles `parameter Real A1(unit="m2") =
1.20;`, which the Document Agent's own simpler Modelica parser regex does
not attempt to parse out (see `analysis/legacy_analyzer.py` docstring).
"""

from __future__ import annotations

from simulation_platform.modelica_gen.analysis import analyze_legacy_file, analyze_sysml_files

_REAL_LEGACY_TANK_MO = """\
within SyntheticTankDemo;
model TankDemo_Rev12
  // Archived 02-Feb-2026. This model predates later approved controls changes.
  parameter Real A1(unit="m2") = 1.20;
  parameter Real qFill(unit="m3/s") = 0.0060;
  parameter Real wait1(unit="s") = 10;

  Real tank1Level(start=h0, unit="m");
  Boolean valve1;

  type StepState = enumeration(IDLE,FILL,HOLD1,TRANSFER,HOLD2,DRAIN,HOLD3);
  discrete StepState seq(start=StepState.IDLE);

algorithm
  when edge(startCmd) then stopped := false; end when;
  valve1 := (seq == StepState.FILL);

equation
  der(tank1Level) = (if valve1 then qFill else 0)/A1;
end TankDemo_Rev12;
"""


def test_legacy_analyzer_parses_real_tank_dataset_file() -> None:
    model = analyze_legacy_file("07_legacy_tank_demo.mo", _REAL_LEGACY_TANK_MO)

    assert model.filename == "07_legacy_tank_demo.mo"
    assert len(model.classes) == 1
    tank_class = model.classes[0]
    assert tank_class.kind == "model"
    assert tank_class.name == "TankDemo_Rev12"

    params_by_name = {p.name: p for p in tank_class.parameters}
    assert params_by_name["A1"].value == "1.20"
    assert params_by_name["A1"].unit == "m2"
    assert params_by_name["qFill"].unit == "m3/s"
    assert params_by_name["wait1"].value == "10"

    variables_by_name = {v.name: v for v in tank_class.variables}
    assert variables_by_name["valve1"].type == "Boolean"

    # A variable's custom enum type (not just Real/Boolean/Integer/String)
    # and the enum declaration itself must both be captured -- found live
    # on a real dataset (see DECISIONS.md): the algorithm section
    # references "seq" and "StepState", and skipping either would produce
    # a legacy-reuse class the real compiler rejects as referencing an
    # undeclared variable.
    assert variables_by_name["seq"].type == "StepState"
    assert any("enumeration(IDLE,FILL,HOLD1,TRANSFER,HOLD2,DRAIN,HOLD3)" in decl for decl in tank_class.type_declarations)

    # `discrete` and `start=...` must both survive parsing -- found live
    # on a real dataset (see DECISIONS.md D50): "seq" is a genuinely free
    # discrete variable (never reassigned anywhere in the source; it's
    # meant to be driven by a sequencer this fragment doesn't include),
    # and dropping either its `discrete` qualifier or its `start=` value
    # on reuse left the reused class with no way to determine it at all.
    assert variables_by_name["seq"].is_discrete is True
    assert variables_by_name["seq"].start_value == "StepState.IDLE"
    assert variables_by_name["valve1"].is_discrete is False
    assert variables_by_name["valve1"].start_value is None

    # Equation-section and algorithm-section content must stay separate --
    # Modelica requires `:=` assignments in `algorithm`, never `equation`
    # (found live on a real dataset: merging them produced a real compiler
    # error, "Equations can not contain assignments"; see DECISIONS.md).
    assert any("der(tank1Level)" in eq for eq in tank_class.equations)
    assert not any(":=" in eq for eq in tank_class.equations)
    assert any(":=" in stmt for stmt in tank_class.algorithm_statements)
    assert not any("der(" in stmt for stmt in tank_class.algorithm_statements)


def test_legacy_analyzer_parses_connect_calls() -> None:
    text = (
        "model Circuit\n"
        "equation\n"
        "  connect(sensor.y, controller.u);\n"
        "end Circuit;\n"
    )
    model = analyze_legacy_file("circuit.mo", text)
    assert model.classes[0].connects == [("sensor.y", "controller.u")]


def test_sysml_analyzer_parses_architecture_and_requirements() -> None:
    files = {
        "Architecture.sysml": (
            "package Architecture {\n"
            "    part def TankDemo;\n"
            "    part def Valve01;\n"
            "    part tankDemo : TankDemo;\n"
            "    part valve01 : Valve01;\n"
            "    connect tankDemo to valve01;  // CONNECTED_TO\n"
            "}\n"
        ),
        "Requirements.sysml": (
            "package Requirements {\n"
            "    requirement def TankDemoRequirement {\n"
            "        doc /* TankDemo.h1High <= 0.78 m */\n"
            "        attribute h1High : Real;\n"
            "    }\n"
            "}\n"
        ),
        "Behaviors.sysml": (
            "package Behaviors {\n"
            "    action def FillControl;\n"
            "    // level <= 0.78 m -> STOP fill\n"
            "}\n"
        ),
    }

    model = analyze_sysml_files(files)

    assert {p.instance_name: p.part_def for p in model.parts} == {"tankDemo": "TankDemo", "valve01": "Valve01"}
    assert len(model.connections) == 1
    assert model.connections[0].source_instance == "tankDemo"
    assert model.connections[0].target_instance == "valve01"
    assert model.connections[0].relationship_type == "CONNECTED_TO"

    assert len(model.requirements) == 1
    assert model.requirements[0].name == "TankDemoRequirement"
    assert model.requirements[0].property == "h1High"
    assert model.requirements[0].doc == "TankDemo.h1High <= 0.78 m"

    assert len(model.behaviors) == 1
    assert model.behaviors[0].name == "FillControl"
    assert model.behaviors[0].comment == "level <= 0.78 m -> STOP fill"
