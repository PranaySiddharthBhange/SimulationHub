"""Tests against the real, locally installed OpenModelica `omc` compiler.

Skipped automatically when no local install is found -- see
`compiler/openmodelica_client.py` and `DECISIONS.md` D21 for why this
can't be a hard dependency of the package. Run these after `winget install
OpenModelica.OpenModelica.Official` to actually exercise the real
compiler; CI/deterministic runs skip them.
"""

from __future__ import annotations

import pytest

from simulation_platform.compiler import CompilerUnavailable, compile_files, find_omc_executable
from simulation_platform.modelica_gen.generation import generate_modelica_files
from simulation_platform.schemas import (
    LegacyClass,
    LegacyComparison,
    LegacyModel,
    LegacyRecommendation,
    LegacyVariable,
    ModelicaMapping,
    ModelicaMappingType,
    SysMLSemanticModel,
)

try:
    find_omc_executable()
    _OMC_AVAILABLE = True
except CompilerUnavailable:
    _OMC_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _OMC_AVAILABLE, reason="No local OpenModelica install found.")


def test_omc_compiles_a_valid_model() -> None:
    files = {
        "TankSystem.mo": "model TankSystem\n  parameter Real h1High(unit=\"m\") = 0.78;\nend TankSystem;\n"
    }
    result = compile_files("exec_test_valid", files, entry_class="TankSystem", timeout=90.0)

    assert result.status.value == "PASSED"
    assert result.errors == []
    assert result.backend == "openmodelica"
    assert result.backend_version != "unknown"


def test_omc_flags_a_broken_model_with_correct_file_and_line() -> None:
    files = {
        "Broken.mo": "model Broken\n  parameter Real x\nequation\nend Broken;\n"
    }
    result = compile_files("exec_test_broken", files, entry_class="Broken", timeout=90.0)

    assert result.status.value == "FAILED"
    assert result.errors != []
    assert all(error.file == "Broken.mo" for error in result.errors)
    assert all(error.line is not None for error in result.errors)


def test_omc_runs_a_real_simulate_and_catches_an_under_determined_system() -> None:
    """A model that passes `checkModel()`-style structural checks (no
    syntax error, every parameter has a value) but is genuinely
    under-determined at the equation level -- found live on a real
    dataset (see DECISIONS.md D42-D54) as exactly the class of gap this
    agent's own compile check needs to catch itself, not rely on a human
    re-running the model in OMEdit. Two unknowns (`x`, `y`), one
    equation -- `checkModel()` alone would not reliably catch this the
    way a real `simulate()` attempt does."""

    files = {
        "Underdetermined.mo": (
            "model Underdetermined\n"
            "  Real x;\n"
            "  Real y;\n"
            "equation\n"
            "  x + y = 1;\n"
            "end Underdetermined;\n"
        )
    }
    result = compile_files("exec_test_underdetermined", files, entry_class="Underdetermined", timeout=90.0)

    assert result.status.value == "FAILED"
    assert result.errors != []
    assert any("under-determined" in e.message.lower() for e in result.errors)
    assert any(e.category.value == "UNDERDETERMINED_SYSTEM" for e in result.errors)


def test_a_synthesized_state_machine_actually_drives_a_real_simulated_transition() -> None:
    """End-to-end proof for the state-machine synthesis feature (see
    `modelica_gen/generation/modelica_generator.py`'s `_render_state_
    machine`): not just that the generated `.mo` text looks right, but
    that the REAL OpenModelica solver accepts it and the sequencer
    variable genuinely changes state over simulated time -- catching
    exactly the two real defects found live while building this (an
    over-determined system from separate `when` clauses, and a discrete
    algebraic loop from guards that didn't read `pre(...)`), neither of
    which a text-only assertion could have caught."""

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
    sysml_contract_raw = {
        "requirements": [{"id": "REQ-010", "subject": "S", "property": "wait", "operator": "==", "value": 2.0}],
        "behaviors": [
            {
                "id": "BEH-001", "trigger_property": "Tank 1 level", "trigger_operator": ">=",
                "trigger_value": 0.5, "action_type": "transition", "action_target": "seq",
            },
        ],
    }
    state_machines = [
        {
            "state_machine_id": "SM-001", "target_type_hint": "StepState",
            "states": ["IDLE", "FILL", "DONE"], "initial_state": "IDLE",
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

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "seq_001", mappings, legacy_comparisons, legacy_models, SysMLSemanticModel(), sysml_contract_raw,
        state_machines=state_machines,
    )
    result = compile_files(
        "exec_test_state_machine", files, entry_class=entry_class, timeout=90.0,
        start_time=0, stop_time=15, number_of_intervals=150,
    )

    assert result.status.value == "PASSED"
    assert result.errors == []
    seq_summary = result.result_summary["sequencer1.seq"]
    # StepState.IDLE=1, FILL=2, DONE=3 -- the whole point of this feature is
    # that `seq` no longer sits frozen at its `start=` value for the entire
    # run (the exact bug this feature exists to fix, see DECISIONS.md D50).
    assert seq_summary["min"] == 1.0
    assert seq_summary["final"] == 3.0


def test_a_behavior_targeting_a_from_scratch_stub_actually_compiles() -> None:
    """End-to-end proof for the from-scratch-stub field-declaration fix
    (`generation/modelica_generator.py`'s `_render_stub_class`): before
    this fix, a from-scratch MODEL with no legacy match declared NOTHING
    at all, so a real behavior's `trigger_variable`/`action_variable`
    pointing at one of its fields produced a genuine, guaranteed
    "field not found" error from the real compiler -- not something a
    text-only assertion on the generated `.mo` could have caught."""

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

    files, entry_class, _class_names, _declared = generate_modelica_files(
        "nacl_001", mappings, [], [], SysMLSemanticModel(), sysml_contract_raw,
    )
    result = compile_files("exec_test_stub_field", files, entry_class=entry_class, timeout=90.0)

    assert result.status.value == "PASSED"
    assert result.errors == []
