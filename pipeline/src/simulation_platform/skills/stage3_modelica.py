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
- ONE REFERENCE PER NETWORK, NEVER TWO SOURCES FIXING THE SAME NODE. Every
  electrical circuit needs exactly one `Ground`, every mechanical chain exactly
  one fixed reference, every magnetic circuit exactly one magnetic ground/reference,
  and every fluid loop exactly one pressure reference (a boundary or expansion
  source). A missing one leaves a potential undetermined (a singular system); an
  extra one over-determines it. The same discipline applies at an ordinary
  connection point: never let two components each try to FIX the same
  potential/level/pressure/flow at one node (two voltage sources in parallel, two
  fixed-temperature boundaries on one node, two prescribed levels feeding one
  tank's inlet) -- exactly one definition per connected quantity, matching the
  equation-count rule below. Seen live on this project: an earlier bundle had two
  separate outlet connections each trying to define the same tank inlet flow;
  fixed by summing them into one scalar flow equation and one mixed-composition
  equation instead of leaving both connected directly.

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
  belongs to simply carries nothing for the whole run. Wire every port you
  declare. Before returning, walk each component's connectors and confirm each
  one appears in a `connect(...)` or is given a value by an equation in the
  system model.
- AN INPUT AN INSTANCE DOES NOT USE IS WIRED TO A CONSTANT. One reusable class
  instantiated per unit carries the union of every unit's ports -- only the
  heated vessel takes a duty command, only some take a second inlet -- so some
  inputs have no natural source on some instances. Do not resolve that by
  writing a near-duplicate class per unit, and do not leave the input dangling.
  Give it a source that says zero explicitly:

      Modelica.Blocks.Sources.Constant noHeat(k = 0)
        annotation(Placement(transformation(extent={{-100,-10},{-80,10}})));
    equation
      connect(noHeat.y, B1.Qcmd)
        annotation(Line(points={{-79,0},{-60,0}}, color={0,0,127}));

  This is deliberate rather than accidental zero, it needs no bookkeeping, and
  the diagram shows plainly that the port is tied off.

  Do NOT make such a port conditional. `RealInput Qcmd if useHeatPort;` looks
  like the answer and is a trap: a conditional component is REMOVED from the
  model when its guard is false, so the class can no longer mention it in any
  equation -- `Qin = if useHeatPort then Qcmd else 0;` is rejected with
  "'B1.Qcmd' refers to a component with a false condition" even though the
  guard is tested right there. Seen live: the same error came back identically
  on two consecutive repair attempts, because the message points at the class's
  equation while the cause is the declaration. Using one correctly requires a
  protected internal connector and a `connect` to it, which is not worth it
  here.

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

- A CLAMP MUST NOT SIT ON A THRESHOLD THE BRIEF TESTS. A vessel that stops
  draining at `level <= 0.01` can never satisfy a criterion written
  `level < 0.01`, and a stage waiting on that criterion waits forever. Seen
  live: a plant charged and mixed correctly, then stalled for the rest of the
  run because "empty" was clamped at exactly the value "empty" is defined as,
  and every later stage and its checks stayed at zero.
  When you introduce a floor to keep a quantity physical, put it strictly
  BELOW any threshold a guard or check compares against -- drain to
  effectively zero and let the guard decide -- and record the floor in
  `corrections`. Before returning, take each threshold the brief states and
  confirm the quantity can actually cross it in the direction required.
- REPORT EVERY VARIABLE THE BRIEF'S CONTRACT NAMES. The brief lists the
  variables the model must report, and a check reading one that is absent
  cannot be evaluated at all -- which is a worse outcome than failing, because
  nothing is learned. Declare each one at the top level under the exact name
  the brief uses, even where it only mirrors an internal value.
- A REPORTED VARIABLE MUST ALIAS A COMPONENT'S OUTPUT, NEVER ITS PARAMETER.
  `X = someBlock.k;` reads `someBlock`'s PARAMETER -- the value it was
  configured with -- not a simulated signal, and a parameter is not part of
  the result trajectory: the variable compiles cleanly but is silently absent
  from the result summary. Seen live: a required flow-proof signal was
  written as `FIS801_kg_s = fis801.k;` against a `Modelica.Blocks.Sources.
  Constant`, and the acceptance check reading it found the variable simply
  missing. Always alias the OUTPUT connector, `someBlock.y`
  (`RealOutput`/`BooleanOutput`), even for a value that never changes.
- A CONSTANT BOOLEAN IS `BooleanConstant`, NEVER A ONE-ENTRY `BooleanTable`.
  BooleanTable TOGGLES at every time it lists, so
  `BooleanTable(table={0}, startValue=true)` starts true and flips to false at
  t=0, staying false for the entire run. That is how a permissive meant to read
  "always available" ends up permanently false, and it is nearly invisible:
  the model compiles, simulates the full horizon, and every safety check passes
  because the sequence it was gating never ran. Seen live -- a plant sat in its
  initial state for 3000 s with its start command arriving correctly, because
  the one other condition in the guard was wired this way.
  Write `Modelica.Blocks.Sources.BooleanConstant(k = true)` for a signal that
  simply holds. Reserve BooleanTable for a signal that genuinely changes at
  stated times, and give each momentary occurrence a PAIR of entries.
- ANY TABLE'S TIME COLUMN (`BooleanTable.table`, `CombiTimeTable.table`'s first
  column, or similar) MUST BE STRICTLY INCREASING, with no duplicate or
  reversed timestamp. A repeated or out-of-order time is rejected by the real
  compiler with an error that names the table instance, not the schedule value
  that caused it, so check every table's own time values against the brief's
  stated schedule before returning, not just its shape.
