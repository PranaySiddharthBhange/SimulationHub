"""Static, curated Modelica Standard Library (MSL) catalog. Mirrors
`Modelica Agent.md`, Section 13: "Don't let the LLM invent library class
names blindly."

Every class name below is a real MSL 4.x class -- this is a small, honest
subset covering the domains the four golden datasets actually use (signal,
fluid, thermal, electrical, mechanical, magnetic), not an attempt at a
complete MSL index. `libraries/library_resolver.py` only ever returns
candidates from this fixed list; nothing here is LLM-generated. Every
Magnetic/Electrical class name and connector shape below was verified
against the real, locally installed MSL 4.1.0 via `omc` introspection
(`getClassNames`/`list`) plus a real compile+simulate run of a minimal
circuit combining them, not assumed from training knowledge -- see
`generation/modelica_generator.py`'s placeholder-parameter dict for which
of these have no default value at all.
"""

from __future__ import annotations

from pydantic import BaseModel

CONNECTOR_KINDS = ("SIGNAL", "FLUID", "THERMAL", "ELECTRICAL", "MECHANICAL", "MAGNETIC")


class LibraryCandidate(BaseModel):
    modelica_class: str
    connector_kind: str  # one of CONNECTOR_KINDS
    description: str


# Connector types per domain -- used by connection/interface mapping.
CONNECTOR_CATALOG: dict[str, list[LibraryCandidate]] = {
    "SIGNAL": [
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Interfaces.RealInput", connector_kind="SIGNAL",
            description="Scalar real-valued input signal.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Interfaces.RealOutput", connector_kind="SIGNAL",
            description="Scalar real-valued output signal.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Interfaces.BooleanInput", connector_kind="SIGNAL",
            description="Scalar boolean input signal.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Interfaces.BooleanOutput", connector_kind="SIGNAL",
            description="Scalar boolean output signal.",
        ),
    ],
    "FLUID": [
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Interfaces.FluidPort_a", connector_kind="FLUID",
            description="Fluid connector, port a (flow-in convention).",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Interfaces.FluidPort_b", connector_kind="FLUID",
            description="Fluid connector, port b (flow-out convention).",
        ),
    ],
    "THERMAL": [
        LibraryCandidate(
            modelica_class="Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a", connector_kind="THERMAL",
            description="Thermal connector, port a.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_b", connector_kind="THERMAL",
            description="Thermal connector, port b.",
        ),
    ],
    "ELECTRICAL": [
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Interfaces.PositivePin", connector_kind="ELECTRICAL",
            description="Electrical connector, positive pin.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Interfaces.NegativePin", connector_kind="ELECTRICAL",
            description="Electrical connector, negative pin.",
        ),
    ],
    "MECHANICAL": [
        LibraryCandidate(
            modelica_class="Modelica.Mechanics.Translational.Interfaces.Flange_a", connector_kind="MECHANICAL",
            description="Translational mechanical flange, side a.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Mechanics.Translational.Interfaces.Flange_b", connector_kind="MECHANICAL",
            description="Translational mechanical flange, side b.",
        ),
    ],
    # Added for the Magnetic Circuit domain (Level 3) -- before this, an
    # interface with kind="MAGNETIC" silently fell back to a bare SIGNAL
    # connector pair (`connector_mapper.py`'s own default), which would
    # have wired a magnetic port as if it were a plain real-valued signal.
    "MAGNETIC": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort", connector_kind="MAGNETIC",
            description="Magnetic connector, positive port.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Interfaces.NegativeMagneticPort", connector_kind="MAGNETIC",
            description="Magnetic connector, negative port.",
        ),
    ],
}

