"""Stage 3: Modelica generation. Extends `prompts.common.COMMON` with the
Modelica-specific authoring order and an event-semantics checklist -- every
rule below fixes a real, confirmed failure against the actual `omc` compiler
(some are compile errors; some are silent behavioral bugs the compiler does
NOT catch, only the actual simulated trajectory reveals them).
"""

from simulation_platform.prompts.common import COMMON

MODELICA = COMMON + """
Stage 3: use the concise SysML flow and the full engineering brief to create a
MULTI-FILE Modelica bundle built from the verified Modelica Standard Library catalog
appended to this prompt. The output must be easy to inspect in OMEdit as a component
diagram as well as executable by OpenModelica.

Return an `entry_class` and an ordered `files` list. Put one meaningful physical or
control unit in each component file and the connected experiment in exactly one
`role="system"` file, last in load order. Use at least two files; for the two-tank
case, Tank 1 and Tank 2 must be separate files. Do not hide every helper as a nested
class in one giant file. Every file must contain one complete top-level Modelica
class whose name matches its filename. Do not generate `package.mo`.

Instantiate real, fully-qualified Modelica Standard Library components from the
provided catalog wherever their semantics match the brief, and list every class
actually used in `library_components`. Add `annotation(Icon(...))` to reusable
components and explicit `annotation(Placement(...))` plus connection-line annotations
in the system diagram so opening the system in OMEdit shows a useful GUI. The system
file must also include the experiment annotation. Custom equations and a custom
controller are allowed where no library component faithfully expresses the specified
physics or pause/resume semantics; give those classes clear icons too.

Choose the simplest fidelity that solves the specified experiment. Never force a
pressure-driven fluid network onto a fixed-flow brief lacking pressure/Cv/pipe data,
and never replace a requested physical library network with unconnected decorative
icons.

You get up to several attempts against a REAL compiler that actually runs the full
scenario, but treat every attempt as if it were your only one -- write it to compile
AND behave correctly the first time, don't rely on the repair loop to find your
mistakes for you. You are fully capable of getting this right in one pass: apply
real Modelica semantics rigorously, not a rough approximation of them, and actually
verify your own equations against the two checklists below before returning them.

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

AUTHORING ORDER -- cover these five things, matching the ACTUAL system in the brief,
not a generic template:
1. STATE VARIABLES -- one continuous Real state per accumulating physical quantity
   (e.g. a level, a stored mass, a temperature), each with an explicit lumped
   balance ODE (der(x) = (in - out) / capacity-style relation), not a vague "real
   equations" placeholder. Explicit start value and fixed=true/false per the brief's
   stated initial condition.
2. DISCRETE CONTROL -- named discrete states/transitions as an explicit mode
   variable (Integer or enumeration) driven by `when` clauses on the actual stated
   guard conditions: continuous threshold events for level/measurement-based
   guards, explicit timer state variables (not floating-point event-time equality
   tests) for delay-based transitions, obeying any stated pause/resume/freeze
   policy. See the EVENT-SEMANTICS CHECKLIST below -- it is part of this step, not
   optional extra credit.
3. INTERLOCKS -- every stated mutual-exclusion/inhibit rule as an explicit boolean
   guard directly gating the relevant command, not a comment -- a real condition the
   checks can catch if it's ever wrong.
4. PARAMETERS -- one `parameter` per resolved numeric value, with its real unit. If
   the brief shows a value that had multiple historical values and states which is
   authoritative, use ONLY that resolved value -- never the superseded one, never a
   blend of both.
5. SCHEDULE AND OUTPUTS -- put the actual stated command schedule in the controller
   or top-level system model so the complete ordered bundle runs standalone; expose
   the exact output variable names the frozen acceptance checks reference.

Acceptance thresholds are authoritative. Do not add epsilon margins to a level,
temperature, time, or other transition threshold unless the brief explicitly gives
that tolerance. A numerically convenient margin changes the physical requirement
and can make a final acceptance expression false even when the sequence completes.

EVENT-SEMANTICS CHECKLIST -- every rule below fixes a real, confirmed failure (some
are compile errors; some are silent behavioral bugs the compiler does NOT catch --
only the actual simulated trajectory reveals them). Check your draft against every
line before returning it:
- Initial value of a discrete mode variable: set it EXACTLY ONE way -- either
  `fixed=true` on the declaration, or an `algorithm ... when initial() then mode :=
  ...; end when;` assignment (with `start=...` as a solver hint only, no
  `fixed=true`). Both together = a redundant initial equation = opaque
  "solveEquation failed" error.
- One discrete mode variable, ONE assigning construct: a single combined
  `when {...} then <if/elseif chain> end when;`, never multiple independent
  `when`/`elsewhen` blocks each assigning it (the solver can't order independent
  writers to the same variable -- "purely discrete algebraic loop" /
  "BackendDAECreate.lowerWhenEqn"). Every branch of that one if/elseif must assign
  the same set of variables (Modelica's own rule). This applies just as much when
  TWO parallel discrete variables (e.g. two branches of a split) share one `when`
  block -- confirmed live: writing two SEPARATE `if/elseif ... end if;` statements
  back to back inside that one `when` (one assigning branchA, a second assigning
  branchB) reproduces the exact same "purely discrete algebraic loop" failure as
  two separate `when` blocks would, because it's still two independent assigning
  constructs, just textually adjacent instead of in separate `when`s. Merge them
  into ONE if/elseif chain whose every branch assigns BOTH variables together
  (`branchA := ...; branchB := ...;` in every arm, including the final `else`),
  the same shape as the worked example below, extended to however many parallel
  variables that one `when` actually needs to drive.
- The same one-writer rule applies across DIFFERENT kinds of `when` constructs.
  Never assign an event flag in both `when sample(...)` and the controller's
  transition `when` block. Sampled input latches belong only to the sample block;
  transition outputs belong only to the transition block. Assigning a default
  value to the transition output from the sample block adds a second equation and
  makes an otherwise valid component over-determined.
- Still getting "purely discrete algebraic loop" / "analyseStrongComponentBlock
  failed"? A very common, systematic root cause: a command Boolean defined
  ALGEBRAICALLY from a mode/branch variable (`V15_cmd = branchB ==
  BranchBMode.X;`, in the `equation` section) is then ALSO read inside a `when`
  trigger vector or an if/elseif guard that assigns THAT SAME mode/branch
  variable (directly, or transitively through another discrete variable it
  feeds). That closes a real dependency cycle: the command depends on the mode,
  and the mode's own transition depends on the command. Confirmed live: fixing
  ONE such occurrence (e.g. wrapping just that one reference in `pre()`) did NOT
  clear the error, because the SAME structural pattern was still present at
  other command/guard pairs elsewhere in the file -- this is a class of mistake
  to hunt down exhaustively, not a single line to patch. For EVERY
  algebraically-derived command/flag Boolean in the file, check every place it
  (or anything built from it) is read inside a `when` trigger or an if/elseif
  guard that writes to the mode/branch variable it was derived from, and fix
  every one you find, not just the first. The most robust fix is usually to
  stop routing mode-transition guards through the intermediate command Boolean
  at all -- write the guard directly against the real sensor/level/state
  condition the command itself was derived from (e.g. use the branch-mode
  comparison directly in the guard, not the derived `_cmd` variable), so the
  guard and the command are two independent consumers of the same discrete
  state instead of one depending on the other. Only reach for wrapping an
  intermediate Boolean in `delay(...)` (the real compiler's own suggested
  workaround) if a genuine cycle remains after removing every such indirection.
- Two SEPARATE `when` blocks driving two DIFFERENT discrete variables (e.g. a main
  step sequencer `mode` and a downstream parallel-branch dispatcher `branchA`/
  `branchB`) are fine on their own, but each one's trigger-condition vector and
  every plain (non-`when`) equation that feeds into it must reference the OTHER
  block's discrete variable only through `pre(...)`, never live -- confirmed live:
  one `when` block's trigger list included a plain Boolean (`restartReady`, itself
  built from `joinReady = branchA == BranchAMode.Done and branchB ==
  BranchBMode.Done`) that read `branchA`/`branchB` LIVE, while the OTHER `when`
  block (the one that actually assigns `branchA`/`branchB`) had a trigger element
  reading `mode` LIVE (`mode == MainMode.Step7... and pre(mode) <>
  MainMode.Step7...`) -- `mode` being what the FIRST block assigns. That is a
  genuine two-way simultaneity between the two blocks, and produced the exact same
  "purely discrete algebraic loop" / `analyseStrongComponentBlock failed` error as
  every other variant of this failure class. Fix every such cross-reference to use
  `pre()` (e.g. `joinReady = pre(branchA) == BranchAMode.Done and pre(branchB) ==
  BranchBMode.Done;`). Separately: if a downstream state machine's very FIRST
  transition is really the same logical instant as an upstream transition (e.g.
  "entering Step7 immediately dispatches both branches"), don't model that as the
  downstream block reacting to an edge of the upstream variable at all -- fold that
  specific initialization directly into the SAME if/elseif arm of the UPSTREAM
  `when` block that makes the transition (`mode := Step7; branchA := Cool_B6;
  branchB := Transfer_B5_to_B7;`, all three assignments together in that one arm),
  and let the downstream block's own `when` handle only ITS OWN later-internal
  progression (Cool_B6 -> Return_B6_to_B1 -> Done, etc.), which never needs to read
  `mode` at all.
- If a mode's OWN exit condition can already be satisfied at the very instant
  that mode is entered (a state that's really a pass-through/no-op check, e.g.
  "verify X is already idle before proceeding" where X can easily already be
  idle), do not rely on the `when` block's own event to catch that case -- it
  will silently stall until some UNRELATED later event in the model happens to
  force a re-evaluation, however long that takes. Confirmed live (traced via the
  real simulated trajectory, invisible in the compiler PASSED result): a mode
  entered a "verify B5 idle" state at t=1153.7s with B5's level already below
  the idle threshold (true from t=0, no future crossing ever coming, since
  nothing fills B5 in that state) -- the exit condition was therefore already
  true the instant the state was entered, yet the mode did not advance until
  t=2500.0s, when an unrelated restart-timer event elsewhere in the model
  happened to force the next event iteration and only then picked up the
  already-true condition (same root cause as the `noEvent`-shared-threshold
  case above: a `when` vector element that's already true when it starts being
  evaluated, with no future zero-crossing of its own, never gets its own event
  to fire on). Fix: don't let entry and this kind of immediately-checkable exit
  live in two separate transitions relying on two separate events -- fold the
  check into the SAME if/elseif arm that performs entry, so entry and an
  immediate pass-through resolve together within the one event already firing
  (`elseif <entry condition> then if <exit condition already true> then mode :=
  <the state AFTER the pass-through state> else mode := <the pass-through state>
  end if;`), rather than assigning the pass-through state unconditionally and
  trusting a later event to immediately re-examine it.
- A flow cutoff gated on a state's own physical limit (e.g. `q = if h > h_low then
  qNominal else 0.0;`, to stop an outflow once its source is depleted) can hang the
  solver forever -- NOT a compile error, a `simulate() did not finish` timeout --
  whenever the system can physically balance exactly AT that boundary (inflow and
  threshold-gated outflow with close but unequal rates: confirmed live, 900k+ CSV
  rows stuck at one instant, the cutoff toggling every iteration because the state
  genuinely wants to sit on the threshold with no clean crossing to find). Fix:
  `q = if u and noEvent(h > h_low) then qNominal else 0.0;` -- `noEvent` evaluates
  the condition directly each step instead of forcing exact root-finding. Reserve
  real state events for genuine mode/phase transitions; use `noEvent` specifically
  for a physical-limit flow cutoff where the exact instant doesn't matter.
- Never let a `noEvent`-gated flow cutoff and a `when`-block mode-transition guard
  test the SAME threshold value on the SAME state. Confirmed live (traced via the
  real simulated trajectory, invisible in the compiler PASSED result): a tank level
  `h_B3` was drained by a flow cut off via `noEvent(h_B3 > h_B3_empty)`, and the
  mode-transition guard separately tested `h_B3 <= h_B3_empty` -- the state
  genuinely reached that value by t=490s (confirmed from the CSV), but because the
  flow cutoff clamps the state flat exactly AT that same boundary instead of letting
  it cross through, the transition guard's own zero-crossing event never gets a
  clean transversal edge to detect, and the mode stayed stuck for another ~2000s
  until an unrelated later event (an unrelated timer crossing its own threshold)
  incidentally forced the next event iteration and only then picked up the
  already-true guard. Fix: give the mode-transition guard a small margin on the far
  side of the physical cutoff so it genuinely crosses BEFORE the flow clamps (e.g.
  flow cutoff at `noEvent(h > h_low)`, transition guard at `h <= h_low * 1.05` or
  `h <= h_low + margin`, whichever the brief's tolerances allow) -- never reuse the
  exact same numeric threshold for both a `noEvent` flow clamp and a real event
  guard on the same state.
- Before returning, for EVERY mode/phase whose EXIT condition is a continuous
  threshold reached via a bounded rate (evaporating to a target concentration,
  filling/draining to a target level, heating/cooling to a target temperature),
  actually compute -- with a calculator, using the exact numeric parameter values
  you just wrote (duty/flow rate, mass/capacity at the point that phase begins,
  latent heat, specific heat, etc.), not a rough guess -- the time that phase
  needs, and SUM every phase's time (not just the slowest one) against the
  model's own declared `StopTime`. Require the summed total to be no more than
  85% of `StopTime` -- a bare "it just barely fits" is not good enough and has
  repeatedly, confirmably failed:
  * First confirmed live: evaporation duty and latent heat implied ~11,400s
    against a declared 3000s `StopTime` -- off by ~4x, the batch never left that
    phase at all.
  * Second confirmed live, a DIFFERENT model of the SAME case, after that first
    bug was fixed: heating to the boiling threshold needed ~3136s against the
    SAME declared 3000s `StopTime` -- off by only 136s (4.5%), close enough that
    it looked deceptively fine at a glance, but the batch STILL silently never
    finished, never restarted, never exercised its later phases, and this was
    STILL completely invisible to the real compiler's PASSED result (which only
    checks that the equations solve, not that the scenario actually completes).
    A near-miss is exactly as broken as a large miss -- do not treat "close" as
    acceptable.
  If your computed total does not leave that 85% margin, do not just return the
  model anyway and hope -- first re-check whether you actually resolved the
  brief's numeric values correctly (a duty, mass basis, or capacity value may be
  mis-transcribed, since a realistically-designed batch process's own horizon
  should accommodate its real duty cycle); only widen `StopTime` if the brief
  does not otherwise fix it as a required value. Show this arithmetic to
  yourself before returning -- don't skip straight to writing the annotation.
  If the brief ALSO states a separate minimum-wait/restart-style gate (e.g. "join
  only after time > 2500s") that is itself close to `StopTime`, remember that
  budget for the phases before that gate isn't limited to some small leftover
  slice of `StopTime` -- a phase can legitimately use almost the ENTIRE window up
  to that gate, since nothing downstream can complete earlier than the gate
  allows anyway. Confirmed live: a model sized a vessel's capacity against only
  the time it assumed was "left over" after the phases before it, when the
  actual available budget (bounded by the real restart gate, not an arbitrary
  guess) was substantially larger -- it fell short of its target by a wide
  margin as a result, reaching only ~64% of the required value by `StopTime`.
  Compute the REAL available budget for a rate-limited phase as everything up to
  the later of `StopTime` or the next hard gate that blocks progress regardless,
  not your own guess at "the remaining fraction."
- When the brief gives RATE parameters (heater/cooler duty, flow rates) and LEVEL
  thresholds (a charge level, an idle level) for a vessel but never states that
  vessel's cross-sectional area/capacity, do not default the area to an arbitrary
  round number (`1.0` is not inherently more justified than `0.1` or `10` -- it's
  just the laziest-looking guess) -- that silently fixes the vessel's total
  mass/volume, and an unlucky guess there can make otherwise-correct duty and
  timing numbers mutually IMPOSSIBLE even though every individual value was
  right. Confirmed live: a brief gave B5's heater duty (20,000 W, explicit),
  charge level (0.18 m, explicit), evaporation target concentration (explicit),
  and stated the acceptance-run EVIDENCE that the real logged run reaches restart
  around 2500s and completes within the declared 3000s `StopTime` -- but never
  gave B5's cross-sectional area. Defaulting it to 1.0 m² (a common but arbitrary
  choice) implied a ~180 kg batch that the stated heater duty needs roughly 4
  hours to evaporate to the target concentration -- off from the declared/
  evidenced window by more than an order of magnitude, even though the duty,
  level, and target numbers were all individually correct. When a vessel's area
  is unstated, DERIVE it so the vessel's behavior across its full stated level
  range is consistent with whatever explicit timing evidence the brief DOES give
  (a stated acceptance-run duration, a restart time, a described sequence of
  observed events with approximate times) -- work the arithmetic backward from
  that evidence using the vessel's own stated rate parameters, the same way you
  already must for the StopTime-margin check above, and report the derived value
  and its reasoning in `corrections`. Never silently default an unstated capacity
  parameter without checking it against the rest of the brief's own numbers.
- A latent-heat phase-change rate (evaporation, condensation, melting) is a TWO-
  REGIME energy balance, not one smooth formula: below the phase-change
  temperature, ALL heater duty goes to sensible heating (`der(T) = Q/(m*cp)`,
  phase-change rate = 0); once AT the phase-change temperature (a real threshold
  or `noEvent` comparison, e.g. `noEvent(T >= T_boil - margin)`, the same pattern
  already used elsewhere in this checklist for flow cutoffs), ALL further duty
  converts to phase change (`m_dot = Q/h_fg`, temperature ~constant). Never invent
  an ad-hoc smooth "penalty" term subtracted from the heater duty to approximate
  that switch (e.g. `m_dot = max((Q - k*(T_target - T))/h_fg, 0.0)` for some
  invented gain `k`) -- confirmed live: such a term used `k = rho*A*cp/10`, which
  at ANY temperature more than about `10*Q/(rho*A*cp)` below the target (here,
  about 0.05 K -- meaning practically the entire heating trajectory) makes the
  subtracted term outweigh `Q` by orders of magnitude, so the whole expression
  clamps to exactly 0 for the ENTIRE simulation and evaporation silently never
  starts at all -- compiled and ran to completion with zero solver errors, only
  caught by actually inspecting the real trajectory's `m_evap` column (constant 0
  start to finish) and hand-computing the formula at the actual operating
  temperatures reached. Before returning any phase-change/threshold-switch
  formula that isn't a plain `if condition then rate else 0`, evaluate it
  numerically yourself at a few representative points along the trajectory you
  expect (start, mid, and the actual crossing region) using your own chosen
  parameter values, the same way the real compiler's trajectory would -- if it
  doesn't produce the rate you intended at the point you intended, don't return
  it.
- Every scheduled command (time-based, drives a mode transition) must be genuinely
  one-shot. A raw `time >= T_command` can look edge-triggered but silently re-fire:
  confirmed live, a shared if/elseif body re-evaluated it as a plain level check on
  a LATER unrelated event and hijacked a transition that should have happened
  instead, silently eating a whole downstream phase. Use an edge-detected pulse
  (`cmdPulse = cmd and not pre(cmd);`, in the equation section) -- or any approach
  you can verify truly cannot re-match on a later event.
- If the SAME command type is scheduled to occur MORE THAN ONCE (e.g. two separate
  START times), give each occurrence its OWN independent edge-detected pulse, then
  OR the pulses together -- never OR the raw level conditions first and edge-detect
  the result. Confirmed live: `cmd = (time>=T1) or (time>=T2); pulse = cmd and not
  pre(cmd);` latches `cmd` permanently true the moment T1 crosses, so `pre(cmd)` is
  already true by T2 and `pulse` can never fire again -- the second occurrence
  silently never happens (traced via the real simulated trajectory: a system stayed
  stuck in a paused state for 480s because its second "resume" command never
  produced a pulse, and this was invisible in the compiler's PASSED result -- only
  checking the actual trajectory revealed it). Correct form: `pulse1 = (time>=T1)
  and not pre(time>=T1); pulse2 = (time>=T2) and not pre(time>=T2); pulse = pulse1
  or pulse2;` -- each occurrence gets its own `pre()` on its own raw condition,
  never a shared `pre()` on an already-OR'd condition.
- A timer as a continuous state (`der(timer) = ...`): reset ONLY via
  `reinit(timer, value)`, never `:=` ("not differentiable" error), and `reinit`
  must live in a `when` clause in the EQUATION section, never inside `algorithm`.
  If the mode dispatcher lives in `algorithm`, give each phase its OWN
  equation-section `when` for the reinit, keyed on that phase's entry edge (`when
  mode == WaitAfterHigh and pre(mode) <> WaitAfterHigh then reinit(waitTimer, 0.0);
  end when;`). A shared timer merely frozen (der=0) between reuses, never reinit at
  each new phase's start, silently carries its old value and fires every later
  phase too early -- compiles and simulates fine, so verify by tracing the phase
  sequence yourself, not by trusting a passing compile.
- Every element of a `when {c1, c2, ...}` vector must itself be Boolean (`time >=
  20`), never a bare numeric/time literal (`when {20, 220, ...}` is a type error).
- Parenthesize fully whenever combining `if-then-else` with an arithmetic operator:
  `x = (if c then a else b) - d`, never `x = if c then a else b - d` (parses as
  `if c then a else (b - d)` -- `if-then-else` binds more loosely than
  `+`/`-`/`*`/`/`). Check the literal text you're about to return, not just your
  own summary of the fix -- confirmed live, a draft claimed this fix in its
  corrections while the returned code still had the broken form.
- `equation` sections use `=` for every statement, never `:=` (`:=` is
  `algorithm`-only; a stray one is a parse error). Scan your `equation` block for
  this before returning.
- `pre(x)` is only valid when `x` is a discrete-time variable (one only ever
  assigned inside a `when` clause) -- never on a continuous `Real` computed by a
  plain `equation` ("Argument 1 of pre must be a discrete expression" -- confirmed
  live on an algebraically-defined composition fraction). Needing a safe fallback
  for a near-zero denominator in a continuous equation is not a reason to reach for
  `pre()`: use a floor instead, e.g. `x = num/max(den, eps);`, not `x = if den >
  eps then num/den else pre(x);`.
- A component's own `start` value is a declaration-only initialization hint, never
  a readable expression afterward -- `x.start` is not valid anywhere in an
  `equation`/`algorithm` section ("Variable start not found in scope", confirmed
  live). If two variables need a consistent initial value, write the same literal
  expression in both `start=` attributes directly; never try to derive one
  variable's initial value from another's `.start`.
- An attribute modifier like `(unit="...")` belongs on the DECLARED component
  itself, immediately after its name and before any `=` -- `parameter Real
  x(unit="kg/kg") = 0.0;` is correct; `parameter Real x = 0.0(unit="kg/kg");` is a
  parse error (confirmed live), because the modifier binds to the declaration, not
  to the assigned value.
- Reference only real, existing library types. `Modelica.Units.SI.TemperatureDegC`
  does not exist (confirmed live) -- `SI.Temperature` is always Kelvin; for a
  Celsius-scaled quantity use a plain `Real(unit="degC")` and convert explicitly
  (`T_degC = T_kelvin - 273.15;`), don't invent a plausible-sounding SI type name.
- Never leave an editing placeholder/marker token in the code you return --
  `<REMOVE ME>`, `TODO`, `XXX`, `...` or similar (confirmed live: a draft left a
  literal `<REMOVE ME>` token where a real component name belonged, which the
  compiler then reported as an undefined variable). If you decided to remove
  something, actually delete it from the returned text; every line you return
  must be real, finished, intentional content, never a note to yourself.
- Before returning, the model should be exactly determined: one equation per
  unknown. An over-determined system ("too many equations") almost always means
  the SAME variable was given two independent defining equations somewhere (e.g.
  both an algebraic definition and a separate `der(...)` equation for it, or a
  duplicated line) -- find and remove the redundant one rather than trusting the
  solver to reconcile extra equations.

WORKED EXAMPLE of a correctly-structured one-shot command + single mode dispatcher
(the exact shape that has repeatedly failed live -- follow this structure, not just
the prose rules above, for the command/mode-transition part of your model):
```
equation
  // level condition first, THEN edge-detect it into a one-shot pulse -- both
  // in the equation section, `pre()` applied to the declared Boolean, not to
  // a raw comparison expression
  startCmd = time >= tStart;
  stopCmd  = time >= tStop;
  startPulse = startCmd and not pre(startCmd);
  stopPulse  = stopCmd and not pre(stopCmd);
  // reinit for any wait-phase timer lives HERE, in its own when, never in algorithm
  when mode == Mode.Waiting and pre(mode) <> Mode.Waiting then
    reinit(waitTimer, 0.0);
  end when;
algorithm
  // exactly ONE when/elsewhen chain assigns `mode`; every element is one-shot
  // (a pulse boolean) or a genuine physical threshold crossing -- never a raw
  // `time >= T` mixed in as if it were one-shot
  when {startPulse, stopPulse, mode == Mode.Running and level >= levelHigh,
        mode == Mode.Waiting and waitTimer >= waitDuration} then
    if stopPulse and pre(mode) <> Mode.Idle then
      mode := Mode.Paused;
    elseif startPulse and pre(mode) == Mode.Idle then
      mode := Mode.Running;
    elseif pre(mode) == Mode.Running and level >= levelHigh then
      mode := Mode.Waiting;
    elseif pre(mode) == Mode.Waiting and waitTimer >= waitDuration then
      mode := Mode.Running;
    end if;
  end when;
```
Note what makes this correct: `startPulse`/`stopPulse` are TRUE for exactly one
event instant each, so they cannot re-match on a later, unrelated event the way a
raw `time >= tStart` would; `reinit` is in the equation section in its own `when`,
never inside the `algorithm` block; and `mode` has exactly one assigning construct.

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
