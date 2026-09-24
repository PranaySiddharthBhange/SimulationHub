"""General engineering-domain knowledge, appended to Stage 2/3's prompts for
whichever domain(s) `contracts.Understanding.domains` names (see
`prompts.merge_notes.MERGE_PROMPT`, which asks the merge call to pick from
`DOMAIN_SKILLS`'s keys).

This is domain knowledge, not problem knowledge: standard equations and
modeling conventions that hold for every system of that kind, written with
NO entity names, ids, or numeric values from any specific problem -- the
exact same discipline `prompts/common.py` and every `skills/stage*.py` file
already hold to, and for the same reason: a concrete example name or value
sitting in a shared prompt has twice now been confirmed to leak verbatim
into an unrelated problem's fabricated output when the model lacked real
signal (see `skills/stage1_understanding.py`'s own note on this). Domain
knowledge is safe to share broadly precisely because it stays general.

A real, confirmed gap this closes: run live against the actual magnetic-
circuit dataset in `test_cases/`, the local model correctly stopped
inventing entities once the CSV-chunking header-loss bug was fixed (see
`reasoner_pipeline._chunk_source_text`), but still mislabeled `H_gap_A_m`
(magnetic field strength, A/m) as "Henry value" -- a plausible-sounding but
wrong unit guess a model without real magnetics grounding will keep making.
Generic domain knowledge on hand at generation time is a direct fix for
exactly that class of mistake, distinct from -- and layered on top of --
the "don't fabricate when signal is sparse" discipline everywhere else.

Classification happens ONCE, in Merge (the first point in the pipeline
with a full, cross-document view of the whole system -- Stage 1 reads one
document/chunk at a time and could not classify reliably). Stage 1 itself
gets no domain skill text for that reason; the gap is architectural, not
an oversight -- there IS no known domain before Stage 1 has produced
something Merge can read.

Add a new domain by adding one entry here; nothing else needs to change --
an unrecognized or absent domain key already degrades to "no extra skill
text," never an error.
"""

