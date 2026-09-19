"""Modelica Generation. Mirrors `Modelica Agent.md`, Section 19.

Deterministic -- no LLM call happens here, only rendering of decisions
already made by the planner/mapper stages. Three honest simplifications,
each because building the real thing is a genuinely hard, separate
problem, not because it was overlooked (matches the SysML Agent's own
scope calls, e.g. `DECISIONS.md` D11 on auto-repair):

1. A `LIBRARY_COMPONENT` mapping is referenced directly by its catalog
   class name where it's instantiated -- it never gets its own generated
   file (there's nothing to generate; the class already exists in MSL).
2. A `REUSE_AS_IS`/`MODIFY_LEGACY` component is rebuilt from the actual
   parsed legacy parameters/variables/equations (with any differing
   parameter value overridden to the current requirement bound) --
   faithful reuse, not a placeholder.
3. A brand-new `MODEL`/`BLOCK` mapping with no legacy match becomes a
   syntactically valid but intentionally empty stub (parameters only, no
   fabricated equations) -- deriving real physical/control equations from
   an engineering description is exactly the hard problem this pipeline
   exists to eventually solve, not something to fake with invented
   equations that would misrepresent confidence (see `AI-LOG.md` Case 4 on
   exactly that failure mode, one layer up in the SysML Agent).
4. Structural connections are rendered as comments by default. Real
   `connect()` calls are now generated too, but only between instances
   whose Modelica port names/counts are actually known -- shared, generic
   matching logic (`_match_connections` below) drives every known two-port
   connector family (Fluid's `port_a`/`port_b`, Electrical's `p`/`n`,
   Magnetic's `port_p`/`port_n`), not one family hardcoded in isolation.
   What happens to a port nobody connected genuinely differs by domain,
   though, and stays two separate strategies rather than one: Fluid is
   boundary-condition-driven, so each open port independently gets its own
   `Boundary_pT` (`_resolve_fluid_connections`, added live after OMEdit's
   real solver found every Fluid port structurally unconnected -- see
   `DECISIONS.md` D47). Electrical/Magnetic are potential-based circuits
   (Kirchhoff-style) -- giving every open pin its own independent `Ground`
   would be physically wrong (it would short or fragment the circuit), so
   `_resolve_potential_connections` instead gives exactly one shared
   reference per genuinely connected subgraph. `Vessels.OpenTank`'s
   `ports[nPorts]` array (unlike a fixed two-port pair) and the 4-port
   `ElectroMagneticConverter` (bridging Electrical and Magnetic at once)
   are both special-cased or left alone rather than forced into the plain
   two-port shape. A connection touching any other kind of mapping (a
   MODEL/BLOCK stub, a legacy-reuse class, a signal block) still only
   renders as a comment -- a guessed port name for a class this agent
   doesn't actually understand the interface of would very likely fail
   to compile while looking confidently correct.
5. A never-assigned legacy sequencer variable (e.g. `discrete StepState
   seq`) can now be driven by a REAL, LLM-synthesized state machine
   (`mapping/state_machine_synthesizer.py`), not just an inert default or a
   single scheduled-command pulse -- inferring the narrative order/grouping
   of a set of already-extracted behaviors is a language-understanding
   task, a better fit for LLM reasoning than deterministic pattern-
   matching. Same safety envelope as every other LLM-proposed value in this
   module: `_render_state_machine` independently re-verifies the target
   enum type, every proposed state name against the type's REAL declared
   literals, and every transition's behavior/requirement id before ever
   rendering a `when` block; anything unresolvable is dropped with a
   disclosed comment, never guessed.
6. EVERY remaining value this module could not derive on its own -- a
   generic library placeholder (`_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS`), a
   PARAMETER mapping with no requirement bound, or a from-scratch stub's
   sensed field (`_render_stub_class`) -- is applied only provisionally and
   raised as a pending decision, exactly like a never-assigned legacy
   variable. `mapping/parameter_value_suggester.py` (an LLM call run once
   per generation attempt, in `workflow/modelica_graph.py`) grounds each
   one in the actual project documents before a human ever sees it, so
   "PLACEHOLDER" always means "provisional and disclosed," never "silently
   final."
"""

from __future__ import annotations

import re

from simulation_platform.modelica_gen.naming import instance_name as _instance_name
from simulation_platform.modelica_gen.naming import legal_identifier as _legal_identifier
from simulation_platform.modelica_gen.naming import readable_identifier as _readable_identifier
from simulation_platform.schemas import LegacyComparison, LegacyModel, ModelicaMapping, ModelicaMappingType, SysMLSemanticModel


def _entry_class_name(project_id: str) -> str:
    return _legal_identifier("".join(part.capitalize() for part in project_id.split("_"))) + "System"


def _normalize_unit(unit: str | None) -> str | None:
    """Modelica unit strings (per the Modelica Language Specification) don't
    use `^` for exponents -- e.g. "m3/s", not "m^3/s" -- but a unit sourced
    from an engineering document is often written the human way, with a
    caret. Found live on a real dataset (see DECISIONS.md): passing the
    caret straight through produced a real, valid-looking but non-canonical
    Modelica unit string that the deterministic unit checker correctly
    flagged as unrecognized. Stripping `^` here fixes the actually-generated
    syntax, not just the validator's opinion of it."""

    return unit.replace("^", "") if unit else unit


# Every entry here is a real `Modelica.Fluid.*` class whose base class
# (checked directly against the MSL 4.1.0 source, not guessed from an error
# message) declares at least one parameter with NO default value at all --
# a bare instantiation compiles this agent's own `checkModel()` check
# cleanly (a structural/type check) but fails real translation, since every
# `fixed=true` parameter (the default) needs a concrete value at that
# point. Found live, one class at a time, each only via an actual OMEdit
# simulation attempt this agent's own compile check never reaches (see
# DECISIONS.md D42/D44/D45/D46) -- `Modelica.Fluid.Machines.PrescribedPump`
# was added proactively once the pattern was clear, the same way D37 fixed
# compiler-agent's `package.mo` bug before that agent's own first live run
# could hit it. Every value here is a documented, reasonable STARTING
# placeholder (e.g. 1500 rpm is a common synchronous pump speed, 1 bar a
# common nominal valve pressure drop), applied provisionally so the model
# stays simulatable -- but never treated as final: `_apply_parameter_
# overrides` raises each one as a pending decision an LLM then grounds in
# the actual project documents before a human confirms it (see `mapping/
# parameter_value_suggester.py`), same propose-then-confirm discipline as
# a never-assigned legacy variable. Keyed by exact target class, not the
# whole `Fluid` namespace, since which parameters are mandatory genuinely
# varies per MSL class (e.g. `ValveIncompressible` needs no geometry,
# `OpenTank` needs no nominal pressure drop).
# A bare signal-connector *type* (e.g. `Modelica.Blocks.Interfaces.
# RealOutput`) instantiated directly, not as a port on some other block --
# found live (see DECISIONS.md D52): `RealOutput` is really just `output
# Real` (a plain signal), and a standalone instance with nothing feeding it
# a value is exactly as under-determined as a legacy variable never
# assigned anywhere (this module already has a placeholder-equation
# pattern for that -- see `_render_legacy_based_class`). Values are
# type-appropriate placeholders, not a fabricated real signal.
_BARE_SIGNAL_CONNECTOR_DEFAULTS: dict[str, str] = {
    "Modelica.Blocks.Interfaces.RealOutput": "0.0",
    "Modelica.Blocks.Interfaces.RealInput": "0.0",
    "Modelica.Blocks.Interfaces.BooleanOutput": "false",
    "Modelica.Blocks.Interfaces.BooleanInput": "false",
    "Modelica.Blocks.Interfaces.IntegerOutput": "0",
    "Modelica.Blocks.Interfaces.IntegerInput": "0",
}

