# Negative-Damping Oscillator — A Result That Grows, Not Settles

## System

A mass-spring system identical in form to `simple_spring_mass_release` in
this same folder, except the damper here ADDS energy to the system instead
of removing it (a negative damping coefficient -- representing, for
example, a self-excited instability such as flutter). Released from a
small initial displacement, the oscillation amplitude GROWS over time
instead of decaying. This case exists specifically to check that a
generated model, and the checks written against it, do not silently assume
every released system settles down -- some genuinely do not, and this one
is deliberately built to diverge.

- Mass: 1 kg. Spring: stiffness 1 N/m (natural frequency
  `omega_n = sqrt(k/m) = 1 rad/s`).
- Damper: -0.1 N*s/m -- note the negative sign; this term adds energy to
  the system rather than removing it (damping ratio zeta = -0.05).
- Clamp: holds the mass fixed at position 0.01 m with zero velocity from
  t = 0 to t = 5 s. Releases once at t = 5 s and never re-engages.
- Governing equation from t = 5 s onward:
  `m*d^2(x)/dt^2 + c*dx/dt + k*x = 0`, with c = -0.1 N*s/m, starting from
  x = 0.01 m and velocity 0 m/s at the instant of release.
- No external force, controller, or safety cutoff of any kind exists in
  this brief -- the amplitude is expected to keep growing for the entire
  stated run.

## Requirements

- REQ-SIM-001: Simulate for 110 seconds and report the mass's position and
  the clamp's engaged/released state for the whole run.
- REQ-FUN-001: While the clamp is engaged (t = 0 to t = 5 s), position
  shall stay exactly at 0.01 m.
- REQ-FUN-002: At t = 5 s the clamp shall release once, and the mass shall
  begin oscillating around the spring's natural length.
- REQ-FUN-003: Given the stated negative damping, the oscillation
  amplitude shall GROW over time rather than decay -- each successive
  swing shall reach further from zero than the one before it, for the
  entire remainder of the run.

## Acceptance checks

- AC-01 clamp engaged pre-release: `clamp_engaged == 1` and
  `position_m == 0.01` at t = 4 s.
- AC-02 clamp releases on schedule: `clamp_engaged == 0` at t = 6 s.
- AC-03 amplitude has grown well past its starting value by mid-run:
  `abs(position_m) >= 0.15` becomes true at some point between t = 60 s
  and t = 75 s (ever value == 1.0). Expected about 0.193 m in magnitude
  near t = 65 s.
- AC-04 amplitude keeps growing further: `abs(position_m) >= 0.8` becomes
  true at some point between t = 95 s and t = 110 s (ever value == 1.0).
  Expected about 0.897 m near t = 100 s and about 1.22 m near t = 105 s.
- AC-05 growth is monotonic on the envelope: the peak magnitude reached by
  t = 105 s shall exceed the peak magnitude reached by t = 65 s (treat the
  AC-03 and AC-04 evidence together -- the later swing must be larger in
  magnitude than the earlier one, confirming genuine growth, not a
  one-off large sample).
- AC-06 never at rest again after release, for the entire run: at no point
  from t = 6 s to t = 110 s shall `abs(position_m) <= 0.001` and
  `abs(velocity_m_s) <= 0.001` hold simultaneously -- a genuinely growing
  oscillation never returns to rest at the origin.

## Notes

- This is the direct counterpart to `simple_spring_mass_release`: same
  mass and stiffness, same release-at-t=5s structure, but with the sign of
  the damping term flipped. Every growth figure above was computed from
  the same closed-form damped-oscillator solution used there, with
  zeta = -0.05 substituted in, confirmed numerically rather than assumed.
- Do not add a limiter, saturation, or any stabilizing feedback anywhere
  in this model -- this brief describes a genuinely open-loop unstable
  system on purpose, and nothing in the stated physics bounds the
  amplitude within the simulated window.
- This case is a useful check on the pipeline itself, not just on
  generated Modelica: an acceptance check or a validation review that
  assumes "released systems settle down" (a pattern true of every other
  case in this folder) would incorrectly flag this correct, growing
  result as wrong.
