"""Verified Modelica Standard Library catalogs, one per engineering domain.

Each entry names real, installed MSL classes for that KIND of system and says
which representation preserves the stated physics. That stops Stage 3 inventing
plausible-looking library paths and produces component diagrams that are useful
in OMEdit.

Deliberately domain knowledge, never problem knowledge -- no entity name, id,
tag, topology or numeric value from any specific dataset appears here, exactly
as `skills/domains.py` already requires of itself and for the same confirmed
reason: a concrete example name sitting in a shared prompt leaks verbatim into
an unrelated problem's output when the model lacks real signal. An earlier
version of this file described one specific two-tank benchmark -- its vessel
tags, its valve tags, its exact file split and its filenames -- under the
`fluid_level_and_flow` key. Every project Merge classifies into that domain
receives this text, and a second dataset in `projects/` (an evaporation
process) already selects the same key, so that problem was being handed
another problem's component tags and told which files to produce. The problem's
own entities, structure and numbers come exclusively from the merged
engineering brief.

Class names were checked against the Modelica 4.1.0 library bundled with
OpenModelica 1.27.1.
"""

from __future__ import annotations


_SIGNAL_FLOW_NOTE = """\
BUILD FROM LIBRARY COMPONENTS FIRST. For each physical element the brief names,
use the Modelica Standard Library class that represents it and instantiate that
class directly in the system model. A library component brings its own icon,
its own connectors and its own diagram graphics, so the component diagram is
meaningful in OMEdit without drawing anything by hand -- a library vessel
already renders as a tank with a live level, a library valve as a valve symbol,
a library boundary as a source node. Hand-written replacements for classes the
library already provides are the main reason a generated diagram comes out as a
row of blank rectangles.

Write a CUSTOM class only where no library class expresses the behaviour. In a
sequenced process that is normally just the sequence controller; the vessels,
valves, boundaries, operator command sources and measurement readouts all exist
in the library. Give that one custom class a real icon and placed connectors.

Preferring the acausal physical library also removes a whole failure class: its
flows are solved from the physics, so there is no hand-built signal chain to
accidentally close into an algebraic loop.

When a library class needs a parameter the brief does not state (a medium, a
nominal pressure drop, a port diameter), choose it so the component reproduces
the behaviour the brief DOES state, and record that choice in `corrections` as
an explicit assumption. That is different from inventing a requirement: the
brief's own stated rates, levels, thresholds and timings still govern, and must
be reproduced by the result.

Every file must contain exactly one top-level class whose name matches its
filename, named after the entity the BRIEF names -- never after an example.
Put the connected experiment in the single `role="system"` file, loaded last.
"""