_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS: dict[str, list[str]] = {
    # `use_portsData` defaults to `true`, which requires a `diameter` for
    # every port in `portsData[nPorts]` with no default at all -- only a
    # real risk once a tank actually has ports (D47's connect() fix can
    # set `nPorts` > 0), found live in OMEdit the very next simulation
    # attempt after that fix landed. `use_portsData = false` switches to
    # MSL's own simpler zero-diameter port treatment (`portsData_diameter
    # = zeros(nPorts)`, in `Vessels.mo`) -- a real, built-in MSL
    # simplification, not a fabricated per-port diameter this pipeline has
    # no actual geometry data for.
    "Modelica.Fluid.Vessels.OpenTank": ["height = 1.0", "crossArea = 1.0", "use_portsData = false"],
    # `opening` is a genuine `input Real` control signal (0 = closed, 1 =
    # fully open) on the valve, connected internally to `opening_actual`
    # (`connect(opening, opening_actual);` in `Valves.mo`, when
    # `filteredOpening=false`, the default) -- it's not a mandatory
    # *parameter* like the other two below, but a real, undriven input
    # port with no default of its own. Root-caused live (see DECISIONS.md
    # D53) via a minimal, isolated reproduction after `dp_nominal`/
    # `m_flow_nominal` alone still left `relativeFlowCoefficient`
    # unresolved: `opening`'s indeterminacy propagates through
    # `opening_actual` into every downstream flow equation. Nothing
    # upstream in this pipeline wires a real control/actuation signal to
    # a valve, so `opening = 1.0` (fully open) is the documented
    # placeholder -- a common Modelica.Fluid simplification when no real
    # control signal exists, not fabricated control logic.
    "Modelica.Fluid.Valves.ValveIncompressible": ["dp_nominal = 100000", "m_flow_nominal = 1.0", "opening = 1.0"],
    "Modelica.Fluid.Machines.PrescribedPump": ["N_nominal = 1500"],
    # Magnetic Circuit (Level 3) + generic electrical -- each checked live
    # via `omc` (a bare instantiation's real `simulate()` attempt, not
    # `checkModel()`, warns "has no value... using available start value"
    # for exactly these, the same detection method used for the Fluid
    # entries above). `Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance`
    # (R_m) and `ElectroMagneticConverter` (N) are deliberately NOT listed
    # here -- both have real `=` defaults (R_m=1, N=1) confirmed by reading
    # their actual source, not just an absence of warnings.
    "Modelica.Electrical.Analog.Basic.Resistor": ["R = 1.0"],
    "Modelica.Electrical.Analog.Basic.Inductor": ["L = 1.0"],
    "Modelica.Electrical.Analog.Sources.ConstantVoltage": ["V = 1.0"],
    "Modelica.Electrical.Analog.Sources.SineVoltage": ["V = 1.0", "f = 50"],
    "Modelica.Electrical.Analog.Sources.ConstantCurrent": ["I = 1.0"],
    "Modelica.Electrical.Analog.Sources.SineCurrent": ["I = 1.0", "f = 50"],
}


def _default_modifiers(target: str) -> list[str]:
    """Every `Modelica.Fluid.*` component declares its working fluid as a
    `replaceable package Medium = Modelica.Media.Interfaces.PartialMedium`
    -- a partial/abstract default with no concrete substance data
    ("Constant openTank.Medium.singleState is used without having been
    given a value"). Water is the documented default assumption absent any
    other information. See `_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS` above for
    the per-class mandatory-parameter placeholders layered on top (which,
    despite this function's own Fluid-specific Medium handling, also covers
    non-Fluid classes -- e.g. Electrical/Magnetic -- that need no Medium
    redeclaration at all)."""

    modifiers: list[str] = []
    if target.startswith("Modelica.Fluid."):
        modifiers.append("redeclare package Medium = Modelica.Media.Water.StandardWater")
    modifiers.extend(_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS.get(target, []))
    return modifiers


def _apply_parameter_overrides(
    instance: str,
    modifiers: list[str],
    placeholder_names: set[str],
    command_overrides: dict[str, str],
    pending_decisions: list[dict] | None,
    target: str,
    reason: str,
) -> list[str]:
    """Same propose-then-confirm treatment as a never-assigned legacy
    variable, applied to `_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS`'s generic
    values -- these compile and simulate fine (a real MSL class with a
    real, if generic, value), but a generic `dp_nominal = 100000` or
    `N_nominal = 1500` has no connection to the actual problem being
    modeled. Only touches a modifier whose name is a known placeholder
    (`placeholder_names`) -- a `redeclare package Medium = ...` modifier's
    "name" (the text before its own `=`) never matches one of those, so it
    passes through completely unchanged."""

    resolved: list[str] = []
    for modifier in modifiers:
        name, _, default_value = modifier.partition("=")
        name = name.strip()
        if name not in placeholder_names:
            resolved.append(modifier)
            continue

        override_key = f"{instance}.{name}"
        confirmed = command_overrides.get(override_key)
        if confirmed is not None:
            resolved.append(f"{name} = {confirmed}")
        else:
            if pending_decisions is not None:
                pending_decisions.append({
                    "class_name": target,
                    "variable": override_key,
                    "suggested_value": default_value.strip(),
                    "reason": f"generic MSL placeholder for {reason} -- not derived from the actual problem",
                    "grounded": False,
                })
            resolved.append(modifier)
    return resolved


# The families of MSL classes whose port names are fixed and known -- each
# checked directly against the real MSL 4.1.0 source (`omc` introspection +
# a real compile/simulate run), never guessed. `Modelica.Fluid.Vessels.
# OpenTank` is handled separately below (a `ports[nPorts]` array, not a
# fixed two-port pair), and `Modelica.Magnetic.FluxTubes.Basic.
# ElectroMagneticConverter` is deliberately NOT listed anywhere here -- it
# has FOUR ports across two different connector kinds at once (Electrical
# `p`/`n` and Magnetic `port_p`/`port_n`), a shape this simple two-port
# matcher doesn't understand; a connection touching it still only renders
# as a comment, same as any other interface this pipeline can't confidently
# resolve.
_FLUID_TWO_PORT_CLASSES: dict[str, tuple[str, str]] = {
    "Modelica.Fluid.Valves.ValveIncompressible": ("port_a", "port_b"),
    "Modelica.Fluid.Machines.PrescribedPump": ("port_a", "port_b"),
}
_FLUID_VESSEL_CLASSES = {"Modelica.Fluid.Vessels.OpenTank"}
_FLUID_BOUNDARY_CLASS = "Modelica.Fluid.Sources.Boundary_pT"

_ELECTRICAL_TWO_PORT_CLASSES: dict[str, tuple[str, str]] = {
    "Modelica.Electrical.Analog.Basic.Resistor": ("p", "n"),
    "Modelica.Electrical.Analog.Basic.Inductor": ("p", "n"),
}
_ELECTRICAL_REFERENCE_CLASS = "Modelica.Electrical.Analog.Basic.Ground"
_ELECTRICAL_REFERENCE_PORT = "p"

_MAGNETIC_TWO_PORT_CLASSES: dict[str, tuple[str, str]] = {
    "Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance": ("port_p", "port_n"),
    "Modelica.Magnetic.FluxTubes.Basic.EddyCurrent": ("port_p", "port_n"),
}
_MAGNETIC_REFERENCE_CLASS = "Modelica.Magnetic.FluxTubes.Basic.Ground"
_MAGNETIC_REFERENCE_PORT = "port"


def _make_instance_resolver(
    sysml_semantic_model: SysMLSemanticModel,
    engineering_id_by_name: dict[str, str],
    element_registry: dict[str, tuple[str, str]],
):
    """Shared by every connection-resolution family below: bridges a SysML
    *instance* name (e.g. "tk101", from `sysml_semantic_model.connections`)
    back to the `ModelicaMapping` it produced -- instance name -> SysML
    part-def name (via `sysml_semantic_model.parts`) -> engineering id (via
    `engineering_id_by_name`, the SysML Agent's own traceability map) ->
    `element_registry` (this module's own sysml_element -> (target,
    instance) map, built as mappings are processed)."""

    part_def_by_instance_name = {p.instance_name: p.part_def for p in sysml_semantic_model.parts}

    def _resolve(instance_name: str) -> tuple[str, str] | None:
        part_def = part_def_by_instance_name.get(instance_name)
        if part_def is None:
            return None
        engineering_id = engineering_id_by_name.get(part_def, part_def)
        return element_registry.get(engineering_id)

    return _resolve


def _match_connections(
    connections,
    resolve,
    port_available,
    next_port,
    on_connected=None,
) -> list[str]:
    """Generic SysML-connection -> real Modelica `connect()` matcher,
    shared by every two-port-like connector family (Fluid, Electrical,
    Magnetic -- see the domain-specific wrappers below). Deliberately
    domain-agnostic: it only knows how to resolve an instance and ask "is a
    port available" / "give me the next one" -- what counts as available (a
    fixed two-port pair vs. a growable `ports[]` array) and what a leftover
    port becomes (an independent boundary vs. a shared reference) are both
    entirely up to the caller.

    Checks BOTH endpoints have an available port BEFORE consuming either
    one (see DECISIONS.md D49): consuming the source's port first and only
    then discovering the target's is already exhausted silently leaked the
    source's port, with no `connect()` and no fallback ever generated for
    it. `on_connected(source_instance, target_instance)`, when given, lets
    a caller track which instances ended up in the same connected network
    (used by the potential-based domains to size their shared reference).
    """

    connect_lines: list[str] = []
    for connection in connections:
        source = resolve(connection.source_instance)
        target = resolve(connection.target_instance)
        if source is None or target is None:
            continue
        source_target, source_instance = source
        target_target, target_instance = target
        if not (port_available(source_target, source_instance) and port_available(target_target, target_instance)):
            continue
        source_port = next_port(source_target, source_instance)
        target_port = next_port(target_target, target_instance)
        connect_lines.append(f"  connect({source_instance}.{source_port}, {target_instance}.{target_port});")
        if on_connected is not None:
            on_connected(source_instance, target_instance)
    return connect_lines