# Component keyword -> candidate library components. Keys are matched as a
# case-insensitive substring against a SysML part's def name or type.
COMPONENT_KEYWORD_CATALOG: dict[str, list[LibraryCandidate]] = {
    "sensor": [
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Interfaces.RealOutput", connector_kind="SIGNAL",
            description="Sensor represented as a scalar signal source (its measured value).",
        ),
    ],
    "controller": [
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Continuous.LimPID", connector_kind="SIGNAL",
            description="Continuous PID control loop with output limiting.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Blocks.Logical.OnOffController", connector_kind="SIGNAL",
            description="Hysteresis-based on/off controller.",
        ),
    ],
    "valve": [
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Valves.ValveIncompressible", connector_kind="FLUID",
            description="Flow-restricting valve for an incompressible medium.",
        ),
    ],
    "damper": [
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Valves.ValveIncompressible", connector_kind="FLUID",
            description="Air damper modeled as a flow-restricting valve (no dedicated MSL damper class).",
        ),
    ],
    "pump": [
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Machines.PrescribedPump", connector_kind="FLUID",
            description="Pump with a prescribed head/flow characteristic.",
        ),
    ],
    "tank": [
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Vessels.OpenTank", connector_kind="FLUID",
            description="Open tank with a free liquid surface.",
        ),
    ],
    "heat": [
        LibraryCandidate(
            modelica_class="Modelica.Thermal.HeatTransfer.Components.ThermalConductor", connector_kind="THERMAL",
            description="Lumped thermal conductor between two heat ports.",
        ),
    ],
    # CO2 ventilation (Level 2) -- an actively driven air mover, distinct
    # from "damper" above (a passive flow restriction). Reuses the same
    # real MSL pump class already verified for Tank -- a fan is a pump for
    # a gas medium, no dedicated MSL "fan" class exists.
    "fan": [
        LibraryCandidate(
            modelica_class="Modelica.Fluid.Machines.PrescribedPump", connector_kind="FLUID",
            description="Actively driven air mover (fan), modeled as a prescribed-speed pump.",
        ),
    ],
    # Magnetic Circuit (Level 3) -- every entry below verified against the
    # real, locally installed MSL 4.1.0 (class names, connector shapes, and
    # which parameters have no default at all all checked live via `omc`
    # introspection and a real compile+simulate run, not assumed from
    # memory -- same discipline as the Fluid entries above).
    "coil": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.ElectroMagneticConverter", connector_kind="MAGNETIC",
            description="Ideal electrical<->magnetic coupling (Ampere's law + Faraday's law) -- the coil/winding.",
        ),
    ],
    "winding": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.ElectroMagneticConverter", connector_kind="MAGNETIC",
            description="Ideal electrical<->magnetic coupling (Ampere's law + Faraday's law) -- the coil/winding.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Basic.Resistor", connector_kind="ELECTRICAL",
            description="The winding's own electrical resistance -- a real, explicit I^2*R loss path.",
        ),
    ],
    "core": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance", connector_kind="MAGNETIC",
            description="Magnetic core reluctance (constant, parameterized -- not derived from geometry).",
        ),
    ],
    "reluctance": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance", connector_kind="MAGNETIC",
            description="Constant magnetic reluctance element.",
        ),
    ],
    "air gap": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance", connector_kind="MAGNETIC",
            description="Air gap modeled as a (typically high-value) constant reluctance -- same class as core reluctance.",
        ),
    ],
    "airgap": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance", connector_kind="MAGNETIC",
            description="Air gap modeled as a (typically high-value) constant reluctance -- same class as core reluctance.",
        ),
    ],
    "eddy current": [
        LibraryCandidate(
            modelica_class="Modelica.Magnetic.FluxTubes.Basic.EddyCurrent", connector_kind="MAGNETIC",
            description="Explicit eddy-current loss path in a conductive flux tube.",
        ),
    ],
    "resistor": [
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Basic.Resistor", connector_kind="ELECTRICAL",
            description="Ideal electrical resistor -- a real, explicit I^2*R loss path.",
        ),
    ],
    "inductor": [
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Basic.Inductor", connector_kind="ELECTRICAL",
            description="Ideal electrical inductor.",
        ),
    ],
    "voltage source": [
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Sources.ConstantVoltage", connector_kind="ELECTRICAL",
            description="Ideal constant (DC) voltage source.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Sources.SineVoltage", connector_kind="ELECTRICAL",
            description="Ideal sinusoidal (AC) voltage source.",
        ),
    ],
    "current source": [
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Sources.ConstantCurrent", connector_kind="ELECTRICAL",
            description="Ideal constant (DC) current source.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Sources.SineCurrent", connector_kind="ELECTRICAL",
            description="Ideal sinusoidal (AC) current source -- e.g. a stated RMS excitation amplitude at a given frequency.",
        ),
    ],
    "excitation": [
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Sources.SineVoltage", connector_kind="ELECTRICAL",
            description="Sinusoidal excitation source, if voltage-driven.",
        ),
        LibraryCandidate(
            modelica_class="Modelica.Electrical.Analog.Sources.SineCurrent", connector_kind="ELECTRICAL",
            description="Sinusoidal excitation source, if current-driven (e.g. a stated RMS current amplitude).",
        ),
    ],
}
