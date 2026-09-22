"""Verified Modelica Standard Library catalog for the first two target systems.

The catalog is deliberately small and problem-shaped. It gives Stage 3 real,
installed class names and tells it which representation preserves the stated
physics. This prevents plausible-looking invented library paths and produces
component diagrams that are useful in OMEdit.

The names below were checked against the Modelica 4.1.0 library bundled with
OpenModelica 1.27.1. The problem's numeric parameters still come exclusively
from the merged engineering brief.
"""

from __future__ import annotations


MODELICA_LIBRARY_CATALOG: dict[str, str] = {
    "fluid_level_and_flow": """\
TWO-TANK FILL / TRANSFER / DRAIN CATALOG (Modelica Standard Library 4.1.0)

The supplied tank problem specifies ideal, fixed volumetric flow whenever an
on/off valve is commanded open. It does not provide pressures, pipe geometry,
valve Cv, pump curves, or fluid-property data. Preserve that stated fidelity
with a signal-flow volume balance. Do not replace the fixed flows with an
invented pressure-driven Modelica.Fluid network.

Required/recommended MSL classes:
- Modelica.Blocks.Interfaces.RealInput / RealOutput: flow and level connectors
  on each tank component.
- Modelica.Blocks.Interfaces.BooleanInput / BooleanOutput: valve commands and
  operator/controller signals.
- Modelica.Blocks.Math.Add: net flow Q_in - Q_out.
- Modelica.Blocks.Math.Gain: convert net volumetric flow to level rate with
  gain 1/A.
- Modelica.Blocks.Continuous.Integrator: integrate level rate, initialized from
  the brief. A custom equation may enforce the stated low-level cutoff where a
  plain Integrator cannot.
- Modelica.Blocks.Math.BooleanToReal: convert each Boolean valve command to
  0/1 and scale it by the brief's nominal flow.
- Modelica.Blocks.Sources.BooleanTable: only when it directly represents the
  brief's operator command schedule; otherwise implement one-shot schedule
  events in the scenario/controller.
- Modelica.StateGraph.InitialStep, Modelica.StateGraph.Step,
  Modelica.StateGraph.Transition, and Modelica.StateGraph.TransitionWithSignal:
  optional graphical sequence components. Use them only when the complete
  pause/resume/timer behavior can be expressed correctly; a custom controller
  model with an enumeration is safer for the current freeze/resume semantics.
- Modelica.Icons.Example, Modelica.Blocks.Icons.Block, and
  Modelica.Blocks.Icons.PartialBooleanBlock: standard visual bases.

Available only if later evidence supplies the missing hydraulic data:
- Modelica.Fluid.System
- Modelica.Fluid.Vessels.OpenTank
- Modelica.Fluid.Sources.Boundary_pT
- Modelica.Fluid.Sources.MassFlowSource_T
- Modelica.Fluid.Valves.ValveDiscrete
- Modelica.Fluid.Pipes.StaticPipe
Do not instantiate those pressure/medium-based components for this fixed-flow
benchmark merely for appearance. The current signal-flow model is the faithful
MSL-based representation.

Expected file split for this problem:
1. Tank1.mo -- TK-101 component with its own parameters, level state, connectors,
   Icon annotation, and Diagram annotation.
2. Tank2.mo -- TK-102 component, separately inspectable in OMEdit.
3. OnOffValve.mo -- reusable Boolean-to-nominal-flow component.
4. TankSequenceController.mo -- the concise fill/wait/transfer/wait/drain/wait
   state machine, including pause/resume and shutdown.
5. TwoTankSystem.mo -- top-level connected experiment and command schedule,
   loaded last and named as entry_class.
""",

    "magnetic_circuit": """\
QUASI-STATIC MAGNETIC CIRCUIT CATALOG (Modelica Standard Library 4.1.0)

The magnetic benchmark is a linear reluctance network: four series core
sections followed by parallel useful-gap and leakage branches, driven by a
specified MMF schedule. Represent that topology directly with FluxTubes so it
is visible and navigable in OMEdit.

The connection order is strict: source -> CORE_L -> CORE_U -> CORE_R -> split;
from the split, GAP_1 and LEAK_1 are the ONLY two parallel paths; they rejoin ->
CORE_D -> source return. CORE_R must be before the split and must never be wired
between the same branch nodes as GAP_1/LEAK_1, which would create an unintended
third parallel path and violate Phi_core = Phi_gap + Phi_leak.

Required/recommended MSL classes:
- Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance: each released linear
  core section, the useful air gap, and the equivalent leakage reluctance.
- Modelica.Magnetic.FluxTubes.Sources.SignalMagneticPotentialDifference:
  imposed magnetomotive force N*I from the stated excitation schedule.
- Modelica.Magnetic.FluxTubes.Basic.Ground: magnetic reference potential.
- Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor: core, useful-gap,
  and leakage branch flux measurements.
- Modelica.Magnetic.FluxTubes.Sensors.MagneticPotentialDifferenceSensor:
  optional check of core/gap MMF drops.
- Modelica.Blocks.Sources.TimeTable or Modelica.Blocks.Sources.CombiTimeTable:
  the stated hold/ramp/hold current schedule.
- Modelica.Blocks.Math.Gain: N*I excitation and derived signed measurement
  scaling where a direct library sensor does not expose the requested value.
- Modelica.Constants.pi and Modelica.Constants.mu_0: standard constants; do
  not duplicate approximate values when the library constant is applicable.
- Modelica.Icons.Example and Modelica.Icons.UnderConstruction: use Example for
  the finished top-level experiment; never use UnderConstruction in output.

Do not use nonlinear shape/material FluxTubes components unless the brief gives
a B-H curve or geometry sufficient for them. The released benchmark explicitly
uses constant reluctances, so ConstantReluctance is the correct built-in class.

Expected file split for this problem:
1. CorePath.mo -- reusable/assembled four-section series core path.
2. AirGapBranch.mo -- useful air-gap reluctance and sensors.
3. LeakageBranch.mo -- equivalent leakage reluctance and sensors.
4. Excitation.mo -- current/MMF schedule using MSL source and math blocks.
5. MagneticCircuitSystem.mo -- connected top-level experiment, loaded last and
   named as entry_class.
""",
}


def modelica_catalog_block(domains: list[str]) -> str:
    """Return catalogs relevant to the domains selected during Merge."""

    matched = [MODELICA_LIBRARY_CATALOG[d] for d in domains if d in MODELICA_LIBRARY_CATALOG]
    if not matched:
        return ""
    return (
        "\n\nVERIFIED MODELICA STANDARD LIBRARY CATALOG FOR THIS PROBLEM\n\n"
        + "\n\n".join(matched)
        + "\n\nUse only relevant entries. Record every fully-qualified MSL class actually "
        "instantiated in library_components."
    )