- A CONTINUOUS SIGNAL DRIVING ITS OWN SWITCHING COMMAND NEEDS AN EDGE OR A
  DWELL GUARD, NEVER A BARE LEVEL COMPARISON RE-EVALUATED EVERY STEP.
  `cmd = level >= setpoint;` where `cmd` itself drives the flow that moves
  `level` can toggle every solver step once `level` sits within numerical
  noise of `setpoint`, producing thousands of events in a tiny time span
  ("model terminated ... too many events" / the simulation appears to hang).
  This does NOT mean moving or widening the brief's stated threshold -- see
  the "do not add an arbitrary threshold margin" rule under EVENT AND
  DISCRETE-CONTROL DISCIPLINE below, which still governs the threshold VALUE.
  Keep the exact stated threshold and prevent the chatter a different way:
  latch the transition through the controller's own scan/edge machinery
  (`pre(mode) == ... and level >= setpoint` inside the mode dispatcher, which
  only re-evaluates on an event and only fires the one edge) rather than a
  free-standing continuous equation re-armed every step. Reserve an actual
  second threshold (true two-level hysteresis) for a case where the brief
  itself describes two distinct setpoints (a high and a low), and never
  invent one around a threshold an acceptance check compares against.
- A PERMISSIVE IN A TRANSITION GUARD IS COMPUTED, NOT ASSUMED. If a guard reads
  a condition the brief defines from plant state -- a vessel being empty, a
  flow proof being present -- derive it from that state, so it becomes true
  when the plant makes it true. Wiring it to a source fixes the whole sequence
  to whatever that source happens to say.
- AN ENTRY GUARD ALREADY TRUE AT t=0 NEVER FIRES AGAIN. A `when {...} then`
  mode dispatcher only re-evaluates its branches on an EVENT -- something
  changing. If a transition's guard is built from permissives that are all
  `BooleanConstant`/always-true from the very first instant, the condition
  never has a false-to-true EDGE for the `when` to catch, because it was
  already true before the first event existed to notice it. Worse, if that
  same `when` also carries an `if initial() then mode := State.Initial; ...`
  branch, that branch matches first on the ONE event that does fire (the
  initial event itself) and the dispatcher re-asserts the initial state
  forever -- the model compiles, simulates the full horizon, and every
  command stays at its starting value for the whole run. Do not let a
  same-scan `if initial()` branch pre-empt the real entry check: either give
  the entry transition an explicit one-shot pulse (`entryPulse =
  edge(startButton) or (initial() and startEnable and ...)`, wired to an
  actual clock/button edge, not a bare constant) or verify by construction
  that the entry guard can only become true from a later event, never from
  the initial one.