class _UnionFind:
    """Minimal disjoint-set structure -- used only to group instances of a
    potential-based domain (Electrical/Magnetic) into their connected
    subgraphs, so each subgraph gets exactly one shared reference/ground
    instead of one per open port (see `_resolve_potential_connections`)."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, item: str) -> str:
        self._parent.setdefault(item, item)
        root = item
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[item] != root:
            self._parent[item], item = root, self._parent[item]
        return root

    def union(self, a: str, b: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self._parent[root_a] = root_b


# Half of `_LIBRARY_CLASS_PLACEHOLDER_PARAMETERS`'s own
# `ValveIncompressible` `dp_nominal` placeholder (100000 Pa) -- found live
# on a real simulation: the ORIGINAL step (a flat 1000 Pa) only ever
# solved the *symmetry* problem (see D52 below), never the *magnitude*
# one. A `ValveIncompressible`'s actual flow scales roughly with
# `sqrt(actual_dp / dp_nominal)`, so a 1000 Pa differential against a
# 100000 Pa nominal produced only ~10% of nominal flow (and less for
# later-staggered boundaries) -- a real Tank system's level barely moved
# (0.001 m over 900 s, instead of the ~4.5 m a correctly-flowing valve at
# its own grounded nominal flow rate would produce). Sized to be a
# meaningful FRACTION of a typical valve's own nominal operating point,
# not just numerically distinct from its neighbors.
_FLUID_BOUNDARY_PRESSURE_STEP = 50000


def _resolve_fluid_connections(
    sysml_semantic_model: SysMLSemanticModel,
    engineering_id_by_name: dict[str, str],
    element_registry: dict[str, tuple[str, str]],
    instance_records: list[dict],
    command_overrides: dict[str, str] | None = None,
    pending_decisions: list[dict] | None = None,
) -> tuple[list[str], list[dict]]:
    """Real `connect()` generation for the one family of MSL classes whose
    port names/counts are actually known. Found live in OMEdit (see
    DECISIONS.md D47): with no real `connect()` calls at all (this
    module's own Known Simplification #4, previously unconditional),
    every `Modelica.Fluid` port was structurally unconnected, and OMEdit's
    symbolic solver reported more unknowns than equations ("Too few
    equations") since nothing ever pinned down a port's pressure/enthalpy.

    Bridges a SysML *instance* name (e.g. "tk101", from
    `sysml_semantic_model.connections`) back to the `ModelicaMapping` it
    produced via the same two-step lookup `legacy/legacy_comparator.py`
    already uses: instance name -> SysML part-def name (via
    `sysml_semantic_model.parts`) -> engineering id (via
    `engineering_id_by_name`, the SysML Agent's own traceability map) ->
    `element_registry` (this module's own sysml_element -> (target,
    instance) map, built as mappings are processed).

    A connection where either endpoint isn't one of the known Fluid
    classes above is left alone entirely -- still rendered only as a
    `// connect: ...` comment by the caller, exactly as before this fix.
    """

    resolve = _make_instance_resolver(sysml_semantic_model, engineering_id_by_name, element_registry)

    # Pre-populated for every known two-port instance, not just ones a
    # connection actually touches -- `port_a`/`port_b` are plain, always-
    # present connectors (not sized by a count), so a two-port device the
    # SysML model never connects at all needs boundary sources on *both*
    # ports, the same as a device left with one port unresolved.
    open_ports: dict[str, list[str]] = {
        instance: list(_FLUID_TWO_PORT_CLASSES[target])
        for target, instance in element_registry.values()
        if target in _FLUID_TWO_PORT_CLASSES
    }
    tank_port_count: dict[str, int] = {}

    def _port_available(target: str, instance: str) -> bool:
        if target in _FLUID_TWO_PORT_CLASSES:
            return bool(open_ports.get(instance))
        return target in _FLUID_VESSEL_CLASSES

    def _next_port(target: str, instance: str) -> str:
        if target in _FLUID_TWO_PORT_CLASSES:
            return open_ports[instance].pop(0)
        tank_port_count[instance] = tank_port_count.get(instance, 0) + 1
        return f"ports[{tank_port_count[instance]}]"

    connect_lines = _match_connections(sysml_semantic_model.connections, resolve, _port_available, _next_port)

    # Anything left in `open_ports` is a genuine open end of the flow
    # network (or a two-port device the SysML model never connects at
    # all) -- give it its own boundary condition so the system stays
    # fully determined, the same way a real end-of-line valve/pump would
    # need one in a hand-built model, rather than leaving the port
    # dangling the way a bare instantiation did before this fix.
    #
    # Every `Boundary_pT`'s pressure defaults to the same `Medium.p_default`
    # (~atmospheric) -- found live (see DECISIONS.md D52): a valve/pump
    # bounded on *both* ends by identical-pressure boundaries has zero
    # driving pressure differential, an outright mathematically
    # indeterminate flow direction (`relativeFlowCoefficient` reported
    # unresolved), not a missing-default-value problem another placeholder
    # value alone could fix. Staggering each auto-boundary's pressure by a
    # small, distinct amount guarantees no two auto-boundaries anywhere in
    # the model ever share an identical pressure, breaking every possible
    # symmetric pairing regardless of chain topology (an isolated single
    # valve, or a multi-valve chain whose two open ends happen to land on
    # the same port letter) -- a stated placeholder differential, not real
    # plant pressure data.
    #
    # Found live in this session's own gap audit: this value was applied
    # unconditionally with no `pending_decisions` entry at all -- a human
    # running the pipeline was never even told an auto-boundary was
    # inserted, let alone given a chance to supply a real plant pressure
    # if one is actually known. Disclosed the same way as every other
    # gap now, but marked `grounded=True` -- this is a deliberate
    # numerical technique (breaking a symmetric zero-driving-pressure
    # network), not a guess the LLM parameter suggester should try to
    # "improve": an LLM-invented pressure could easily reintroduce the
    # exact symmetric-pairing bug this staggering exists to prevent.
    extra_records: list[dict] = []
    boundary_index = 0
    for instance, remaining_ports in open_ports.items():
        for port in remaining_ports:
            boundary_index += 1
            boundary_instance = f"{instance}_{port}_boundary"
            staggered_pressure = 101325 + boundary_index * _FLUID_BOUNDARY_PRESSURE_STEP
            override_key = f"{boundary_instance}.p"
            confirmed = (command_overrides or {}).get(override_key)
            pressure_value = confirmed if confirmed is not None else staggered_pressure
            if confirmed is None and pending_decisions is not None:
                pending_decisions.append({
                    "class_name": _FLUID_BOUNDARY_CLASS,
                    "variable": override_key,
                    "suggested_value": str(staggered_pressure),
                    "reason": (
                        f"auto boundary condition for {instance}.{port}, left open by the SysML model -- "
                        "pressure staggered only to avoid a symmetric zero-driving-pressure network, not "
                        "real plant data; override with a real boundary pressure if one is actually known"
                    ),
                    "grounded": True,
                })
            comment = f"auto boundary condition for {instance}.{port}, left open by the SysML model " + (
                "(user-approved pressure)" if confirmed is not None
                else "(PLACEHOLDER pressure, staggered to avoid a symmetric zero-driving-pressure network)"
            )
            extra_records.append({
                "target": _FLUID_BOUNDARY_CLASS,
                "instance": boundary_instance,
                "modifiers": [*_default_modifiers(_FLUID_BOUNDARY_CLASS), "nPorts = 1", f"p = {pressure_value}"],
                "comment": comment,
            })
            connect_lines.append(f"  connect({instance}.{port}, {boundary_instance}.ports[1]);")

    # `OpenTank`'s `ports[nPorts]` defaults to `nPorts = 0` (no ports at
    # all) -- any tank actually touched by a real connection needs its
    # own instance record patched with the exact count wired, or the
    # `connect()` calls above would reference a port index that doesn't
    # exist.
    if tank_port_count:
        records_by_instance = {r["instance"]: r for r in instance_records}
        for instance, count in tank_port_count.items():
            record = records_by_instance.get(instance)
            if record is not None:
                record["modifiers"] = [*record["modifiers"], f"nPorts = {count}"]

    return connect_lines, extra_records


def _resolve_potential_connections(
    sysml_semantic_model: SysMLSemanticModel,
    engineering_id_by_name: dict[str, str],
    element_registry: dict[str, tuple[str, str]],
    two_port_classes: dict[str, tuple[str, str]],
    reference_class: str,
    reference_port: str,
) -> tuple[list[str], list[dict]]:
    """Real `connect()` generation for a potential-based connector family
    (Electrical, Magnetic) -- one call per family, since a shared reference
    in one domain has no meaning in the other. Deliberately a DIFFERENT
    strategy from `_resolve_fluid_connections`, not a copy of it: Fluid is
    boundary-condition-driven, so each open port can independently get its
    own value; a potential-based (Kirchhoff-style) circuit instead needs
    exactly ONE shared reference/ground per genuinely connected network --
    giving every open pin its own independent `Ground` would be physically
    wrong (it would short or fragment the circuit), not just a stylistic
    difference. Reuses the same generic `_match_connections` matcher and
    the same D49 leak-prevention discipline as the Fluid resolver.

    Any two-port instance not in `two_port_classes` is ignored entirely --
    handled by a different call (the other domain), or left as a comment by
    the caller if this pipeline doesn't understand its interface at all
    (e.g. the 4-port `ElectroMagneticConverter`)."""

    resolve = _make_instance_resolver(sysml_semantic_model, engineering_id_by_name, element_registry)

    relevant_instances = {
        instance: target for target, instance in element_registry.values() if target in two_port_classes
    }
    if not relevant_instances:
        return [], []

    open_ports: dict[str, list[str]] = {
        instance: list(two_port_classes[target]) for instance, target in relevant_instances.items()
    }
    union_find = _UnionFind()
    for instance in relevant_instances:
        union_find.find(instance)  # every instance starts as its own singleton group, even if never connected

    def _port_available(target: str, instance: str) -> bool:
        return target in two_port_classes and bool(open_ports.get(instance))

    def _next_port(target: str, instance: str) -> str:
        return open_ports[instance].pop(0)

    connect_lines = _match_connections(
        sysml_semantic_model.connections, resolve, _port_available, _next_port, on_connected=union_find.union
    )

    # Group the remaining instances by connected subgraph; give each
    # subgraph exactly one shared reference, attached to one of ITS OWN
    # leftover ports -- never a fabricated multi-way junction on an
    # already-fully-connected port this pipeline has no infrastructure to
    # model (Modelica connectors CAN support N-way junctions, but nothing
    # here tracks that; safer to disclose the gap than guess at it).
    groups: dict[str, list[str]] = {}
    for instance in relevant_instances:
        groups.setdefault(union_find.find(instance), []).append(instance)

    extra_records: list[dict] = []
    reference_index = 0
    for members in groups.values():
        anchor = next((m for m in sorted(members) if open_ports.get(m)), None)
        if anchor is None:
            connect_lines.append(
                f"  // no reference/ground available for this connected network ({', '.join(sorted(members))}) "
                "-- every port is already connected elsewhere; may be under-determined without one"
            )
            continue
        reference_index += 1
        anchor_port = open_ports[anchor].pop(0)
        reference_instance = f"{anchor}_reference_{reference_index}"
        extra_records.append({
            "target": reference_class,
            "instance": reference_instance,
            "modifiers": [],
            "comment": f"auto reference/ground for the connected network containing {anchor}",
        })
        connect_lines.append(f"  connect({anchor}.{anchor_port}, {reference_instance}.{reference_port});")

    # Only ONE reference per subgraph is correct (see docstring) -- but a
    # subgraph with more than one leftover port (e.g. two components in a
    # simple series chain each have one far end open) has ports beyond the
    # chosen anchor that are now genuinely dangling. Silently doing nothing
    # with them would hide a real gap; disclose each one honestly instead
    # of fabricating a second reference or guessing a connection.
    for instance, remaining_ports in open_ports.items():
        for port in remaining_ports:
            connect_lines.append(
                f"  // {instance}.{port} left unconnected -- already gave its network a shared reference "
                "elsewhere; no further real connection available for this specific port"
            )

    return connect_lines, extra_records


def _find_legacy_class(sysml_element_name: str, legacy_class_name: str, legacy_models: list[LegacyModel]):
    for legacy_model in legacy_models:
        for legacy_class in legacy_model.classes:
            if legacy_class.name == legacy_class_name:
                return legacy_class
    return None


_DEFAULT_VALUE_BY_TYPE = {"Boolean": "false", "Integer": "0", "Real": "0.0", "String": '""'}
# Either a direct assignment (`name := ...` / `name = ...`, excluding
# `==`) or `der(name)` appearing anywhere -- a state variable governed by
# its own differential equation (`der(tank1Level) = ...;`) is already
# fully determined and must never *also* get a placeholder equation.
# Found live on a real dataset (see DECISIONS.md D50): the first version
# of this check only looked for a direct assignment, so a `start=`-
# carrying state variable already governed by `der(...)` got a second,
# conflicting constant equation on top of its real ODE, silently turning
# a level that should evolve over time into a fixed constant.
_ASSIGNMENT_TARGET = r"(?:\bder\(\s*{name}\s*\)|{name}\s*:?=(?!=))"


def _is_ever_assigned(name: str, statements: list[str]) -> bool:
    pattern = re.compile(_ASSIGNMENT_TARGET.format(name=re.escape(name)))
    return any(pattern.search(statement) for statement in statements)


_COMMAND_PULSE_WIDTH_SECONDS = 1.0


def _matching_scheduled_times(variable_name: str, scheduled_commands: list[dict]) -> list[float]:
    """Matches a never-assigned variable (e.g. "startCmd") against an
    extracted operator command schedule (e.g. command_name="START") by a
    simple case-insensitive substring check -- deliberately not fuzzy
    matching, so it's easy to reason about which variables this will and
    won't catch. Found live on a real dataset: a document had an exact,
    timestamped command schedule (and a benchmark ground-truth trace) for
    exactly the variables a reused legacy class left permanently `false`."""

    name_lower = variable_name.lower()
    times = [
        cmd["time_value"] for cmd in scheduled_commands
        if cmd.get("command_name") and cmd["command_name"].lower() in name_lower
    ]
    return sorted(times)


def _render_pulse_expression(times: list[float]) -> str:
    """A real time-driven boolean signal, true for one pulse width starting
    at each scheduled time -- long enough for `edge(...)` to see a real
    rising edge (and a later falling edge), never permanently latched."""

    clauses = [f"(time >= {t} and time < {t + _COMMAND_PULSE_WIDTH_SECONDS})" for t in times]
    return " or ".join(clauses)


_ENUM_TYPE_PATTERN = re.compile(r"type\s+(\w+)\s*=\s*enumeration\s*\(([^)]*)\)")


def _enum_literals_for_type(legacy_class, type_name: str) -> set[str] | None:
    """The REAL declared literal names for one specific enum type in this
    legacy class, or None if that type isn't declared here at all --
    `None` (not an empty set) matters, so a state machine can be rejected
    for "unknown type" separately from "known type, but proposed a state
    that isn't a real literal of it" (see `_render_state_machine`)."""

    for type_decl in legacy_class.type_declarations:
        match = _ENUM_TYPE_PATTERN.search(type_decl)
        if match and match.group(1) == type_name:
            return {literal.strip() for literal in match.group(2).split(",") if literal.strip()}
    return None


def _render_state_machine(
    var,
    legacy_class,
    state_machine: dict,
    behaviors_by_id: dict,
    requirements_by_id: dict,
) -> tuple[str | None, list[str]] | None:
    """Renders a real `when seq==X and <cond> then seq:=Y; end when;` chain
    for a never-assigned legacy sequencer variable, from an LLM-synthesized
    `StateMachine` (see `mapping/state_machine_synthesizer.py`) -- or
    returns None if the state machine doesn't check out against what was
    ACTUALLY declared here (wrong enum type, an invented state name, ...).
    Every reference is independently re-verified, exactly like
    `_render_behavior_equation` re-verifies `trigger_variable` -- the LLM
    proposes a state machine, this function never trusts it blindly.

    Returns (timer_declaration, equation_lines): the timer is a fresh
    `discrete Real {var}EnteredAt` reset on every transition, letting a
    `wait_parameter_id`-gated transition express "N seconds after entering
    this state" (`time - {var}EnteredAt >= N`) regardless of which state
    was entered, without the LLM ever having to invent Modelica timer
    syntax itself.

    Every resolved transition is chained into ONE `when ... elsewhen ...
    end when;` clause, never separate `when` clauses each assigning the
    same variable -- found live via a real `omc` compile attempt: two
    independent `when` clauses both assigning `seq` produced a genuine
    "Too many equations, over-determined system" error (Modelica's
    equation-section semantics require exactly one governing equation per
    variable; `elsewhen` is the language's own construct for "more than
    one condition can assign this same variable," not a stylistic choice).

    Every guard condition reads `pre(...)` of the state/timer, never their
    raw current value -- also found live: without `pre(...)`, `omc`'s
    backend reported a real "purely discrete algebraic loop" (the guard
    and the assignment it gates would otherwise mutually depend on each
    other within the same event). `pre(x)` (a real Modelica built-in --
    "value of `x` at the last event") is the language's own, standard
    idiom for exactly this FSM pattern, not a workaround invented here.
    """

    if state_machine.get("target_type_hint") != var.type:
        return None

    real_literals = _enum_literals_for_type(legacy_class, var.type)
    if real_literals is None:
        return None

    states = state_machine.get("states") or []
    if not states or not set(states) <= real_literals:
        return None
    if state_machine.get("initial_state") not in states:
        return None

    known_names = {v.name for v in legacy_class.variables} | {p.name for p in legacy_class.parameters}
    timer_name = f"{var.name}EnteredAt"

    disclosed_gaps: list[str] = []
    clauses: list[tuple[str, str]] = []  # (condition, reason_comment) pairs, in order
    for transition in state_machine.get("transitions", []):
        from_state = transition.get("from_state")
        to_state = transition.get("to_state")
        if from_state not in states or to_state not in states:
            continue

        condition = None
        trigger_behavior_id = transition.get("trigger_behavior_id")
        condition_variable = transition.get("condition_variable")
        wait_parameter_id = transition.get("wait_parameter_id")

        if trigger_behavior_id and condition_variable and condition_variable in known_names:
            behavior = behaviors_by_id.get(trigger_behavior_id)
            if behavior is not None:
                operator = behavior.get("trigger_operator")
                trigger_value = behavior.get("trigger_value")
                if operator and trigger_value is not None:
                    condition = f"{condition_variable} {operator} {trigger_value}"
        elif wait_parameter_id:
            requirement = requirements_by_id.get(wait_parameter_id)
            bound = _requirement_bound_value(requirement) if requirement is not None else None
            if bound is not None and _is_numeric(bound):
                condition = f"time - pre({timer_name}) >= {bound}"

        if condition is None:
            disclosed_gaps.append(
                f"  // state machine transition {from_state} -> {to_state} skipped -- could not verify "
                "a real trigger/wait reference for it"
            )
            continue

        reason_comment = f"  // {transition['reason']}" if transition.get("reason") else ""
        full_condition = f"pre({var.name}) == {var.type}.{from_state} and {condition}"
        assignment = f"    {var.name} = {var.type}.{to_state};\n    {timer_name} = time;"
        clauses.append((f"{full_condition} then\n{assignment}", reason_comment))

    if not clauses:
        return (None, disclosed_gaps) if disclosed_gaps else None

    chain_lines = [f"  when {clauses[0][0]}{clauses[0][1]}"]
    for condition_then, reason_comment in clauses[1:]:
        chain_lines.append(f"  elsewhen {condition_then}{reason_comment}")
    chain_lines.append("  end when;")

    return f"  discrete Real {timer_name}(start=0);", [*disclosed_gaps, "\n".join(chain_lines)]


def _render_legacy_based_class(
    class_name: str,
    legacy_class,
    overrides: dict[str, str],
    scheduled_commands: list[dict] | None = None,
    command_overrides: dict[str, str] | None = None,
    pending_decisions: list[dict] | None = None,
    state_machines: list[dict] | None = None,
    behaviors_by_id: dict | None = None,
    requirements_by_id: dict | None = None,
) -> str:
    lines = [f"model {class_name}"]
    for type_decl in legacy_class.type_declarations:
        lines.append(f"  {type_decl}")
    for param in legacy_class.parameters:
        value = overrides.get(param.name, param.value)
        unit_clause = f'(unit="{_normalize_unit(param.unit)}") ' if param.unit else ""
        lines.append(f"  parameter {param.type} {param.name}{unit_clause}= {value};")

    all_statements = legacy_class.equations + legacy_class.algorithm_statements
    placeholder_equations: list[str] = []
    for var in legacy_class.variables:
        prefix = "discrete " if var.is_discrete else ""
        modifier_parts = []
        if var.unit:
            modifier_parts.append(f'unit="{_normalize_unit(var.unit)}"')
        if var.start_value:
            modifier_parts.append(f"start={var.start_value}")
        modifier_clause = f"({', '.join(modifier_parts)})" if modifier_parts else ""
        lines.append(f"  {prefix}{var.type} {var.name}{modifier_clause};")

        # A variable never assigned anywhere in the reused class (found
        # live on a real dataset -- see DECISIONS.md D50): the original
        # legacy source itself never gives some variables a value either
        # (e.g. `startCmd`/`stopCmd`/`shutCmd`, `discrete StepState seq`)
        # -- they're genuinely meant to be driven by a sequencer/HMI this
        # standalone fragment doesn't include, not something this parser
        # ever dropped. Faithfully reusing the algorithm that reads them
        # (e.g. `edge(startCmd)`) without also giving them *some* equation
        # leaves the reused class structurally under-determined -- the
        # real solver's own "Too few equations" error, not a fabricated
        # one. A documented placeholder equation (the variable's own
        # `start=` value if it has one, otherwise a type-appropriate
        # default) keeps the class simulatable without inventing a real
        # command signal -- UNLESS the project's own documents state an
        # actual operator command schedule for it (a real test procedure
        # found live: an exact "at 20s START, at 220s STOP, ..." schedule,
        # with a benchmark ground-truth trace, that would otherwise leave
        # every tank level frozen for the entire simulation -- structurally
        # valid, physically meaningless). When a schedule matches, a real
        # time-driven pulse expression is PROPOSED, not applied blind: it's
        # used provisionally (so the file stays loadable) but also recorded
        # in `pending_decisions` for a human to confirm, per `new
        # direction.txt` §15 -- propose, explain why, ask, only then treat
        # it as final. `command_overrides` (keyed by variable name) is
        # where a caller supplies the user's actual confirmed answer, which
        # always wins over the raw suggestion.
        if not _is_ever_assigned(var.name, all_statements):
            # A never-assigned discrete sequencer variable (e.g. `discrete
            # StepState seq`) is exactly the population an LLM-synthesized
            # `StateMachine` targets -- checked BEFORE the scheduled-
            # command/inert-default path below, since a real, verified
            # transition chain is strictly more informative than either of
            # those (see `mapping/state_machine_synthesizer.py`).
            matched_state_machine = next(
                (sm for sm in (state_machines or []) if sm.get("target_type_hint") == var.type), None
            )
            rendered_state_machine = (
                _render_state_machine(var, legacy_class, matched_state_machine, behaviors_by_id or {}, requirements_by_id or {})
                if matched_state_machine is not None else None
            )
            if rendered_state_machine is not None:
                timer_declaration, sm_equation_lines = rendered_state_machine
                if timer_declaration:
                    lines.append(timer_declaration)
                placeholder_equations.extend(sm_equation_lines)
                continue

            matched_times = _matching_scheduled_times(var.name, scheduled_commands or [])
            if matched_times:
                suggestion = _render_pulse_expression(matched_times)
                reason = (
                    f"matches a scheduled command in the project's own documents at t={matched_times} s"
                )
                # A real, exactly-derived value (an actual extracted
                # timestamp) -- never sent through the LLM parameter-value
                # refiner (`mapping/parameter_value_suggester.py`) for a
                # "smarter" guess, which could only make it worse.
                grounded = True
            else:
                suggestion = var.start_value or _DEFAULT_VALUE_BY_TYPE.get(var.type)
                reason = "no scheduled command found for this variable; falling back to an inert default"
                grounded = False

            if suggestion is None:
                continue

            confirmed = (command_overrides or {}).get(var.name)
            if confirmed is not None:
                placeholder_equations.append(f"  {var.name} = {confirmed};  // user-approved ({reason})")
            else:
                if pending_decisions is not None:
                    pending_decisions.append({
                        "class_name": class_name,
                        "variable": var.name,
                        "suggested_value": suggestion,
                        "reason": reason,
                        "grounded": grounded,
                    })
                placeholder_equations.append(
                    f"  {var.name} = {suggestion};  "
                    f"// PROPOSED, pending confirmation ({reason}) -- never assigned in the original legacy source"
                )

    if legacy_class.algorithm_statements:
        lines.append("algorithm")
        for statement in legacy_class.algorithm_statements:
            lines.append(f"  {statement}")
    if legacy_class.equations or placeholder_equations:
        lines.append("equation")
        for eq in legacy_class.equations:
            lines.append(f"  {eq}")
        lines.extend(placeholder_equations)
    lines.append(f"end {class_name};")
    return "\n".join(lines) + "\n"


def _requirement_bound_value(requirement: dict) -> str | None:
    for key in ("max", "min", "value"):
        if requirement.get(key) is not None:
            return str(requirement[key])
    return None


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _dedupe(name: str, used: set[str], case_insensitive: bool = False) -> str:
    """Guarantees a unique name against `used`, appending `_2`, `_3`, ...
    on a collision. Found live on a real dataset (see DECISIONS.md): two
    different SysML entities independently mapped to the same
    LIBRARY_COMPONENT target class rendered the identical instance name
    (both "openTank"), and the real compiler correctly rejected the
    resulting duplicate declaration. Same backstop pattern as the SysML
    Agent's `_deduplicate_names` (D32) -- a prompt instruction alone can't
    guarantee this, only checking does.

    `case_insensitive=True` (used for class names, since they become file
    names) additionally catches a collision Python's own case-sensitive
    set never would: found live, two class names differing only by case
    ("start" and "START") wrote to what Windows' (and macOS default) case-
    insensitive filesystem treats as the *same file* -- whichever mapping
    happened to save second silently clobbered the other's class
    definition on disk, even though both were distinct, valid dict keys
    in memory. Instance names don't need this -- they're never file names,
    and Modelica identifiers are genuinely case-sensitive at the language
    level."""

    normalize = (lambda s: s.lower()) if case_insensitive else (lambda s: s)
    normalized_used = {normalize(u) for u in used}

    if normalize(name) not in normalized_used:
        used.add(name)
        return name
    suffix = 2
    while normalize(f"{name}_{suffix}") in normalized_used:
        suffix += 1
    deduped = f"{name}_{suffix}"
    used.add(deduped)
    return deduped


def _legacy_covered_concept_names(legacy_models: list[LegacyModel]) -> set[str]:
    """Every identifier already meaningfully represented inside the legacy
    code being reused -- enumeration literals (e.g. a state machine's
    `type StepState = enumeration(IDLE,FILL,...);`), declared variable
    names, and declared parameter names, all case-insensitive.

    Found live on a real dataset: extraction produced separate `Entity`
    records for a reused controller's own internal states/signals/button
    presses (already inside that controller's own enumeration/variables),
    each of which then dutifully got its own separate, EMPTY stub `.mo`
    file -- 20+ of ~48 generated files on one real run were exactly this,
    confirmed by inspecting the actual output (an `IDLE.mo` containing only
    a comment, while the reused `TankDemo_Rev12.mo` already declares
    `type StepState = enumeration(IDLE,FILL,...)`). A from-scratch stub
    whose own name matches one of these represents a concept that's
    already captured elsewhere, not a genuinely distinct component."""

    covered: set[str] = set()
    enum_pattern = re.compile(r"enumeration\s*\(([^)]*)\)")
    for legacy_model in legacy_models:
        for legacy_class in legacy_model.classes:
            for type_decl in legacy_class.type_declarations:
                for match in enum_pattern.finditer(type_decl):
                    covered.update(literal.strip() for literal in match.group(1).split(",") if literal.strip())
            covered.update(v.name for v in legacy_class.variables)
            covered.update(p.name for p in legacy_class.parameters)
    return {name.lower() for name in covered}


def _render_stub_class(
    class_name: str,
    reason: str,
    referenced_fields: dict[str, dict] | None = None,
    command_overrides: dict[str, str] | None = None,
    pending_decisions: list[dict] | None = None,
) -> str:
    """`referenced_fields` (field_name -> {"type": "Real"|"Boolean",
    "assigned": bool}) is every field some OTHER mapping's `trigger_
    variable`/`action_variable`/`control_input_variable`/
    `control_output_variable` claims to reference on THIS instance --
    found live: a from-scratch stub previously declared NOTHING, so any
    such reference produced a real, guaranteed "field not found" compile
    error, not a placeholder-value problem (`_resolve_declared_field_ref`
    only checks the INSTANCE was actually declared, never the field, by
    design -- see its own docstring). Declaring the field here at least
    keeps the class structurally real.

    An `assigned` field (the target of a real behavior/control-law
    equation) needs no equation of its own here -- that equation IS its
    governing equation. A read-only field (only ever a `trigger_variable`/
    `control_input_variable`, e.g. a sensed physical quantity this
    from-scratch stub has no real physics for) would otherwise be
    genuinely under-determined -- given the SAME propose-then-confirm
    treatment as a never-assigned legacy variable (see `_render_legacy_
    based_class`): a disclosed placeholder value, applied provisionally,
    recorded in `pending_decisions` for a human to confirm, and overridden
    by `command_overrides` (keyed `"{class_name}.{field}"`) once they do.
    """

    field_lines: list[str] = []
    placeholder_equations: list[str] = []
    for field_name, spec in sorted((referenced_fields or {}).items()):
        field_type = spec.get("type", "Real")
        field_lines.append(f"  {field_type} {field_name};")
        if spec.get("assigned"):
            continue

        override_key = f"{class_name}.{field_name}"
        default_value = "false" if field_type == "Boolean" else "0.0"
        confirmed = (command_overrides or {}).get(override_key)
        if confirmed is not None:
            placeholder_equations.append(f"  {field_name} = {confirmed};  // user-approved (sensed value for a from-scratch component)")
        else:
            if pending_decisions is not None:
                pending_decisions.append({
                    "class_name": class_name,
                    "variable": override_key,
                    "suggested_value": default_value,
                    "reason": (
                        f"'{field_name}' is read by a real behavior/control law, but this is a from-scratch "
                        "component with no derived physics -- no real measured/computed value is available yet"
                    ),
                    "grounded": False,
                })
            placeholder_equations.append(
                f"  {field_name} = {default_value};  // PROPOSED, pending confirmation -- no real physics "
                "derived yet for this from-scratch component's sensed value"
            )

    lines = [
        f"model {class_name}",
        f"  // Generated stub -- {reason}",
        "  // Behavior/equations not yet derived automatically; see README known simplifications.",
        *field_lines,
    ]
    if placeholder_equations:
        lines.append("equation")
        lines.extend(placeholder_equations)
    lines.append(f"end {class_name};")
    return "\n".join(lines) + "\n"


def _resolve_declared_field_ref(raw_ref: str | None, element_registry: dict[str, tuple[str, str]]) -> str | None:
    """`raw_ref` is "<component_id>.<field>" as the mapper wrote it --
    resolves the component id half against `element_registry` (built from
    what was ACTUALLY declared, not guessed) and returns the real
    "<instance>.<field>" reference, or None if the component id doesn't
    match anything that was actually declared. The `<field>` half is not
    independently verified (this pipeline has no per-class port/parameter
    introspection) -- an unverifiable field name fails loudly at real
    compile time (unresolved reference), which is an accepted, honest
    failure mode; a wrong INSTANCE would instead risk silently wiring the
    wrong physical thing together, which this check specifically prevents."""

    if not raw_ref or "." not in raw_ref:
        return None
    component_id, field = raw_ref.split(".", 1)
    registered = element_registry.get(component_id)
    if registered is None:
        return None
    _class_name, instance = registered
    return f"{instance}.{field}"


def _render_behavior_equation(
    mapping: ModelicaMapping, behavior: dict | None, element_registry: dict[str, tuple[str, str]]
) -> str:
    """Renders a real `when ... then ... end when;` for a trigger-based
    control behavior when every piece needed is both present and verified
    against what was actually declared -- falls back to the existing honest
    `// {reason}` comment otherwise. See `skills/modelica_modeling.py`: a
    wrong-but-confident `when` clause is worse than a disclosed gap, so
    nothing here is rendered as real code unless it checks out."""

    comment = f"  // {mapping.reason}"
    if behavior is None:
        return comment

    trigger_ref = _resolve_declared_field_ref(mapping.trigger_variable, element_registry)
    action_ref = _resolve_declared_field_ref(mapping.action_variable, element_registry)
    action_value = mapping.action_value
    operator = behavior.get("trigger_operator")
    trigger_value = behavior.get("trigger_value")

    if not (trigger_ref and action_ref and action_value is not None and operator and trigger_value is not None):
        return comment

    condition = f"{trigger_ref} {operator} {trigger_value}"
    return f"  when {condition} then\n    {action_ref} = {action_value};\n  end when;  // {mapping.reason}"


def _render_control_law_equation(
    mapping: ModelicaMapping,
    control_law: dict | None,
    element_registry: dict[str, tuple[str, str]],
    integrator_index: int,
) -> tuple[str, str | None]:
    """Renders a real equation for a continuous/proportional control law
    when every piece needed is both present and verified -- same discipline
    as `_render_behavior_equation`. Returns (equation_or_comment,
    integrator_declaration_or_None); the declaration (only for PI) must be
    emitted in the model's declaration section, before `equation`.

    PROPORTIONAL: `{output} = {gain_p} * ({input} - {setpoint});`
    PI: adds a fresh `Real controlIntegralN(start=0);` state and
    `der(controlIntegralN) = ({input} - {setpoint});` alongside the output
    equation -- a real integral action, not a fabricated placeholder.
    PID's D-term and LINEAR are not yet supported (see prompt guidance) --
    both fall back to the honest comment, same as any unresolved case."""

    comment = f"  // {mapping.reason}"
    if control_law is None:
        return comment, None

    input_ref = _resolve_declared_field_ref(mapping.control_input_variable, element_registry)
    output_ref = _resolve_declared_field_ref(mapping.control_output_variable, element_registry)
    law_type = mapping.control_law_type
    gain_p = mapping.control_gain_p
    setpoint = mapping.control_setpoint if mapping.control_setpoint is not None else 0.0

    if not (input_ref and output_ref and law_type and gain_p is not None):
        return comment, None

    error_expr = f"({input_ref} - {setpoint})"

    if law_type == "PROPORTIONAL":
        return f"  {output_ref} = {gain_p} * {error_expr};  // {mapping.reason}", None

    if law_type == "PI" and mapping.control_gain_i is not None:
        integrator_name = f"controlIntegral{integrator_index}"
        declaration = f"  Real {integrator_name}(start=0);"
        equation = (
            f"  der({integrator_name}) = {error_expr};\n"
            f"  {output_ref} = {gain_p} * {error_expr} + {mapping.control_gain_i} * {integrator_name};"
            f"  // {mapping.reason}"
        )
        return equation, declaration

    return comment, None


def generate_modelica_files(
    project_id: str,
    mappings: list[ModelicaMapping],
    legacy_comparisons: list[LegacyComparison],
    legacy_models: list[LegacyModel],
    sysml_semantic_model: SysMLSemanticModel,
    sysml_contract_raw: dict,
    engineering_id_by_sysml_element_name: dict[str, str] | None = None,
    command_overrides: dict[str, str] | None = None,
    pending_decisions: list[dict] | None = None,
    state_machines: list[dict] | None = None,
) -> tuple[dict[str, str], str, list[str], set[str]]:
    """Returns `(files, entry_class, class_names, declared_instance_names)`.
    `files` maps every generated filename (including
    `package.mo`/`package.order`) to its text.

    `sysml_contract_raw` is needed to render an actual value/unit for each
    PARAMETER mapping -- `ModelicaMapping` (`Agent Contracts.md`, Section 9)
    deliberately has no `value`/`unit` fields of its own, so the requirement
    bound is re-resolved here from the same source `mapping/property_mapper
    .py` used, rather than trying to parse it back out of `mapping.reason`.

    `engineering_id_by_sysml_element_name` (the SysML Agent's own
    traceability map, `UpstreamBundle.engineering_id_by_sysml_element_name
    ()`) is needed only for real `connect()` generation between known
    Fluid components (see `_resolve_fluid_connections`) -- optional and
    defaults to empty, since a caller with no connections to resolve (or
    every existing caller before this feature existed) doesn't need it.

    `command_overrides` (variable name -> confirmed Modelica expression) and
    `pending_decisions` (an out-parameter list this function APPENDS to,
    never replaces) implement the propose-then-confirm protocol for a
    never-assigned legacy variable that could otherwise only get an inert
    placeholder -- see `_render_legacy_based_class`. Both default to None/
    empty for every existing caller that doesn't need this (a plain
    `checkModel`-only run, or a class with no such variable at all).

    `state_machines` is a list of `StateMachine.model_dump()` dicts
    (`mapping/state_machine_synthesizer.py`'s output) -- each is matched
    against a never-assigned discrete legacy variable by its enum type and,
    if every reference in it checks out, rendered as a real transition
    chain instead of an inert placeholder or a scheduled-command pulse (see
    `_render_state_machine`). Defaults to empty for every caller that
    hasn't synthesized one (or has nothing to attach one to).
    """

    comparisons_by_element = {c.sysml_element: c for c in legacy_comparisons}
    requirements_by_id = {r["id"]: r for r in sysml_contract_raw.get("requirements", [])}
    behaviors_by_id = {b["id"]: b for b in sysml_contract_raw.get("behaviors", [])}
    control_laws_by_id = {cl["id"]: cl for cl in sysml_contract_raw.get("control_laws", [])}
    scheduled_commands = sysml_contract_raw.get("scheduled_commands", [])
    legacy_covered_names = _legacy_covered_concept_names(legacy_models)
    entry_class = _entry_class_name(project_id)

    # Every field some OTHER mapping's trigger_variable/action_variable/
    # control_input_variable/control_output_variable claims to reference,
    # grouped by the component id it's on -- computed BEFORE the main loop
    # below (which is what actually renders a from-scratch stub) so a stub
    # class can declare these fields for real instead of staying an empty
    # shell any such reference would then fail to compile against (see
    # `_render_stub_class`'s own docstring for the real bug this fixes).
    stub_field_specs: dict[str, dict[str, dict]] = {}

    def _note_field(raw_ref: str | None, field_type: str, assigned: bool) -> None:
        if not raw_ref or "." not in raw_ref:
            return
        component_id, field_name = raw_ref.split(".", 1)
        fields = stub_field_specs.setdefault(component_id, {})
        existing = fields.get(field_name)
        fields[field_name] = {
            "type": "Boolean" if field_type == "Boolean" or (existing or {}).get("type") == "Boolean" else "Real",
            "assigned": assigned or (existing or {}).get("assigned", False),
        }

    for m in mappings:
        if m.mapping_type != ModelicaMappingType.EQUATION:
            continue
        if m.sysml_element in control_laws_by_id:
            _note_field(m.control_input_variable, "Real", assigned=False)
            _note_field(m.control_output_variable, "Real", assigned=True)
        else:
            action_type = "Boolean" if isinstance(m.action_value, str) and m.action_value.strip().lower() in ("true", "false") else "Real"
            _note_field(m.trigger_variable, "Real", assigned=False)
            _note_field(m.action_variable, action_type, assigned=True)

    files: dict[str, str] = {}
    class_names: list[str] = []
    instance_records: list[dict] = []
    element_registry: dict[str, tuple[str, str]] = {}
    parameter_decls: list[str] = []
    # Also reserves every PARAMETER's readable name (see below) -- Modelica
    # parameters and component instances share ONE namespace inside a
    # single model, so a parameter named e.g. "tank1" and an instance also
    # named "tank1" would be a real duplicate-declaration error, not two
    # independent names.
    declared_instance_names: set[str] = set()
    declared_class_names: set[str] = set()
    needs_fluid_system = False
    signal_connector_instances: list[tuple[str, str]] = []
    skipped_as_already_covered: list[tuple[str, str]] = []

    for mapping in mappings:
        target = _legal_identifier(mapping.target.rsplit(".", 1)[-1]) if mapping.target else mapping.sysml_element

        if mapping.mapping_type == ModelicaMappingType.PARAMETER:
            requirement = requirements_by_id.get(mapping.sysml_element)
            # A real engineering name (e.g. "tank1Diameter" from the
            # requirement's own subject/property), not the bare fact id --
            # found live: every parameter in a generated model showed up in
            # OMEdit's variable browser as "REQ0001", "REQ0002", ...,
            # structurally fine but unreadable to an actual engineer
            # inspecting the model (see `naming.py`'s `readable_identifier`).
            # In the rare case the requirement record itself is genuinely
            # missing (so there's no subject/property to build a name
            # from), try the mapper's own rationale text next -- still
            # real, human-written text, a better name than a bare fact id
            # -- and only fall all the way back to the id if even that's
            # unusable.
            fallback_name = _readable_identifier(mapping.reason, fallback=_legal_identifier(mapping.sysml_element))
            parameter_name = _dedupe(
                _readable_identifier(
                    (requirement or {}).get("subject", ""), (requirement or {}).get("property", ""),
                    fallback=fallback_name,
                ),
                declared_instance_names,
            )
            bound_value = _requirement_bound_value(requirement) if requirement else None
            unit = _normalize_unit((requirement or {}).get("unit"))

            if bound_value is None:
                # A bare `parameter Real X;` (no value) passes the lighter
                # `checkModel()` structural check this agent runs, but real
                # Modelica *translation*/simulation (found live in OMEdit,
                # not this agent's own check -- see DECISIONS.md) requires
                # every `fixed=true` parameter (the default) to have a
                # value: "Parameter ... has neither value nor start value,
                # and is fixed during initialization." A placeholder 0.0,
                # loudly flagged in the comment, keeps the model
                # structurally simulatable without fabricating a real
                # engineering bound.
                unit_clause = f'(unit="{unit}") ' if unit else ""
                confirmed = (command_overrides or {}).get(parameter_name)
                value_str = confirmed if confirmed is not None else "0.0"
                if confirmed is None and pending_decisions is not None:
                    pending_decisions.append({
                        "class_name": entry_class,
                        "variable": parameter_name,
                        "suggested_value": "0.0",
                        "reason": f"{mapping.reason} -- no requirement bound value found for this parameter",
                        "grounded": False,
                    })
                label = "user-approved" if confirmed is not None else "PLACEHOLDER, pending confirmation: no bound value found"
                parameter_decls.append(
                    f"  parameter Real {parameter_name}{unit_clause}= {value_str};  // {mapping.reason} ({label})"
                )
            elif _is_numeric(bound_value):
                unit_clause = f'(unit="{unit}") ' if unit else ""
                parameter_decls.append(
                    f"  parameter Real {parameter_name}{unit_clause}= {bound_value};  // {mapping.reason}"
                )
            else:
                # A non-numeric bound (e.g. a named-mode description like
                # "valid START command when process is idle or paused")
                # can't be a Modelica Real -- found live on a real dataset
                # (see DECISIONS.md). String, not a fabricated number.
                escaped = bound_value.replace('"', '\\"')
                parameter_decls.append(f'  parameter String {parameter_name} = "{escaped}";  // {mapping.reason}')
            continue

        # A genuine MSL reference is a qualified path (e.g.
        # "Modelica.Fluid.Vessels.OpenTank") -- found live (see DECISIONS.md):
        # the mapper LLM tagged a legacy-reuse component as LIBRARY_COMPONENT
        # with a bare local class name ("TankDemo_Rev12") as the target,
        # which this branch then instantiated as if it were already defined
        # somewhere, without ever generating a file for it. The real compiler
        # correctly reported "Class TankDemo_Rev12 not found in scope" for
        # exactly that dangling instantiation. Anything not shaped like a
        # real MSL path falls through to the MODEL/BLOCK handling below
        # instead, which actually generates (or reuses) a class for it --
        # never instantiate a type without ensuring it gets defined.
        if mapping.mapping_type == ModelicaMappingType.LIBRARY_COMPONENT and "." in mapping.target:
            instance = _dedupe(_instance_name(target), declared_instance_names)
            modifiers = _default_modifiers(mapping.target)
            comment = mapping.reason
            placeholder_params = _LIBRARY_CLASS_PLACEHOLDER_PARAMETERS.get(mapping.target)
            if placeholder_params:
                placeholder_names = {p.split("=", 1)[0].strip() for p in placeholder_params}
                modifiers = _apply_parameter_overrides(
                    instance, modifiers, placeholder_names, command_overrides or {}, pending_decisions,
                    mapping.target, f"{mapping.target} ({mapping.reason})",
                )
                comment += f" (placeholder values, proposed pending confirmation: {', '.join(sorted(placeholder_names))})"
            instance_records.append(
                {"target": mapping.target, "instance": instance, "modifiers": modifiers, "comment": comment}
            )
            element_registry[mapping.sysml_element] = (mapping.target, instance)
            if mapping.target.startswith("Modelica.Fluid."):
                needs_fluid_system = True
            if mapping.target in _BARE_SIGNAL_CONNECTOR_DEFAULTS:
                signal_connector_instances.append((mapping.target, instance))
            continue

        if mapping.mapping_type in (ModelicaMappingType.MODEL, ModelicaMappingType.BLOCK, ModelicaMappingType.LIBRARY_COMPONENT):
            comparison = comparisons_by_element.get(mapping.sysml_element)

            # This specific element has no legacy reuse of its OWN, but its
            # name matches a concept (an enum literal, a variable, a
            # parameter) already declared inside legacy code this run is
            # already reusing elsewhere -- skip the redundant empty stub
            # rather than generate a separate, disconnected file for a
            # state/signal/sensor mention that's already represented.
            if comparison is None and target.lower() in legacy_covered_names:
                skipped_as_already_covered.append((mapping.sysml_element, target))
                continue

            class_name = _dedupe(target, declared_class_names, case_insensitive=True)
            if comparison is not None and comparison.recommendation.value != "REPLACE":
                legacy_class = _find_legacy_class(mapping.sysml_element, comparison.legacy_class, legacy_models)
                if legacy_class is not None:
                    files[f"{class_name}.mo"] = _render_legacy_based_class(
                        class_name, legacy_class, comparison.overrides,
                        scheduled_commands, command_overrides, pending_decisions,
                        state_machines, behaviors_by_id, requirements_by_id,
                    )
                    class_names.append(class_name)
                    instance = _dedupe(_instance_name(class_name), declared_instance_names)
                    instance_records.append({
                        "target": class_name, "instance": instance, "modifiers": [],
                        "comment": f"reused from legacy: {comparison.legacy_class} ({comparison.legacy_file})",
                    })
                    element_registry[mapping.sysml_element] = (class_name, instance)
                    continue

            files[f"{class_name}.mo"] = _render_stub_class(
                class_name, f"mapped from '{mapping.sysml_element}': {mapping.reason}",
                stub_field_specs.get(mapping.sysml_element), command_overrides, pending_decisions,
            )
            class_names.append(class_name)
            instance = _dedupe(_instance_name(class_name), declared_instance_names)
            instance_records.append({"target": class_name, "instance": instance, "modifiers": [], "comment": None})
            element_registry[mapping.sysml_element] = (class_name, instance)
            continue

        # EQUATION / ALGORITHM / ASSERTION / CONNECTOR mappings don't get their
        # own file -- they contribute to the entry class body instead.

    # Always resolved, not only when there are SysML connections to map --
    # a two-port Fluid instance with *no* connection at all still has two
    # always-present, structurally unconnected ports that need a boundary
    # condition just as much as one with only one port wired.
    connect_lines, extra_records = _resolve_fluid_connections(
        sysml_semantic_model, engineering_id_by_sysml_element_name or {}, element_registry, instance_records,
        command_overrides, pending_decisions,
    )
    instance_records.extend(extra_records)

    # Same idea, generalized to the potential-based domains -- one call per
    # domain, since a shared reference in one has no meaning in the other
    # (see `_resolve_potential_connections`'s own docstring for why this
    # is genuinely a different strategy from Fluid's, not just more data).
    for two_port_classes, reference_class, reference_port in (
        (_ELECTRICAL_TWO_PORT_CLASSES, _ELECTRICAL_REFERENCE_CLASS, _ELECTRICAL_REFERENCE_PORT),
        (_MAGNETIC_TWO_PORT_CLASSES, _MAGNETIC_REFERENCE_CLASS, _MAGNETIC_REFERENCE_PORT),
    ):
        potential_connect_lines, potential_extra_records = _resolve_potential_connections(
            sysml_semantic_model, engineering_id_by_sysml_element_name or {}, element_registry,
            two_port_classes, reference_class, reference_port,
        )
        connect_lines.extend(potential_connect_lines)
        instance_records.extend(potential_extra_records)

    instance_decls = [
        f"  {r['target']} {r['instance']}"
        + (f"({', '.join(r['modifiers'])})" if r["modifiers"] else "")
        + ";"
        + (f"  // {r['comment']}" if r["comment"] else "")
        for r in instance_records
    ]

    if needs_fluid_system:
        # Any `Modelica.Fluid.*` component uses an `outer system` reference
        # for ambient conditions/flow-model defaults -- without a matching
        # `inner` component, translation only emits a warning and silently
        # auto-generates one (found live in OMEdit, not this agent's own
        # `checkModel()`-based check -- see DECISIONS.md). Declaring it
        # explicitly here doesn't rely on that IDE-only fallback, which a
        # headless `simulate()` call (e.g. the Compiler Agent) may not
        # perform the same way.
        instance_decls.insert(0, "  inner Modelica.Fluid.System system;")

    connection_comments = [
        f"  // connect: {c.source_instance} -> {c.target_instance}"
        + (f"  ({c.relationship_type})" if c.relationship_type else "")
        for c in sysml_semantic_model.connections
    ]

    equation_lines: list[str] = []
    control_law_declarations: list[str] = []
    integrator_index = 0
    for m in mappings:
        if m.mapping_type != ModelicaMappingType.EQUATION:
            continue
        if m.sysml_element in control_laws_by_id:
            integrator_index += 1
            line, declaration = _render_control_law_equation(
                m, control_laws_by_id.get(m.sysml_element), element_registry, integrator_index
            )
            if declaration:
                control_law_declarations.append(declaration)
        else:
            line = _render_behavior_equation(m, behaviors_by_id.get(m.sysml_element), element_registry)
        equation_lines.append(line)
    # A bare signal-connector instance (see `_BARE_SIGNAL_CONNECTOR_
    # DEFAULTS`) has nothing feeding it a value -- this pipeline doesn't
    # wire signal-level connect()s (only the known Fluid port family, see
    # `_resolve_fluid_connections`), so any such instance is unconditionally
    # left undetermined otherwise.
    equation_lines.extend(
        f"  {instance} = {_BARE_SIGNAL_CONNECTOR_DEFAULTS[target]};"
        f"  // PLACEHOLDER: bare signal connector, nothing drives it"
        for target, instance in signal_connector_instances
    )
    assertion_lines = [
        f"  // assert-candidate: {m.sysml_element} -- {m.reason}"
        for m in mappings
        if m.mapping_type == ModelicaMappingType.ASSERTION
    ]

    entry_lines = [f"model {entry_class}"]
    entry_lines.extend(
        f"  // {sysml_element} ('{target}') not separately instantiated -- already represented "
        f"inside a reused legacy class (matching enum literal/variable/parameter name)."
        for sysml_element, target in skipped_as_already_covered
    )
    entry_lines.extend(parameter_decls)
    entry_lines.extend(instance_decls)
    entry_lines.extend(control_law_declarations)
    if connection_comments or connect_lines or equation_lines or assertion_lines:
        entry_lines.append("equation")
        entry_lines.extend(connection_comments)
        entry_lines.extend(connect_lines)
        entry_lines.extend(equation_lines)
        entry_lines.extend(assertion_lines)
    entry_lines.append(f"end {entry_class};")
    files[f"{entry_class}.mo"] = "\n".join(entry_lines) + "\n"
    class_names.append(entry_class)

    package_name = _legal_identifier(project_id, fallback="Project")
    files["package.mo"] = f"package {package_name}\nend {package_name};\n"
    files["package.order"] = "\n".join(class_names) + "\n"

    return files, entry_class, class_names, declared_instance_names
