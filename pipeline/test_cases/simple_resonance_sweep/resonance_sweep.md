# Swept-Frequency Forcing — A Resonance Peak That Lands Off The Natural Frequency

## System

A lightly damped mass-spring-damper is driven by an external sinusoidal
force whose frequency slowly increases over the run (a "chirp" or sweep),
rather than the fixed on/off or step inputs every other case in this
folder uses. The mass's own natural frequency is 1 rad/s. A naive
expectation is that the response amplitude should peak exactly when the
drive frequency crosses 1 rad/s -- but because the sweep moves faster than
the lightly-damped system can fully build up its steady-state resonant
amplitude, the actual peak response happens measurably BEFORE the drive
frequency reaches the natural frequency, at a noticeably lower frequency
and a smaller amplitude than the idealized steady-state resonance formula
would predict. This is a genuinely non-ideal result, in the same spirit as
the fan case in this folder, but for a dynamic (time-varying) rather than
static reason.

- Mass: 1 kg. Spring: stiffness 1 N/m (natural frequency
  `omega_n = sqrt(k/m) = 1 rad/s`). Damper: 0.1 N*s/m (damping ratio
  `zeta = 0.05`).
- No force is applied from t = 0 to t = 5 s; the mass starts at rest at
  its equilibrium (position 0 m, velocity 0 m/s) and stays there.
- From t = 5 s onward, an external force `F(t) = 0.05 * sin(omega(t) * t)`
  N is applied, where the drive frequency `omega(t)` itself increases
  linearly with time: `omega(t) = 0.5 + (1.0/300) * (t - 5)` rad/s for
  `5 <= t <= 305` s, reaching 1.5 rad/s at t = 305 s and then holding at
  1.5 rad/s for the remainder of the run.
- Governing equation from t = 5 s onward:
  `m*d^2(x)/dt^2 + c*dx/dt + k*x = F(t)`, starting from x = 0 m and
  velocity 0 m/s at t = 5 s.

## Requirements

- REQ-SIM-001: Simulate for 310 seconds and report the mass's position and
  the instantaneous drive frequency for the whole run.
- REQ-FUN-001: The mass shall stay at rest until t = 5 s, then begin
  responding to the swept sinusoidal force.
- REQ-FUN-002: The response amplitude shall grow as the drive frequency
  approaches the natural frequency, reach a peak, and then shrink again as
  the drive frequency continues past the natural frequency.
- REQ-FUN-003: The peak response amplitude shall occur while the
  instantaneous drive frequency is still measurably BELOW the 1 rad/s
  natural frequency -- not at or after it -- because the sweep moves
  faster than the system's own decay time (`1/(zeta*omega_n) = 20 s`) can
  fully track.

## Acceptance checks

- AC-01 at rest before forcing begins: `mass_position_m == 0.0` at
  t = 4 s.
- AC-02 drive frequency starts at 0.5 rad/s and increases: `drive_freq_
  rad_s == 0.5` at t = 5 s, and `drive_freq_rad_s == 1.15` at t = 200 s
  (absolute tolerance 0.01).
- AC-03 visible response builds up well before the natural frequency is
  reached: `abs(mass_position_m) >= 0.15` becomes true at some point
  between t = 70 s and t = 100 s (ever value == 1.0).
- AC-04 peak amplitude reaches at least 0.35 m: `abs(mass_position_m) >=
  0.35` becomes true at some point during the run (ever value == 1.0).
  Expected peak about 0.384 m at about t = 95.0 s.
- AC-05 the peak occurs while drive frequency is still below the natural
  frequency, not after it: at t = 95.0 s, `drive_freq_rad_s <= 0.85` --
  expected drive frequency at the peak is about 0.80 rad/s, clearly below
  the 1.0 rad/s natural frequency.
- AC-06 amplitude has clearly fallen back down by the time the sweep
  finishes: `abs(mass_position_m) <= 0.05` holds for the entire interval
  t = 250 s to t = 310 s -- confirms the response is NOT still growing or
  peaking again near the nominal resonance frequency at the end of the
  sweep.

## Notes

- This is the one case in this folder where the acceptance checks
  describe a genuinely counter-intuitive result on purpose: do not
  "correct" the peak-frequency check to land exactly at 1.0 rad/s. The
  peak location and amplitude above were found by direct RK4 numerical
  integration of the exact forced equation with the exact swept-frequency
  force term, not by the idealized steady-state resonance formula
  `amplitude = F0/(2*zeta*k) = 0.5 m`, which this run does not reach
  because the sweep never holds still long enough at any one frequency
  for the amplitude to fully build up to that steady-state value.
- Implement `omega(t)` as a plain time-varying expression (using the
  simulation's own `time` variable) feeding directly into the sine, not as
  a separately-integrated phase state, unless a phase-continuous chirp is
  specifically needed -- this brief's force expression is written directly
  in terms of `omega(t)*t`, and the generated model should match that
  exact expression rather than substitute an equivalent-looking but
  different chirp formulation.
- There is no damping-ratio or stiffness change anywhere in this run --
  only the drive frequency changes over time, and only during t = 5 s to
  t = 305 s.