DOMAIN_SKILLS: dict[str, str] = {
    "fluid_level_and_flow": """\
Fluid level & flow systems (tanks, vessels, valves, pipes, pumps):
- Level dynamics come from a volume (or mass) balance on each vessel, not from
  guessing a fill rate directly: A * dh/dt = Q_in - Q_out, where A is the
  vessel's cross-sectional area at that level (constant for a straight-walled
  tank). Never write dh/dt = Q directly without dividing by area/volume.
- An on/off (isolating) valve's flow is typically either a fixed nominal rate
  while open (0 while closed) if that's what the source gives, or an orifice-
  type relation Q = Cv * sqrt(deltaP) when a valve coefficient and pressure
  drop are actually given -- use whichever the source actually specifies,
  never invent a Cv or pressure drop that wasn't given.
- A flow that should physically stop at a limit (empty vessel, closed valve, a
  level crossing a threshold) needs a real state event on that comparison when
  the limit is a stated setpoint or is used in a transition guard, so the
  solver locates the crossing and the quantity settles exactly at the limit
  rather than a whole step beyond it. `noEvent()` suppresses that location and
  is only appropriate for a boundary whose exact crossing does not matter --
  see `skills/stage3_modelica.py`'s own event-semantics notes for both the
  chattering and the overshoot failure modes this trades between.
- Distinguish level (a length, e.g. m) from volume (m^3) from stored mass
  (kg, = density * volume) -- a source may state a "level limit" that is
  really a volume or mass limit in disguise; convert consistently, don't mix
  units across an equation.""",

    "magnetic_circuit": """\
Magnetic circuits (cores, air gaps, windings, flux paths):
- The magnetic-circuit analogue of Ohm's law: magnetomotive force
  MMF = N * I (ampere-turns, At) drives flux Phi through a reluctance R:
  MMF = Phi * R. Reluctance of a path segment is R = length / (permeability *
  cross_sectional_area); an air gap's reluctance normally dominates the total
  because its permeability is mu_0, orders of magnitude below any core
  material's permeability -- do not treat gap and core reluctance as
  comparable unless the source explicitly gives values that show otherwise.
- Flux density B = Phi / area; magnetic field strength H = B / permeability
  (or H = MMF_drop / path_length for a segment) -- H's SI unit is A/m
  (ampere-turns per metre), NOT Henries (that's inductance, a different
  quantity entirely -- a common mislabeling to avoid).
- A winding's induced voltage follows Faraday's law: U = N * dPhi/dt (or its
  RMS-phasor form for a sinusoidal steady state: |U| = 2*pi*f*N*|Phi|) --
  induced voltage comes from the RATE OF CHANGE of flux linkage, never from
  flux magnitude alone.
- Leakage flux is the portion that does NOT cross the working air gap or
  reach the intended path; a real circuit's useful flux and leakage flux are
  usually reported separately and must not be summed or substituted for one
  another without the source saying so.
- Reluctances in SERIES carry the same flux and their MMF drops add;
  reluctances in PARALLEL share the same MMF drop and their fluxes add. So a
  source that states a leakage FACTOR (the fraction of total flux that leaks,
  or equivalently the fraction that is useful) has already fixed the ratio of
  the two parallel branch reluctances: with leakage fraction s, the leakage and
  useful branches satisfy R_leak = R_useful * (1 - s) / s. Derive the branch
  from the stated factor this way rather than inventing a geometric leakage
  path the source never described.
- Getting the series/parallel TOPOLOGY right is the whole model in this domain.
  Place each segment either before the branch point or inside one branch --
  never between the two branch nodes, which silently creates an extra parallel
  path. Check the split numerically before accepting the circuit: the flux
  entering a junction must equal the sum of the fluxes leaving it, and that
  identity is the fastest way to catch a mis-wired branch.""",

    "thermal": """\
Thermal / heat-transfer systems (thermal masses, heaters, heat exchange):
- A lumped thermal mass's temperature obeys an energy balance, not a bare
  rate: m * cp * dT/dt = Q_in - Q_out, where m is mass (kg) and cp is
  specific heat capacity (J/(kg*K)) -- never write dT/dt = Q directly.
- Heat loss to an ambient/surroundings is usually modeled as proportional to
  the temperature difference (Newton's law of cooling): Q_loss = h * A *
  (T - T_ambient), or as a single lumped thermal conductance/resistance
  (Q_loss = (T - T_ambient) / R_thermal) when the source gives a conductance
  or resistance value instead of h and A separately -- use whichever form the
  source's actual given quantities support.
- A fixed-power heat source contributes a constant Q_in only while active;
  do not conflate the heater's rated power with the resulting temperature
  rate without dividing by the thermal mass's m*cp.
- Distinguish sensible heat (temperature change, m*cp*dT) from latent heat
  (phase change at constant temperature, m*L using the latent heat of
  vaporization/fusion L) -- a process that evaporates or condenses a fluid
  needs the latent term; using only m*cp*dT for a phase-change step silently
  drops the dominant energy term.""",

    "species_concentration_balance": """\
Well-mixed species / concentration balance (a substance diluted, generated,
or removed inside a well-mixed volume -- e.g. a gas species in a room, a
dissolved solute in a stirred vessel):
- The governing equation is a mass balance on the species inside the well-
  mixed volume: V * dC/dt = generation_rate + inflow_rate * C_in -
  outflow_rate * C, where V is the volume, C is the well-mixed (and
  therefore also outlet) concentration, and C_in is the concentration of
  whatever is flowing in (e.g. outdoor air's background level). "Well-mixed"
  specifically means the outlet concentration equals the bulk concentration
  C, not some other value -- do not introduce a separate outlet-concentration
  variable unless the source describes actual internal stratification.
  Consistent units matter here (a generation rate in kg/s, ppm/s and a
  concentration in kg/m^3, ppm are NOT interchangeable without an explicit
  conversion the source provides or that is a standard physical constant).
- A feedback controller that modulates a flow based on a measured
  concentration is a closed loop: the controlled variable (flow) affects the
  measured variable (concentration) which affects the controller's next
  command -- keep this causality explicit rather than modeling the flow as
  independently scheduled once feedback control is stated.
- Generation proportional to a scheduled quantity (e.g. occupant count) is a
  piecewise/time-varying source term, not a constant -- honor the schedule's
  actual steps rather than averaging it into one constant rate.""",

    "multiphase_mixture_process": """\
Multi-component liquid mixtures with composition-dependent properties (a
solute dissolved or suspended in a solvent, tracked through vessels that can
also evaporate/condense that solvent):
- A vessel's real state is mass m, internal energy U, and composition (mass
  fraction(s) Xi of each species) -- NOT level alone. Level is a DERIVED
  quantity (from volume, area, and density), not a primary state, once
  density depends on temperature and composition. Balances: der(m) = net
  mass flow in/out; der(U) = net enthalpy flow in/out (include a -p*der(V)
  term for a compressible formulation, or omit it for an incompressible one
  -- state which you used and why); der(m*Xi) = net species mass flow
  in/out, one equation per independent species tracked.
- Density, enthalpy, heat capacity, saturation pressure, and viscosity of a
  composition-dependent mixture are functions of temperature, pressure, AND
  composition -- rho(T,p,w), h(T,p,w), cp(T,w), etc. -- never assume they
  equal the pure solvent's constant property once composition varies
  meaningfully. Use whatever correlation the brief actually supplies; if it
  gives a correlation with some coefficients explicitly missing, that is a
  real gap to flag as an assumption or question, never a license to invent
  plausible-looking coefficients to complete it.
- Evaporation/condensation is driven by the LATENT heat imbalance, not
  temperature alone: a phase-change mass rate follows from dividing the heat
  flow in excess of what's needed for sensible heating/cooling by the
  (composition-dependent) enthalpy of vaporization -- m_phase_change =
  heat_imbalance / (h_vapor - h_liquid + sensible-correction terms), never a
  bare heat/temperature ratio. Guard the onset of phase change against
  chattering the same way a physical-limit flow cutoff needs `noEvent()`
  elsewhere: suppress the phase-change term while the driving heat flow is
  still below whatever threshold marks the real onset, rather than letting a
  boundary condition toggle every solver iteration.
- A connection port that can physically sit above OR below the liquid
  surface needs asymmetric flow resistance, not one fixed loss factor:
  strongly restrict (near-block) outflow attempted through a port that's
  above the current liquid level, allow inflow through it far more easily,
  and apply hysteresis around the exact level-crossing point so the model
  doesn't chatter as the level oscillates near a port's elevation.""",

    "batch_sequential_process": """\
Batch / sequential process control (staged operations moving between
vessels or units, each stage gated by a completion condition):
- Model the sequence as an explicit discrete state machine: one state per
  named process stage, with guarded transitions whose conditions are exactly
  the stated completion conditions (a level reaching a setpoint, a
  concentration reaching a target, an elapsed-time threshold) -- never
  collapse a multi-stage sequence into a single continuous behavior or drop
  a stage's own completion condition in favor of a fixed duration that
  wasn't actually given.
- A programmable controller is a SAMPLED device: it scans its inputs on a
  fixed cycle and acts on the values it latched, rather than reacting to a
  continuous signal the instant it crosses a threshold. Model it that way --
  sample the operator commands and measurements on the controller's scan
  period and derive one-shot edges from the sampled values. Clocking the
  logic this way is what keeps the discrete equations well-ordered: it is the
  standard remedy for a discrete dependency cycle (an unsolvable "purely
  discrete algebraic loop"), because every discrete value in a scan is
  computed from the previous scan's latched values rather than from another
  value being decided in the same instant. It also matches the real device,
  so the scan period is a genuine modeling parameter rather than a numerical
  trick.
- A stage timer is a quantity that accumulates only while its stage is
  active. Represent it as a state whose rate is one during that stage and
  zero elsewhere, set to its starting value at the moment the stage is
  entered. Where a pause must freeze a timer and a later resume must continue
  from the remaining time rather than restart it, store that remaining time
  when the pause happens and restore it on entry after the resume.
- A stage that runs two branches that must BOTH finish before the sequence
  can proceed (a parallel split/join) needs both branches' own completion
  conditions tracked and ANDed together, not just the first branch to finish.
- Each stage typically has its own governing physics (a fill obeys a volume
  balance, an evaporation stage obeys a mass+energy balance with a latent-
  heat term, a cooling stage obeys a heat-transfer balance) -- reuse the
  matching physical domain's equations for whichever operation is active in
  a given stage, rather than one generic equation across all stages.
- Automated on/off valves in this class of system commonly have a stated
  fail-safe position (e.g. fail closed) -- that is a safety requirement on
  the valve's behavior during a fault/de-energized condition, separate from
  its commanded open/close logic during normal sequencing; both must be
  represented if the source states a fail-safe requirement.""",

    "electrical_circuit": """\
Electrical circuits (resistive/inductive/capacitive networks):
- Kirchhoff's current law: the sum of currents into any node is zero.
  Kirchhoff's voltage law: the sum of voltage drops around any closed loop
  is zero. Use these to derive a circuit's governing equations rather than
  guessing a lumped relation directly.
- Component laws: resistor V = I*R; capacitor I = C*dV/dt; inductor
  V = L*dI/dt. A circuit with capacitors/inductors is a dynamic (ODE)
  system, not an instantaneous algebraic one -- its state (capacitor
  voltages, inductor currents) must be given real initial conditions.
- Real (instantaneous) power P = V*I for DC; for sinusoidal AC, distinguish
  real power (P = V_rms*I_rms*cos(phi)), reactive power, and apparent power
  -- do not treat RMS magnitudes as if they were DC values when phase
  matters to the question being asked.""",

    "mechanical_dynamics": """\
Mechanical dynamics (masses, springs, dampers, rotating/translating bodies):
- Newton's second law is the governing equation for translational motion:
  m * a = sum of forces (m * d2x/dt2 = F_net); for rotation, the analogue is
  J * alpha = sum of torques (J * d2theta/dt2 = tau_net), where J is the
  moment of inertia about the rotation axis.
- A spring contributes a force proportional to displacement from its
  unstretched/equilibrium position (F = -k * (x - x0)), never proportional
  to absolute position unless x0 = 0 is actually the equilibrium; a damper
  contributes a force proportional to velocity (F = -c * dx/dt). Both are
  restoring/dissipative and oppose the motion that generates them.
- Position and velocity are genuinely independent state variables (velocity
  is the derivative of position, not a separately-integrated quantity) --
  give both real, consistent initial conditions rather than deriving one
  from the other at the start of the simulation.""",
}


