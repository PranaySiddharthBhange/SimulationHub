# Two Coupled Masses — Energy Beats Back And Forth Between Them

## System

Two identical masses each sit on their own spring anchored to a fixed
wall, and a third, much weaker spring connects the two masses directly to
each other. Only one mass is displaced and released at the start; the
other begins completely at rest at its own equilibrium. Because the two
masses are coupled, the initial displacement does not stay on the first
mass -- it slowly transfers almost entirely to the second mass, then
transfers back, repeating indefinitely. This produces a slow "beat"
envelope riding on top of the fast individual oscillation, a genuinely
different waveform shape from the single decaying oscillation in
`simple_spring_mass_release`.

- Mass 1 and Mass 2: 1 kg each, both sliding with no friction.
- Spring 1: stiffness 1 N/m, connects Mass 1 to a fixed wall.
- Spring 2: stiffness 1 N/m, connects Mass 2 to a second fixed wall.
- Coupling spring: stiffness 0.02 N/m, connects Mass 1 directly to Mass 2
  (much weaker than either wall spring -- this weak coupling is what
  produces a slow beat rather than fast, tightly locked motion).
- No damping anywhere in this case -- both masses keep oscillating for the
  entire run; nothing settles.
- Starting condition at t = 0: Mass 1 at position 0.10 m from its own
  equilibrium, at rest (velocity 0 m/s). Mass 2 at position 0 m (its own
  equilibrium), at rest (velocity 0 m/s).
- Governing equations:
  `m*d^2(x1)/dt^2 = -k*x1 - k_c*(x1 - x2)`,
  `m*d^2(x2)/dt^2 = -k*x2 - k_c*(x2 - x1)`,
  with m = 1 kg, k = 1 N/m, k_c = 0.02 N/m.

## Requirements

- REQ-SIM-001: Simulate for 350 seconds and report both masses' positions
  for the whole run.
- REQ-FUN-001: Starting with only Mass 1 displaced, Mass 2 shall begin
  oscillating with growing amplitude as energy transfers into it from
  Mass 1.
- REQ-FUN-002: By roughly the halfway point of one beat cycle, nearly all
  of the initial displacement shall have transferred to Mass 2, and
  Mass 1's own oscillation amplitude shall have shrunk to nearly zero at
  that same moment.
- REQ-FUN-003: The energy shall then transfer back, completing a full beat
  cycle, and this exchange shall repeat for the entire run -- neither mass
  shall ever permanently come to rest, and neither shall exceed the
  original 0.10 m amplitude.

## Acceptance checks

- AC-01 starting condition: `mass1_position_m == 0.10` and
  `mass2_position_m == 0.0` at t = 0 s (absolute tolerance 0.001).
- AC-02 Mass 2 grows from rest: `abs(mass2_position_m) >= 0.03` becomes
  true at some point between t = 90 s and t = 130 s (ever value == 1.0).
- AC-03 near-complete energy transfer to Mass 2 at the beat half-period:
  `abs(mass2_position_m) >= 0.095` becomes true at some point between
  t = 150 s and t = 165 s (ever value == 1.0). Expected peak magnitude
  about 0.09999 m at t = 157.1 s.
- AC-04 Mass 1 nearly at rest at that same moment: `abs(mass1_position_m)
  <= 0.01` at t = 157.1 s -- confirms the transfer is genuinely
  near-complete, not just Mass 2 growing while Mass 1 stays large too.
- AC-05 energy returns to Mass 1 by the full beat period:
  `abs(mass1_position_m) >= 0.095` becomes true at some point between
  t = 310 s and t = 325 s (ever value == 1.0). Expected magnitude close to
  0.10 m at about t = 317.3 s.
- AC-06 neither mass ever exceeds the original amplitude, for the entire
  run: `abs(mass1_position_m) <= 0.105` and `abs(mass2_position_m) <=
  0.105` hold at all times from t = 0 s to t = 350 s.
- AC-07 still actively oscillating near the end of the run, not damped
  out: at t = 340 s, `abs(mass1_position_m) >= 0.02` or
  `abs(mass2_position_m) >= 0.02` -- confirms motion has not decayed
  (there is no damping anywhere in this system).

## Notes

- All beat-timing figures above were found by direct RK4 numerical
  integration of the two coupled equations, not estimated from the
  standard beat-frequency approximation formula alone (though they agree
  with it closely: the approximate half-beat period
  `pi/(omega_a - omega_s)` with `omega_s = sqrt(k/m) = 1` and
  `omega_a = sqrt((k+2*k_c)/m) ~= 1.0198` gives about 158.7 s, matching
  the simulated 157.1 s).
- This case has no damping anywhere and is not asking for an equilibrium;
  like the nonlinear pendulum case, it is testing a SUSTAINED dynamic
  pattern (here, a repeating beat), not a settle-to-rest behavior.
- Do not add a coupling term between the two masses' velocities, or any
  damping term -- the beat pattern here depends on the system being
  purely conservative (energy-preserving); adding damping would cause the
  beat envelope itself to decay over time, which this brief does not
  state.