- A SCHEDULED `BooleanTable`/`IntegerTable` PULSE WHOSE FIRST ENTRY IS
  EXACTLY t=0 IS INVISIBLE TO `edge()`, even though the signal genuinely
  toggles. This is a different trap from the rule above (there the source
  never toggles at all; here it does, but at the one instant `edge()`
  cannot see). Confirmed live in an isolated model against the real
  compiler: `BooleanTable(table={0, 0.2, 2505, 2505.2}, startValue=false)`
  feeding `startPulse = edge(startEnable);` never fired on the t=0 toggle
  -- a counter driven by `when startPulse then ... end when;` stayed at 0
  through the whole first pulse and only incremented once, on the SECOND
  scheduled toggle at t=2505 -- because `pre()` already equals the signal's
  own value at the very first instant, so there is no false-to-true edge
  there for `edge()` to catch. Shifting the same table to `{0.001, 0.2,
  2505, 2505.2}` and re-running the identical model caught BOTH pulses.
  Found live: this silently shifted an entire batch-cycle's start (and
  therefore its whole timeline) by 2505 seconds, because the `Initial ->
  Step1` transition simply never ran until the scenario's SECOND pulse --
  which was meant to test a later restart, not the initial start -- with no
  compiler error, since every construct involved is individually legal.
  If a command table is meant to fire (or start high) right at the
  beginning of the run, give its first entry a small positive offset
  (`0.001`, not `0`) instead of landing exactly on t=0, so the toggle
  happens strictly after the initial instant and `edge()` can see it.
- NEVER DIVIDE BY A FLOW. A flow is zero whenever its valve or pump is off,
  which in a sequenced process is most of the run, and the simulation stops the
  instant it happens: "division by zero at time 43, (a=0) / (b=0), where
  divisor b expression is: B3.qIn". It compiles and initialises cleanly first,
  so this only ever shows up part way into the run.
  A composition or specific quantity is carried by INVENTORY, not by the
  instantaneous flow that changes it. Track the extensive quantities as states
  and divide once, by a mass that cannot vanish:

      der(m)      = qIn*rho_in - qOut*rho;
      der(m_salt) = qIn*rho_in*w_in - qOut*rho*w;
      w           = m_salt / max(m, m_min);

  where `m_min` is a small positive floor recorded as an assumption. The same
  applies to any other divisor a schedule can drive to zero -- a level, an
  area, an elapsed time. Guard the divisor at its definition rather than
  wrapping each use in an `if`.
- FLOOR A RATIO'S NUMERATOR THE SAME WAY ITS DENOMINATOR IS FLOORED, or the
  ratio can start at exactly 0 even though it is asserted strictly positive.
  Confirmed live and reproduced against the real compiler: a custom tank
  component computed `T = E/max(cp*m, cp*m_min)` (temperature from stored
  energy) with `assert(T > 0, "temperature below absolute zero");`, but
  declared `E(start = rho*area*levelStart*cp*TStart)` -- no floor at all on
  the numerator's own start expression. Every instance meant to start
  "empty" (`levelStart = 0.0`) made `E`'s start evaluate to EXACTLY 0
  regardless of `TStart`, so `T` started at exactly 0 K and tripped the
  assert during initialization -- reproduced identically on 3 consecutive
  repair attempts in the same run, because the compiler's own message names
  only the generic assert line (reused by every instance of the class) and
  never says which instance or why, so repeated attempts could not converge
  on the real cause from the error text alone. The fix that finally worked:
  floor the numerator's start value with the SAME expression that floors
  the denominator, `E(start = max(rho*area*levelStart, m_min)*cp*TStart)`
  -- the ratio then starts at the physically correct `TStart` regardless of
  how small (or exactly zero) `levelStart` is. Apply this whenever an
  extensive state's start value is a product that includes a parameter
  which can legitimately be 0 (a level, a mass, an area) and that state
  also feeds a ratio asserted strictly positive or otherwise physically
  bounded away from 0.