MODELICA_LIBRARY_CATALOG: dict[str, str] = {
    "fluid_level_and_flow": """\
FLUID LEVEL AND FLOW (vessels, valves, pipes, pumps)

PREFERRED -- the acausal Fluid components, which carry their own icons and
render as a readable process diagram:
- Modelica.Fluid.System: the required global fluid settings; exactly one
  `inner Modelica.Fluid.System system;` in the top-level model.
- Modelica.Fluid.Vessels.OpenTank: a vented vessel. Set `crossArea`, `height`
  and `level_start` from the brief, and give it one `portsData` entry per
  connection with that port's `height` (an inlet at the top, an outlet at the
  bottom). It draws as a tank with a live level.
- Modelica.Fluid.Valves.ValveDiscrete: a commanded on/off valve with a Boolean
  `open` input. Size `m_flow_nominal` and `dp_nominal` so the flow while open
  matches the rate the brief states, and record that sizing as an assumption.
- Modelica.Fluid.Sources.Boundary_pT: a supply source or receiving drain.
- Modelica.Media.Water.ConstantPropertyLiquidWater: a simple constant-property
  liquid, declared once as `package Medium = ...` and redeclared into each
  fluid component, when the brief does not name a specific fluid.
- Modelica.Blocks.Sources.RadioButtonSource: momentary operator pushbuttons
  from a time table, with mutual reset between them -- the correct component
  for START/STOP/SHUT style commands issued at listed times, and the preferred
  choice over hand-building command pulses. Each button takes
  `buttonTimeTable={t1, t2, ...}` and is released when any of the others is
  pressed, so one genuine press is produced per listed time and the commands
  stay mutually exclusive:
  `RadioButtonSource PB_START(buttonTimeTable={20,280}, reset={PB_STOP.on, PB_SHUT.on});`
  Note `reset` takes a Boolean array, so it must list each other button's `.on`
  OUTPUT -- passing the component instances themselves (`reset={PB_STOP,
  PB_SHUT}`) is a type mismatch. The same distinction applies in `connect()`:
  connect `PB_START.on`, never `PB_START`.
- Modelica.Blocks.Sources.RealExpression / BooleanExpression: expose an
  internal value (a vessel's `level`, say) as a signal into the controller
  without adding a sensor component.
- Modelica.StateGraph.InitialStep / Step / Transition / TransitionWithSignal
  and Modelica.StateGraph.StateGraphRoot: a graphical sequence, when the full
  timing and pause/resume behaviour can be expressed with them.

Signal-flow alternative -- use ONLY when the brief's physics genuinely is a
commanded rate rather than a pressure-driven flow, and say so in `corrections`:
- Modelica.Blocks.Interfaces.RealInput / RealOutput: flow and level signals
  between components.
- Modelica.Blocks.Interfaces.BooleanInput / BooleanOutput: on/off valve commands
  and operator/controller signals.
- Modelica.Blocks.Math.Add / Add3 / Sum: a net flow such as Q_in - Q_out.
- Modelica.Blocks.Math.Gain: convert a net volumetric flow to a level rate with
  gain 1/A, or scale a normalized command to a nominal flow.
- Modelica.Blocks.Math.BooleanToReal: convert a Boolean valve command to 0/1.
- Modelica.Blocks.Continuous.Integrator: integrate a rate into an accumulated
  quantity, initialized from the brief. A custom equation may enforce a stated
  physical bound where a plain Integrator cannot.
- Modelica.Blocks.Sources.BooleanTable / TimeTable / CombiTimeTable: a stated
  command or setpoint schedule, when the schedule is genuinely tabular.
- Modelica.Blocks.Nonlinear.Limiter: a saturation the brief actually states.
- Modelica.StateGraph.InitialStep / Step / Transition / TransitionWithSignal:
  optional graphical sequencing. Use them only when the complete timing and
  pause/resume behavior can be expressed correctly; a custom controller model
  with an enumeration is usually safer for freeze/resume semantics.
- Modelica.Icons.Example, Modelica.Blocks.Icons.Block: standard visual bases.

Also available for a richer hydraulic network when the brief supports it:
Modelica.Fluid.Sources.MassFlowSource_T, Modelica.Fluid.Pipes.StaticPipe,
Modelica.Fluid.Machines.PrescribedPump, Modelica.Fluid.Sensors.*.

In the signal-flow form a vessel's level follows from its own volume balance,
`der(level) = (inflow - outflow)/area`, or equivalently from the chain
BooleanToReal -> Gain(nominal flow) -> Add -> Gain(1/area) -> Integrator. Use
one or the other for a given state, never both. In that form the chain must run
strictly downstream: an on/off valve produces its own nominal flow from its
command alone, and the vessel upstream limits that flow to its own inventory
inside its own equations. Never feed a vessel's resulting outflow back into the
valve that sets it -- that closes an algebraic loop which the solver satisfies
with every flow at zero, and the run still reports success.
""",

    "magnetic_circuit": """\
MAGNETIC CIRCUITS (cores, air gaps, windings, flux paths)

Required/recommended MSL classes:
- Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance: a linear core section,
  air gap or equivalent leakage path.
- Modelica.Magnetic.FluxTubes.Sources.SignalMagneticPotentialDifference or
  ConstantMagneticPotentialDifference: an imposed magnetomotive force.
- Modelica.Magnetic.FluxTubes.Basic.Ground: magnetic reference potential; the
  network needs exactly one.
- Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor and
  MagneticPotentialDifferenceSensor: branch flux and MMF-drop measurements.
- Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort and
  NegativeMagneticPort: the magnetic connectors a CUSTOM component declares to
  expose its own terminals -- for example a series path that must expose the
  two nodes where a parallel branch attaches. A custom component in this domain
  carries magnetic ports, not Real signals.
- Modelica.Blocks.Sources.TimeTable / CombiTimeTable / Ramp / Step: a stated
  excitation schedule.
- Modelica.Blocks.Math.Gain: an N*I excitation or a derived signed measurement.
- Modelica.Constants.pi and Modelica.Constants.mu_0: use the library constants
  rather than duplicating approximate values.
- Modelica.Icons.Example: the finished top-level experiment. Never use
  Modelica.Icons.UnderConstruction in output.

Use nonlinear shape/material FluxTubes classes only when the brief supplies a
B-H curve or the geometry those classes require; otherwise ConstantReluctance
is the faithful choice.

`ConstantReluctance` takes parameter `R_m` and magnetic `port_p`/`port_n`; the
signal source takes input `V_m` and the same magnetic ports. Build the series
and parallel structure the BRIEF states, and check that the flux split it
implies actually holds (the flux into a junction equals the sum out of it).
A sensor is connected by its magnetic ports into the path it measures; its
scalar output is not itself a magnetic port.
""",

    "thermal": """\
THERMAL / HEAT TRANSFER (thermal masses, heaters, heat exchange)

Required/recommended MSL classes:
- Modelica.Thermal.HeatTransfer.Components.HeatCapacitor: a lumped thermal mass
  (parameter C = m*cp), with `T(start=..., fixed=true)` from the brief.
- Modelica.Thermal.HeatTransfer.Components.ThermalConductor / ThermalResistor:
  conduction or a lumped loss path.
- Modelica.Thermal.HeatTransfer.Components.Convection: a convective path driven
  by a conductance signal.
- Modelica.Thermal.HeatTransfer.Sources.FixedTemperature /
  PrescribedTemperature: an ambient or a scheduled boundary temperature.
- Modelica.Thermal.HeatTransfer.Sources.FixedHeatFlow / PrescribedHeatFlow:
  a rated or commanded heat input.
- Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor / HeatFlowSensor.
- Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a / HeatPort_b: the thermal
  connectors on a custom component.
- Modelica.Blocks.Sources.* and Modelica.Blocks.Math.* for schedules and signal
  arithmetic.

The acausal HeatTransfer network is appropriate whenever the brief gives real
thermal capacities and conductances/resistances. When it instead gives a bare
energy balance, write it directly as `C*der(T) = Q_in - Q_out` and keep one
formulation per state.
""",

    "electrical_circuit": """\
ELECTRICAL CIRCUITS (resistive/inductive/capacitive networks)

Required/recommended MSL classes:
- Modelica.Electrical.Analog.Basic.Resistor / Capacitor / Inductor / Ground.
- Modelica.Electrical.Analog.Sources.ConstantVoltage / SignalVoltage /
  ConstantCurrent / SignalCurrent.
- Modelica.Electrical.Analog.Ideal.IdealClosingSwitch / IdealOpeningSwitch:
  a commanded switch.
- Modelica.Electrical.Analog.Sensors.VoltageSensor / CurrentSensor /
  PowerSensor.
- Modelica.Electrical.Analog.Interfaces.PositivePin / NegativePin: the
  electrical connectors on a custom component.
- Modelica.Blocks.Sources.* for a stated excitation schedule.

The network needs exactly one Ground. Give every capacitor voltage and inductor
current a real initial condition from the brief.
""",

    "mechanical_dynamics": """\
MECHANICAL DYNAMICS (masses, springs, dampers, rotating/translating bodies)

Required/recommended MSL classes:
- Modelica.Mechanics.Translational.Components.Mass / Spring / Damper /
  SpringDamper / Fixed.
- Modelica.Mechanics.Translational.Sources.Force / Position / Speed.
- Modelica.Mechanics.Translational.Sensors.PositionSensor / SpeedSensor /
  ForceSensor.
- Modelica.Mechanics.Rotational.Components.Inertia / Spring / Damper /
  IdealGear / Fixed, with Rotational.Sources.Torque and the matching sensors,
  for rotating systems.
- Modelica.Mechanics.*.Interfaces.Flange_a / Flange_b: the mechanical
  connectors on a custom component.

Give position and velocity (or angle and angular velocity) independent, real
initial conditions from the brief rather than deriving one from the other.
""",

    "species_concentration_balance": """\
WELL-MIXED SPECIES / CONCENTRATION BALANCE

Required/recommended MSL classes:
- Modelica.Blocks.Continuous.Integrator: accumulate the species inventory,
  initialized from the brief.
- Modelica.Blocks.Math.Add / Add3 / Sum / Product / Division / Gain: assemble
  the generation, inflow and outflow terms of the balance.
- Modelica.Blocks.Sources.CombiTimeTable / TimeTable / Pulse: a stated
  occupancy, generation or ventilation schedule.
- Modelica.Blocks.Continuous.LimPID or Modelica.Blocks.Continuous.PI: a stated
  feedback controller. Use one only when the brief describes feedback control,
  with its stated gains; never invent tuning.
- Modelica.Blocks.Nonlinear.Limiter: a stated actuator saturation.
- Modelica.Blocks.Interfaces.RealInput / RealOutput and Modelica.Icons.Example.

Write the balance on the well-mixed volume itself, `V*der(C) = generation +
flowIn*C_in - flowOut*C`, with the outlet concentration equal to the bulk
concentration C. Keep the unit basis the brief actually uses consistent across
every term.
""",

    "multiphase_mixture_process": """\
MULTI-COMPONENT MIXTURES WITH COMPOSITION-DEPENDENT PROPERTIES

Required/recommended MSL classes:
- Modelica.Blocks.Continuous.Integrator: one per conserved inventory the brief
  tracks (total mass, energy, and each independent species mass).
- Modelica.Blocks.Math.Product / Division / Add / Gain: assemble composition,
  property and phase-change terms from the brief's own correlations.
- Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow and
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor: a stated heat input
  and thermal inertia.
- Modelica.Blocks.Sources.CombiTimeTable / TimeTable: a stated duty or feed
  schedule.
- Modelica.Blocks.Nonlinear.Limiter and Modelica.Blocks.Logical.Hysteresis: a
  stated bound, and hysteresis around a boundary the brief approves.
- Modelica.Constants.* for genuine physical constants.
- Modelica.Icons.Example for the top-level experiment.

Do not reach for Modelica.Media or Modelica.Fluid unless the brief supplies a
real medium model's required data. Carry mass, energy and composition as the
states and derive level, density and temperature-dependent properties from the
brief's own correlations; a missing correlation coefficient is a gap to report,
never one to fill in.
""",

    "batch_sequential_process": """\
BATCH / SEQUENTIAL PROCESS CONTROL (staged operations with guarded transitions)

Required/recommended MSL classes:
- Modelica.Blocks.Interfaces.BooleanInput / BooleanOutput / RealInput /
  RealOutput: command, status and measurement connectors on the controller.
- Modelica.Blocks.Sources.BooleanTable: an operator/command schedule with
  several entries, when a table genuinely represents it.
- Modelica.Blocks.Sources.CombiTimeTable: a multi-column schedule of setpoints
  or commands over time.
- Modelica.Blocks.Math.BooleanToReal / RealToBoolean: reporting and thresholding.
- Modelica.Blocks.Logical.* (And, Or, Not, Greater, Less, Hysteresis, Timer):
  interlocks and guards built from library blocks when that is clearer.
- Modelica.StateGraph.InitialStep / Step / Transition / TransitionWithSignal:
  optional graphical sequencing; a custom controller model with an enumeration
  mode is usually safer when freeze/resume or priority-override semantics apply.
- Modelica.Icons.Example and Modelica.Blocks.Icons.Block.

Express each named stage as one value of a single enumeration mode, and each
transition guard as exactly the completion condition the brief states. A
higher-priority mode (an emergency, shutdown or override stage) is tested
FIRST in the dispatcher's if/elseif chain, before the normal stage-to-stage
transitions, so it can interrupt any stage.
""",
}


def modelica_catalog_block(domains: list[str]) -> str:
    """Return catalogs relevant to the domains selected during Merge."""

    matched = [MODELICA_LIBRARY_CATALOG[d] for d in domains if d in MODELICA_LIBRARY_CATALOG]
    if not matched:
        return ""
    return (
        "\n\nVERIFIED MODELICA STANDARD LIBRARY CATALOG FOR THIS SYSTEM'S DOMAIN(S) "
        "(general domain knowledge -- the brief's own entities, structure and values "
        "always take precedence over anything below):\n\n"
        + _SIGNAL_FLOW_NOTE
        + "\n\n"
        + "\n\n".join(matched)
        + "\n\nUse only relevant entries. Record every fully-qualified MSL class actually "
        "instantiated in library_components."
    )
