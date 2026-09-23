"""Stage 3: Modelica generation. Extends `prompts.common.COMMON` with the
Modelica-specific authoring order and a conservative event-semantics checklist.
Some rules address compiler failures; others address behavioral risks that only
trajectory inspection can reveal.
"""

from simulation_platform.prompts.common import COMMON

MODELICA = COMMON + """
Stage 3: use the concise SysML flow and the full engineering brief to create a
MULTI-FILE Modelica bundle built from the verified Modelica Standard Library catalog
appended to this prompt. The output must be easy to inspect in OMEdit as a component
diagram as well as executable by OpenModelica.

Return an `entry_class` and an ordered `files` list. Put one meaningful physical or
control unit in each component file and the connected experiment in exactly one
`role="system"` file, last in load order. Use at least two files, and keep distinct physical or control units in separately inspectable files when the brief identifies them. Do not hide every helper as a nested class in one giant file. Every file must contain one complete top-level Modelica class whose name matches its filename. Do not generate `package.mo` because this pipeline loads a flat bundle.

Instantiate real, fully-qualified Modelica Standard Library components from the provided catalog when their semantics match the brief, and list every class actually used in `library_components`. Add icon and placement/connection annotations for reusable components and the system diagram when they improve OMEdit inspection; annotations must never replace real equations or connections. The system file must include an experiment annotation matching the confirmed simulation settings. Custom equations and a custom controller are allowed where no catalog component faithfully expresses the specified physics or pause/resume semantics.

Build from real Standard Library components wherever the library provides the
element the brief names, and write a custom class only for behaviour it does
not -- usually just the sequence controller. A library component arrives with
its icon, connectors and diagram graphics already defined, so the diagram is
readable in OMEdit with no drawing work, and an acausal physical network solves
its own flows instead of relying on a hand-built signal chain that can close
into an algebraic loop. Hand-rolled replacements for classes the library
already has are the main reason a generated diagram comes out as blank boxes.

When a library class needs a parameter the brief does not state (a medium, a
nominal pressure drop, a port height), choose it so the component reproduces
the behaviour the brief DOES state, and record that in `corrections` as an
explicit assumption. The brief's own rates, levels, thresholds and timings
still govern and must be reproduced. Never replace a physical network with
unconnected decorative icons.

The pipeline may make repair attempts against a REAL compiler and full scenario, but return the best complete bundle on every attempt. Apply Modelica semantics rigorously and check the equations and event behavior before returning; do not rely on a later repair attempt to discover an avoidable mistake.

CONNECTOR DISCIPLINE -- check this before returning any bundle:
- Every operand passed to `connect(a, b)` must be a real connector declared with
  a connector class such as `Modelica.Blocks.Interfaces.BooleanInput`,
  `BooleanOutput`, `RealInput`, or `RealOutput`, or a connector member of a
  component instance.
- A plain `Boolean`, `Real`, or `Integer` variable is never a connector. Do not
  write `connect(controller.startCmd, startCmd)` when `startCmd` was declared as
  `Boolean startCmd;`. Use an equation such as `controller.startCmd = startCmd;`,
  or model the source itself with a proper output connector.
- Audit both operands of every `connect(...)` against their declarations. This
  applies to command pulses, sensor values, schedules, and physical quantities;
  graphical annotations do not turn an ordinary scalar into a connector.

COMPONENT DIAGRAM -- the bundle is opened and read in OMEdit, so the system
file's diagram layer must show the real plant, not a block box. Judge your own
output by this: someone who knows the process should recognise it from the
diagram alone, and be able to trace the material path and every control signal.

- USE THE LIBRARY COMPONENT WHEREVER ONE EXISTS. A Standard Library class
  arrives with its icon, its connectors and its graphics already defined, so
  instantiating it is what makes the diagram look like the real plant with no
  drawing work at all. Reach for a custom class only for behaviour the library
  genuinely does not provide -- typically just the sequence controller.
- ONE INSTANCE PER NAMED PHYSICAL UNIT. If the brief names several vessels,
  valves, sources or sinks, each one is its own component INSTANCE in the
  system diagram. Never aggregate them into a single combined plant/process
  class -- a class holding every vessel and every valve at once collapses the
  whole diagram to one featureless rectangle and is a failed deliverable even
  when it simulates perfectly.
- WHERE A CUSTOM CLASS IS UNAVOIDABLE, make it reusable: write ONE class and
  instantiate it once per unit with that unit's own parameters, rather than a
  near-duplicate class per instance.
- INCLUDE THE BOUNDARIES. A supply source or receiving drain/sink the brief
  names is a real component in the diagram, not an implicit constant.
- CONNECT THE MATERIAL PATH IN ONE DIRECTION. The components must be wired in
  the same sequence the brief's topology states, so the diagram reproduces the
  process flow end to end. In a signal-flow model that chain runs one way:
  each element passes its flow DOWNSTREAM only. Never also wire the downstream
  unit's value back into the element that feeds it -- two components connected
  both ways with nothing in between form an algebraic loop, and the solver is
  free to satisfy it with every signal stuck at zero, which compiles, simulates
  and reports success while the process does nothing at all. A unit that must
  limit an incoming or outgoing flow to its own available inventory does that
  INSIDE its own equations, from its own state; it does not send a correction
  back upstream. The only long loop is the control loop, and that one runs
  through the controller. Lay them out left-to-right (or top-to-bottom) along that
  path, with the controller set apart and its signal lines running to the
  actuators it commands and back from the measurements it reads.
- EVERY `connect(...)` IN THE SYSTEM FILE CARRIES A LINE ANNOTATION:
  `connect(a.y, b.u) annotation(Line(points={{x1,y1},{x2,y2}}, color={0,0,127}));`
  Route the points around components rather than through them. Use the standard
  signal colours: Real {0,0,127}, Boolean {255,0,255}, Integer {255,127,0}, and
  a physical/material path {0,127,255}. Without these, the tool has nothing to
  draw and the diagram degenerates into overlapping straight lines.
- EVERY CONNECTOR ON EVERY PLACED COMPONENT IS DRIVEN OR CONSUMED. An
  unconnected Modelica input silently defaults to ZERO -- the model still
  compiles, still simulates, still reports success, and the signal path it
  belongs to simply carries nothing for the whole run. Declare only the ports
  you actually wire, and wire every port you declare. Before returning, walk
  each component's connectors and confirm each one appears in a `connect(...)`
  or is given a value by an equation in the system model.

- EVERY CONNECTOR DECLARATION CARRIES A `Placement` on its class boundary, so
  connections attach where they should: inputs on the left edge (x from -120 to
  -100), outputs on the right edge (x from 100 to 120), and spread along y so
  they do not overlap.
- EVERY CUSTOM CLASS CARRIES AN `Icon(graphics={...})` THAT LOOKS LIKE THE REAL
  THING, not a plain box: a vessel as a rectangle with a partial fill rectangle
  and its level text; an on/off valve as two opposed triangles meeting at a
  point; a boundary source or sink as an ellipse; a controller as a block with
  its port names as Text. Add `Text(extent={{-100,100},{100,140}},
  textString="%name")` so each instance shows its own name. Keep the icon
  inside the standard -100..100 coordinate system.

MODELICA LANGUAGE HARD RULES -- each of these has cost a full repair loop,
because the compiler's own message for it names the wrong token, the wrong
file, or nothing at all. Check every one before returning a bundle:

- RESERVED WORDS. These are keywords and can NEVER be used as the name of a
  variable, parameter, component, connector, or class:
  algorithm and annotation block break class connect connector constant
  constrainedby der discrete each else elseif elsewhen encapsulated end
  enumeration equation expandable extends external false final flow for
  function if import impure in initial inner input loop model not operator or
  outer output package parameter partial protected public pure record
  redeclare replaceable return stream then true type when while within
  The dangerous ones in physical modelling are `flow`, `input`, `output`,
  `stream`, `initial`, `der`, `connector`, `type`, `operator`, `in`, `end` and
  `constant`, because they read as natural names for real quantities. Write
  `volumeFlow`, `massFlow`, `qOut`, `cmdIn`, `levelOut` -- never `flow`.
  Do not declare `time` either; it is the built-in independent variable.
  This mistake surfaces as `No viable alternative near token: <the PRECEDING
  token>`, so a parse error naming a token that looks perfectly correct means
  you should inspect the IDENTIFIER that follows it, not the token named.

- BUILT-IN OPERATORS ONLY. Use only operators that really exist: der, pre,
  initial, terminal, sample, edge, change, reinit, delay, noEvent, smooth,
  abs, sign, sqrt, min, max, div, mod, rem, ceil, floor, integer, semiLinear,
  homotopy, and the standard math functions. Never invent one (`sampleEnterTime`,
  `stateTime`, `elapsed` and similar do not exist). If you need the time a state
  was entered, store it yourself: `when <entry condition> then tEnter := time; end when;`
  with `discrete Real tEnter`.

- WRITE THE MODE MACHINE IN AN `algorithm` SECTION. A discrete sequence
  controller belongs in `algorithm ... when {...} then ... := ...; end when;`.
  An if/elseif chain there may legally omit the final `else`, and unassigned
  variables simply hold their previous value. The same chain in an EQUATION
  section is illegal unless every branch -- including a mandatory `else` --
  assigns exactly the SAME set of left-hand-side variables; omitting the
  `else` gives `The branches of an if-equation inside a when-equation must
  have the same set of component references on the left-hand side`. Use the
  algorithm form and avoid the whole class.

- SAMPLE A CONTROLLER'S COMMANDS ON ITS SCAN CYCLE. A programmable controller
  latches its inputs on a fixed scan period, so model it that way rather than
  reacting to continuous signals instantaneously:
  ```
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  startSample = sample(0, scanPeriod) and startButton;
  startPulse  = edge(startSample);
  ```
  This is the primary structural remedy for `Purely discrete algebraic loops
  cannot be solved by iterative processes`: inside one scan every discrete
  value is computed from values latched in the previous scan, so the discrete
  equations are well-ordered by construction instead of depending on each
  other in the same instant. It also matches the real device, so the scan
  period is a genuine modeling parameter. Take the period from the brief when
  it states one; otherwise choose one and record it in `corrections`.
  Sampling costs response latency: a command arriving at t is acted on at the
  next scan tick, up to one period later. Size the period against the TIMING
  TOLERANCE the acceptance checks demand, not merely against the stated
  durations -- if a check requires an action at an exact instant, a 0.1 s scan
  that responds at t+0.1 s fails it. When the brief demands exact event
  instants, capture the operator command edges as real events and clock only
  the internal sequencing, or make the period small enough that the latency is
  inside the stated tolerance.

- `reinit` IS ALLOWED, IN ONE SPECIFIC SHAPE. It sets a continuous state to a
  new value at an event, and OpenModelica accepts it only inside a `when` in
  an EQUATION section. It fails (`Internal error BackendDAECreate.lowerWhenEqn:
  equation not handled`) when it shares a when-branch with ordinary
  assignments. So give each reset its OWN `when`, containing nothing but the
  `reinit`, and keep the mode dispatcher in a separate `algorithm` section:
  ```
  der(waitTimer) = if inWaitState then 1.0 else 0.0;

  when mode == State.WAIT_AFTER_FILL and pre(mode) <> State.WAIT_AFTER_FILL then
    reinit(waitTimer, waitAfterFill - pre(storedWaitRemaining));
  end when;
  ```
  A timer built this way accumulates only while its stage is active, starts
  from the stored remaining time on a resume, and needs no `pre()` gymnastics.

  The state-free alternative is `discrete Real tEnter` set to `time` on entry
  with `waitElapsed = time - pre(tEnter);`. If you use that form, THE `pre(...)`
  IS MANDATORY: `tEnter` is assigned by the same `when` whose trigger reads
  `waitElapsed`, so the plain `time - tEnter` makes the timer depend on the
  transition that sets it. Verified against the real compiler -- the plain form
  translates, builds and simulates with no error at all, yet `tEnter` never
  updates from its start value, so every timed transition after the first
  silently never fires and the controller sits in one state to the end of the
  horizon.

- NO EMPTY ARRAY CONSTRUCTORS. `{}` is not valid Modelica. Write
  `annotation(Icon())` or omit the attribute; never `graphics={}`, `points={}`
  or `table={}`. Annotations are cosmetic: a missing annotation costs nothing,
  a malformed one fails the whole file. Prefer fewer, simpler annotations.

- NO PURELY DISCRETE ALGEBRAIC LOOPS. Inside a `when` that assigns a discrete
  variable, every read of that same variable (and of anything derived from it)
  must go through `pre(...)`. Never write a trigger condition such as
  `mode == Running and level >= high` for a `when` whose body assigns `mode` --
  write `pre(mode) == Running and level >= high`. Equally, never define two
  discrete variables in terms of each other's current values (for example
  `shutActive = ... and not shutDone;` together with `shutDone = shutActive
  and ...;`). This failure appears as `Internal error ... analyseStrongComponentBlock
  failed (Purely discrete algebraic loops cannot be solved by iterative
  processes)` with source locations inside the COMPILER's own files, which say
  nothing about where your mistake is.

- BALANCE EQUATIONS AND UNKNOWNS. Before returning, count them per class: every
  non-parameter, non-constant variable you declare needs exactly one equation
  (a `der(...)` equation counts for its state; a variable assigned only inside a
  `when` needs a `start` value or an `initial` branch and still counts once).
  An output you declare and never assign produces `Too few equations,
  under-determined system`, which names no file and no line at all.

AUTHORING ORDER -- cover these things, matching the ACTUAL system in the brief,
not a generic template:
1. STATE VARIABLES -- represent each accumulating physical quantity (for example a
   level, stored mass, or temperature) with exactly the continuous states required
   by the chosen component or Standard Library block. Give each state a grounded
   balance or constitutive equation, such as `der(x) = (in - out) / capacity`,
   and an explicit initial condition when the brief provides one. Do not duplicate
   a state with both a custom derivative and a library integrator.
   Every accumulating physical quantity also has a physically impossible range,
   whether or not the brief spells it out: an inventory cannot go negative, a
   vessel cannot exceed its capacity, an absolute temperature cannot fall below
   zero. Enforce that bound inside the balance itself by cutting off the
   OUTGOING term when the store is empty (and the incoming term when it is
   full), for example `qOut = if level <= levelMin then 0 else qNominal;`.
   Write that comparison WITHOUT `noEvent(...)` whenever the brief states the
   threshold as a real limit or uses it in a transition guard: `noEvent` tells
   the solver not to locate the crossing, so the state integrates past the limit
   by a whole step and settles visibly beyond it. Reserve `noEvent` for a
   boundary whose exact crossing genuinely does not matter, and never put it on
   a threshold an acceptance check or a stated setpoint refers to.
   Do not enforce it by clamping the state afterwards, and do not change the
   commanded actuator state to achieve it -- the command stays as commanded and
   the flow it produces is what the physics limits. A trajectory that leaves the
   physically possible range is a wrong result even when it compiles, simulates
   and satisfies every stated acceptance check.
2. DISCRETE CONTROL -- use an explicit mode variable, enumeration, clock, or
   StateGraph only when the evidence requires discrete stages. Drive transitions
   with the stated guards, threshold events, or timer logic, and preserve the
   stated pause/resume/freeze policy.
3. INTERLOCKS -- every stated mutual-exclusion or inhibit rule must affect the
   command equation or transition guard, not only a comment. Keep it observable so
   trajectory validation can detect a violation.
4. PARAMETERS -- expose externally meaningful resolved numeric values as parameters
   with their real units. Prefer the library's own typed quantities --
   `Modelica.Units.SI.Height`, `.Time`, `.VolumeFlowRate`, `.Temperature`,
   `.Area` and so on -- over a bare `Real x(unit="m")`, so the units are
   checked by the compiler rather than carried in a string.
   Derived values may remain equations. If the brief resolves
   historical values, use only the authoritative value and do not blend it with a
   superseded value.
5. SCHEDULE AND OUTPUTS -- put the actual stated command schedule in the controller
   or top-level system model so the bundle runs standalone. Expose the exact output
   variable names used by the structured checks and reports.
   Those reported names must be plain variables of the system model, each given
   its value by one equation. Never reuse a required report name as a COMPONENT
   INSTANCE name: the result file then contains `<name>.y` and similar members
   instead of `<name>`, and every check written against the stated name silently
   finds nothing to read.
   A command that the brief issues MORE THAN ONCE must fire once per listed
   occurrence. `cmd = time >= tFirst;` produces exactly one rising edge for the
   whole run, so a second or third occurrence of that same command is silently
   lost -- confirmed live: a controller built this way processed the first START
   and the first STOP, then sat in one state for the remaining two thirds of the
   run while three further scheduled commands passed unnoticed, and still
   compiled and simulated cleanly.
   `Modelica.Blocks.Sources.BooleanTable` TOGGLES its output at every time in
   its table; it does not emit one pulse per entry. Verified against the real
   compiler: `BooleanTable(table={t1, t2}, startValue=false)` goes true at t1
   and false at t2, giving exactly ONE rising edge, so a momentary command
   listed at t1 and again at t2 loses its second occurrence entirely. Give each
   momentary command a PAIR of table entries per occurrence -- `table={t1,
   t1 + w, t2, t2 + w}` for a short width w -- which produces one clean rising
   edge per listed time. Then `cmdPulse = cmd and not pre(cmd);` is a genuine
   one-shot for every occurrence.
   Before returning, count the transitions the schedule must cause and confirm
   the model can produce every one of them.
Acceptance thresholds and the experiment horizon from the Understanding are
authoritative. Do not add epsilon margins, change StopTime, or tune against a
reference trajectory unless the brief explicitly provides a tolerance or approves
hysteresis. If the stated rates and capacities cannot reach a required target
within the fixed horizon, report the inconsistency in `corrections` or
`clarifications` rather than silently changing a parameter.
EVENT AND DISCRETE-CONTROL DISCIPLINE

Use conservative event structures for the generated controller. These are design
rules for this bundle, not claims that every valid Modelica model must use one
exact pattern:

- Initialize each discrete mode exactly once. Use either a fixed start value or
  an explicit `when initial() then` assignment. Do not combine two independent
  initial equations for the same variable.
- Give each discrete variable one clear writer. For a mode machine, prefer one
  `when` statement with one ordered `if/elseif` chain. If separate when blocks
  are necessary for different variables, remove live cross-dependencies between
  their trigger conditions; use `pre(...)` only for variables that are actually
  discrete-time and when the previous event value is intended.
- In a `when` algorithm, use `:=`; in an equation-section `when`, use `=`.
  Keep `reinit(x, value)` in a when-clause and use it only for a continuous
  state that really needs a discontinuous reset. Do not write `reinit` as an
  ordinary continuous equation.
- A relation on a continuous Real such as `level >= limit` can generate a state
  event. A timer should be an explicit continuous timer state or a sampled
  clock; do not depend on floating-point equality such as `time == 10.0`.
- Scheduled commands should be one-shot when they trigger a transition. Use an
  edge pulse (`pulse = command and not pre(command)`) or a mode/previous-mode
  guard that you can show cannot match again on later events.
- Every branch of a single generated mode dispatcher should assign the same
  mode-related variables, or explicitly preserve them with `pre(...)`, so the
  event iteration has one unambiguous writer. Do not derive a command from a
  mode and then use that command as the mode's own transition guard; use the
  underlying state condition directly to avoid a discrete algebraic cycle.
- A state that can already satisfy its exit condition on entry must be handled
  in the entry arm or by a separately guaranteed event. Do not assume a later
  unrelated event will reevaluate an already-true condition.
- Use `noEvent(...)` only when suppressing an event is physically intended, such
  as a saturation or inventory cutoff whose exact crossing is not a control
  transition. A control transition that must be detected needs an event-capable
  guard. Do not add an arbitrary threshold margin: preserve the brief's exact
  threshold unless an approved tolerance or hysteresis is explicitly present.
  If a cutoff and a transition share a boundary, model the ordering explicitly
  (for example with one mode transition or an approved hysteresis band) and
  verify the trajectory; do not silently change the requirement.
- For each rate-limited phase, calculate whether the stated parameters and
  fixed simulation horizon can reach its target. If they cannot, keep the
  required StopTime and report the inconsistency in `corrections` or
  `clarifications`; never change a confirmed experiment horizon or invent a
  capacity merely to make the arithmetic fit. If an unstated capacity is
  necessary, mark it as an assumption and explain the derivation.
- For phase changes, use the physical energy or mass balance stated by the
  brief. A piecewise sensible/latent-heat balance is appropriate only when the
  brief establishes those quantities; never invent a smoothing gain or a
  textbook phase-change model without evidence. Check representative values
  numerically before returning the bundle.

A robust controller shape for a one-shot schedule is:

```
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  discrete Mode mode(start = Mode.Idle, fixed = true);
  discrete Real tEnter(start = 0, fixed = true);
  discrete Real waitRemaining(start = 0, fixed = true);
  Real waitElapsed;
equation
  // startButton / stopButton come in as BooleanInput from the command sources
  startPulse = edge(sample(0, scanPeriod) and startButton);
  stopPulse  = edge(sample(0, scanPeriod) and stopButton);
  waitElapsed = time - pre(tEnter);
algorithm
  when {startPulse, stopPulse, pre(mode) == Mode.Running and level >= levelHigh,
        pre(mode) == Mode.Waiting and waitElapsed >= waitDuration} then
    if stopPulse and pre(mode) <> Mode.Idle then
      mode := Mode.Paused;
      waitRemaining := waitDuration - (time - pre(tEnter));
    elseif startPulse and pre(mode) == Mode.Paused then
      mode := Mode.Waiting;
      tEnter := time - (waitDuration - pre(waitRemaining));
    elseif startPulse and pre(mode) == Mode.Idle then
      mode := Mode.Running;
    elseif pre(mode) == Mode.Running and level >= levelHigh then
      mode := Mode.Waiting;
      tEnter := time;
    elseif pre(mode) == Mode.Waiting and waitElapsed >= waitDuration then
      mode := Mode.Running;
    end if;
  end when;
```
Note what this shape avoids: no `reinit`, no continuous timer state, no `else`
branch obligation (it is an algorithm section), every read of a variable the
same `when` writes goes through `pre(...)`, and the pause/resume policy is
carried by `tEnter`/`waitRemaining` rather than by freezing a derivative.

Adapt this shape to the actual system. It is not a requirement to use this exact
controller, and a valid clocked or StateGraph design may be used when it
faithfully represents the evidence and passes the real compiler and trajectory
checks.
Never emit empty stubs, unused component placeholders, disconnected ports, generic
boundary sources, arbitrary parameter defaults or copied incomplete legacy code.
Preserve units, physical topology, dynamics, event priorities and initialization.
For sampled inputs use the real source schedule, not the expected output trajectory.
Apply flow cutoffs at physical inventory bounds without changing commanded valve
states. Include annotation(experiment(StartTime=..., StopTime=..., Tolerance=...,
Interval=...)) matching the brief's stated simulation horizon and tolerance. Source
reference tables are supplied as column schemas only: map applicable output columns to
modeled variables in references, with justified comparison tolerances and
interpolation. Do not weaken checks or tune against reference output values. Do not
put expected trajectories in the model. No external functions, file I/O, scripts,
system calls or external resources. Return complete code for every file through the
structured `files` field, without Markdown fences, and report material upstream
corrections separately.
"""