- AN `if X > 0 then .../X... else ...` GUARD DOES NOT PROTECT A DIVISION BY
  A DISCONTINUOUS FLOW, even though it looks obviously safe on inspection --
  use `max(X, floor)` instead, with NO `if` at all. Confirmed live and
  reproduced against the real compiler: `B3.xIn = if qB1B3 + qB2B3 > 0 then
  (qB1B3*B1.xNaCl + qB2B3*B2.xNaCl)/(qB1B3 + qB2B3) else 0;`, where
  `qB1B3`/`qB2B3` are each `if <valve>.open then <rate> else 0` (a bare
  step, not a smooth signal) -- crashed identically on 3 consecutive repair
  attempts, byte-for-byte the SAME generated bundle every time, with
  `division by zero at time 104.5..., (a=0) / (b=0), where divisor b
  expression is: B3.qIn` (an alias of the same sum). The generated C code
  shows why: OpenModelica compiles an `if`-guard in a continuous equation
  into an EVENT-triggered relation (`GreaterZC`/`relationhysteresis`) when
  the guarded expression is not smooth or a state -- so the condition's
  cached boolean can still read the PREVIOUS instant's value at the exact
  moment the divisor itself steps to zero, and the division executes
  anyway. This is the same "never divide by a flow" hazard above wearing a
  disguise that passes visual review -- confirmed fix: replace the whole
  `if`/`else` with a bare `max()` floor, `.../max(qB1B3 + qB2B3, 1e-9)` --
  the IDENTICAL bundle then completed the full run with `LOG_SUCCESS`. Any
  time a divisor is built from valve/pump Boolean commands (however many
  terms are summed), floor it with `max(...)`; never gate the division with
  an `if` on that same expression.
- COUNT EQUATIONS AGAINST VARIABLES BEFORE RETURNING. Every non-parameter
  variable you declare must be determined by exactly one equation, and a
  `connect` determines the connected variable. Two short of that is rejected
  with "Too few equations, under-determined system. The model has N equation(s)
  and M variable(s)", which names no variable and no file, so the count is the
  only way to find it. Walk your own declarations: for each one, name the
  equation or connection that gives it its value. A variable you declared for a
  report you never wrote is the usual culprit -- delete it rather than padding
  the model with an equation to match.
- TAKE A CLASS PATH FROM THE CATALOG EXACTLY AS WRITTEN. Do not assemble one
  from the part of the library it feels like it belongs to: conversion blocks
  live under `Modelica.Blocks.Math`, not `Modelica.Blocks.Sources`, and
  `Modelica.Blocks.Sources.BooleanToReal` is rejected with "not found in
  scope". If a class you want is not in the catalog, use one that is.
- `Integer(e)` CONVERTS AN ENUMERATION; `integer(x)` ROUNDS A REAL. They differ
  by one letter and are different builtins. To report an enumeration state as a
  number write `stateId = Integer(mode);` -- lowercase `integer(mode)` is
  rejected with "Type mismatch for positional argument 1 in integer(...)",
  because that builtin takes a Real and rounds it toward minus infinity.
- `edge()` AND `pre()` TAKE A VARIABLE, NEVER AN EXPRESSION. Give the
  expression its own Boolean and pass that:
      Boolean levelHighSample;
    equation
      levelHighSample = sample(0, scanPeriod) and level >= levelHigh;
      levelHighPulse  = edge(levelHighSample);
  Writing `edge(sample(0, scanPeriod) and level >= levelHigh)` is rejected
  with "First argument to edge in component <REMOVE ME> must be a variable"
  -- the component name is not even reported, so the message does not say
  where to look. The same applies to `pre()`. (This example samples a
  continuous THRESHOLD condition, which is a legitimate use of `sample()`
  -- see the sampling rule below for when `sample()` helps and when it only
  adds latency.)
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

- AN INSTANCE NEVER SHARES ITS OWN CLASS'S NAME. Never write
  `CurrentRamp CurrentRamp;` -- an instance name identical to its class name
  shadows the class in that scope, so it compiles at the declaration line
  itself but fails flattening several lines later, the first time anything
  needs to resolve the CLASS rather than this instance: `Expected
  CurrentRamp to be a class, but found component instead`, reported at that
  later USE, never at the declaration that actually caused it. Give every
  instance a name distinct from its class -- conventionally lower-camelCase
  for the instance against PascalCase for the class (`CurrentRamp
  currentRamp;`), which also makes the two visually distinct at a glance.

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