def domain_catalogue() -> str:
    """One line per domain: its key and what it actually covers.

    Merge chooses `Understanding.domains` from this list, and it used to see
    only the bare keys. A key is not self-describing -- confirmed live: an
    evaporation plant that boils water out of a brine was classified into the
    level, thermal, species and batch domains but NOT the phase-change one,
    whose key reads as an abstract category while its text describes exactly
    that plant. Choosing physics from identifiers alone loses whichever domain
    happens to be named least literally, so the description travels with the
    key instead of being duplicated in the prompt.
    """

    lines = []
    for key, text in DOMAIN_SKILLS.items():
        # Every skill opens with a one-sentence scope ending in a colon.
        lead = text.split(":\n", 1)[0].replace("\n", " ")
        lines.append(f"- {key}: {' '.join(lead.split())}")
    return "\n".join(lines)


def domain_skill_block(domains: list[str]) -> str:
    """Concatenates the known skills among `domains`, in a section clearly
    marked as general knowledge (never problem-specific instruction) so it
    reads as engineering background, not as new requirements to satisfy.
    Unknown/unrecognized keys are silently skipped -- an unfamiliar or
    absent domain degrades to no extra text, never an error, matching how
    `clarify=None` degrades Stage 2's human-in-the-loop step elsewhere."""

    matched = [DOMAIN_SKILLS[d] for d in domains if d in DOMAIN_SKILLS]
    if not matched:
        return ""
    body = "\n\n".join(matched)
    return (
        "\n\nDOMAIN BACKGROUND (general engineering knowledge for this system's domain -- "
        "apply it where relevant, but the brief's own stated values and structure always take "
        "precedence over anything below):\n\n" + body
    )