- SAMPLE ONLY THE SIGNALS THAT ACTUALLY NEED IT -- ones the controller's own
  state feeds back into. Gating EVERY input through `sample(0, scanPeriod)`,
  including an independent operator command that never depends on the
  controller's own output at all, costs real timing accuracy for no benefit
  and is a mistake on its own, not just a defensive habit:
  ```
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  startPulse = edge(startButton);   -- startButton comes from an independent
                                     -- schedule/operator source, never from
                                     -- this controller's own mode/output, so
                                     -- capture the edge directly.
  ```
  Confirmed live and verified against the real compiler: `startSample =
  sample(0, scanPeriod) and startButton; startPulse = edge(startSample);`
  compiles and simulates cleanly, but costs a FULL extra scan period of
  latency beyond what `sample()` itself already implies, because the
  command's own source event (a `BooleanTable`/`CombiTimeTable` entry) lands
  a hair after the exact stated instant (its own root-finding tolerance), so
  it can just barely miss the coincident scan tick and only gets caught on
  the NEXT one. On a real case this made every operator-command response land
  one full scan period late (0.80 s target crossed at t=220.0 s, but the
  command took effect at t=220.1 s) and failed two acceptance checks written
  against the stated command times. Removing the `sample()` layer for that
  same signal -- `startPulse = edge(startButton);` directly -- reproduced the
  identical sequence with every transition landing within numerical
  tolerance of its true commanded instant, and did NOT reintroduce any
  algebraic-loop error.
  RESERVE `sample()`-gating for a signal that genuinely creates a same-instant
  dependency on the controller's own state or output -- for example a
  continuous condition computed FROM a value the controller itself just set,
  or two discrete quantities that would otherwise need each other's CURRENT
  value in the same event. That is what actually causes `Purely discrete
  algebraic loops cannot be solved by iterative processes`, and latching such
  a signal to the previous scan's value is the real fix for it. An
  independent operator button, a scheduled command table, or any other input
  that never reads back from this controller's own mode/output has no such
  cycle to break, at any latency, and should be captured directly with
  `edge(...)` on the raw signal for exact response timing.
  When you DO need genuine periodic scanning (state-dependent conditions,
  or the brief explicitly describes a scanned PLC and states its own
  response-time tolerance), take the period from the brief when it states
  one; otherwise choose one and record it in `corrections`. Size it against
  the TIMING TOLERANCE the acceptance checks demand, not merely against the
  stated durations -- if a check requires an action at an exact instant, a
  0.1 s scan that responds a period later still fails it.

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
   Back that up with an explicit `assert(...)` on every quantity with a real
   physical limit -- `assert(w_NaCl >= 0 and w_NaCl <= 1, "mass fraction out of
   range")`, `assert(T_K > 0, "temperature below absolute zero")`, a valve
   opening in `[0, 1]`, an absolute pressure `> 0`. An `assert` costs nothing
   when the model is right, and turns a silently-wrong trajectory (the failure
   mode this pipeline has actually hit) into a loud simulation-time failure
   this repair loop can see and fix, instead of a report that looks plausible
   but is not.
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
   Set `nominal = ...` on a variable whose brief-stated magnitude sits far from
   1 in its own SI unit (a pressure around 1e5 Pa next to a mass flow around
   1e-3 kg/s, for example), so the solver scales its iteration against the
   right magnitude instead of an arbitrary one.
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
   t1 + w, t2, t2 + w}` -- which produces one clean rising edge per listed
   time. Then `cmdPulse = cmd and not pre(cmd);` is a genuine one-shot for
   every occurrence.
   The width w is NOT free: when the controller latches its inputs on a scan
   period, a press shorter than one scan can fall entirely between two scans
   and be missed, and nothing reports it -- the model compiles, simulates
   cleanly, and simply never performs the commanded action. Confirmed live on
   a sequencing benchmark: scanPeriod was 0.1 s and each press was given
   w = 0.05 s, so a STOP at 220 s was never seen, the controller stayed in its
   transfer state for the next 200 s, and the run still looked plausible
   because a later command happened to land on a scan boundary and did fire.
   Set `w` to at least twice the scan period, so at least one scan instant
   falls strictly inside every press. Derive it rather than guessing: declare
   `parameter Real cmdWidth = 2 * scanPeriod;` and build the tables from it.
   If the commands are not sampled at all, w only needs to be long enough to
   produce a distinct rising edge.
   Before returning, count the transitions the schedule must cause and confirm
   the model can produce every one of them. For each scheduled command, check
   the arithmetic explicitly: that its press is wide enough for the scan that
   reads it, and that the state it arrives in actually has a transition
   accepting it. A command the controller cannot see and a command the state
   machine ignores fail identically and silently.
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
  initial equations for the same variable -- never write `discrete Mode
  mode(start = Mode.IDLE, fixed = true);` AND ALSO assign `mode := Mode.IDLE;`
  inside `when initial() then ... end when;`. This is the single most
  misleading real-compiler failure in this whole prompt: OpenModelica does
  NOT reject it as an initialization error. The over-determined
  initialization forces the enumeration/Integer variable into a nonlinear
  system's iteration variables, and OMC's C code generator for those
  unconditionally emits a `.nominal` field access for every iteration
  variable regardless of type -- which Integer/enumeration attributes do not
  have. What you actually see, many attempts later, is a locationless C
  build failure naming a GENERATED file, not yours: `error: no member named
  'nominal' in 'struct INTEGER_ATTRIBUTE'` in a file named
  `<Model>_NNnls.c`, sometimes preceded by the warnings "The initial
  conditions are over specified" and "the tearing heuristic was not able to
  avoid discrete iteration variables". If you ever see either of those, the
  fix is NOT in the nonlinear-system machinery the message points at -- find
  every discrete/Integer/enumeration variable declared with `fixed = true`
  and check whether `when initial()` also assigns it; remove one of the two
  initial equations.
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
  parameter Real cmdWidth = 2 * scanPeriod "command press width; see the schedule rule above";
  discrete Mode mode(start = Mode.Idle, fixed = true);
  discrete Real tEnter(start = 0, fixed = true);
  discrete Real waitRemaining(start = 0, fixed = true);
  Real waitElapsed;
equation
  // startButton / stopButton come in as BooleanInput from an independent
  // command source (an operator or a schedule table) that never reads back
  // from this controller's own mode/output, so capture the edge directly --
  // NOT through sample(scanPeriod), which would cost a full extra scan
  // period of latency against the command's true instant for no benefit
  // (see the sampling rule above).
  startPulse  = edge(startButton);
  stopPulse   = edge(stopButton);
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

FINAL CHECKLIST -- unrelated final constraints, kept short on purpose. Go
through every one before returning:
- Never emit empty stubs, unused component placeholders, disconnected ports,
  generic boundary sources, arbitrary parameter defaults, or copied incomplete
  legacy code.
- Preserve units, physical topology, dynamics, event priorities, and
  initialization exactly as the brief establishes them.
- For sampled inputs, drive them from the real source schedule, never from the
  expected OUTPUT trajectory -- an input built from the answer is not a model.
- Apply flow cutoffs at physical inventory bounds without changing the
  commanded valve state itself (see STATE VARIABLES above).
- Include `annotation(experiment(StartTime=..., StopTime=..., Tolerance=...,
  Interval=...))` matching the brief's stated simulation horizon and
  tolerance, on the system file.
- Source reference tables are supplied as column schemas only: map applicable
  output columns to modeled variables in `references`, with justified
  comparison tolerances and interpolation. Never weaken a check or tune a
  parameter against a reference output value, and never put an expected
  trajectory inside the model itself.
- No external functions, file I/O, scripts, system calls, or other external
  resources -- the bundle must be self-contained and runnable offline.
- Return complete code for every file through the structured `files` field,
  with no Markdown fences around any file's `code`, and report every material
  upstream assumption or correction in `corrections`, separately from the code.
"""
