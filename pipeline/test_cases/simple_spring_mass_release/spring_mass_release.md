# Held Mass Released Onto A Spring-Damper — Underdamped Oscillation To Rest

## System

A single mass slides horizontally on a frictionless surface, anchored to a
fixed wall through a spring and a damper acting in parallel. A clamp holds
the mass at a fixed, stretched position away from the spring's natural
length for the first part of the run. The clamp releases once, at a fixed
time, and never re-engages: from that instant on, the mass moves freely
under the spring's restoring force and the damper's resistance alone, with
no other force acting on it.

This is a genuinely different kind of behavior from every other case in
this folder: it is second-order (position AND velocity both matter, not
just an accumulating level), the chosen damping is light enough that the
mass overshoots the spring's natural length and swings to the opposite
side before settling, and it never truly reaches its final rest position --
only decays toward it asymptotically.

- Mass: 1 kg, sliding with no friction against the surface itself (the
  damper is the only source of resistance).
- Spring: stiffness 1 N/m, unstretched (zero force) at position x = 0 m.
  Connects the mass to the fixed wall.
- Damper: damping coefficient 0.2 N*s/m, connects the mass to the same
  fixed wall, in parallel with the spring.
- Clamp: holds the mass fixed at position x = 0.10 m (stretched 0.10 m from
  the spring's natural length) with zero velocity, from t = 0 to t = 5 s.
  At t = 5 s the clamp releases once and never re-engages for the rest of
  the run; from that instant, position and velocity evolve solely from the
  spring and damper forces (`m*x'' + c*x' + k*x = 0`, starting from
  x = 0.10 m and velocity 0 m/s at the instant of release).
- No external force, motor, or controller acts on the mass at any point in
  this run -- once released, the system evolves on its own.

## Requirements

- REQ-SIM-001: Simulate for 150 seconds and report the mass's position,
  its velocity, and the clamp's engaged/released state for the whole run.
- REQ-FUN-001: While the clamp is engaged (t = 0 to t = 5 s), position
  shall stay exactly at 0.10 m and velocity shall stay exactly at 0 m/s.
- REQ-FUN-002: At t = 5 s the clamp shall release once, and the mass shall
  begin moving back toward the spring's natural length (position
  decreasing from 0.10 m, velocity going negative).
- REQ-FUN-003: Given the stated mass, stiffness, and damping, the motion
  shall be underdamped: the mass shall overshoot past the natural length
  (position goes negative) before eventually settling there, rather than
  approaching 0 m monotonically.
- REQ-FUN-004: The oscillation shall decay over time and the mass shall
  come to rest at the spring's natural length (position 0 m, velocity
  0 m/s) well before the end of the simulated run.

## Acceptance checks

- AC-01 clamp engaged pre-release: `clamp_engaged == 1` at t = 4 s.
- AC-02 position and velocity frozen while clamped: `position_m == 0.10`
  and `velocity_m_s == 0.0` at t = 4 s (absolute tolerance 0.001).
- AC-03 clamp releases on schedule: `clamp_engaged == 0` at t = 6 s (one
  second after the scheduled release, clear of the switching instant
  itself).
- AC-04 mass moving back toward natural length right after release:
  `velocity_m_s <= -0.04` at t = 6 s (the mass is moving in the negative
  direction at meaningful speed shortly after release).
- AC-05 overshoot past the natural length (confirms genuine underdamped
  behavior, not just decay to zero): `position_m <= -0.05` becomes true at
  some point during the run (ever value == 1.0). Expected around
  t = 8.16 s, where position reaches about -0.0729 m.
- AC-06 velocity returns to zero at the overshoot peak: `abs(velocity_m_s)
  <= 0.01` at t = 8.16 s -- the mass momentarily stops there before
  swinging back.
- AC-07 oscillation crosses the natural length before the overshoot peak:
  `position_m <= 0.0` becomes true at some point before t = 8 s (ever
  value == 1.0, checked over 5 s to 8 s). Expected around t = 6.68 s.
- AC-08 settled at rest by the end of the run: `position_m == 0.0` and
  `velocity_m_s == 0.0` at t = 150 s (absolute tolerance 0.005) -- the
  oscillation has fully decayed.
- AC-09 stays settled, not still oscillating: `abs(position_m) <= 0.003`
  holds for the entire interval t = 50 s to t = 150 s -- by t = 50 s
  (45 s after release, well past the point the envelope decays under the
  0.2% band) the motion must already be negligible and must not grow again.

## Notes

- This case is deliberately the mechanical counterpart to the gravity-flow
  two-tank case in this same folder: both hold a state fixed, release it
  once at t = 5 s, and let the system relax on its own with no further
  input. The two-tank case is strictly first-order and monotonic (no
  overshoot is possible, by construction); this case is second-order and
  underdamped specifically so it overshoots and oscillates before settling
  -- a dynamic shape nothing else in this folder exercises.
- The damping ratio here is `zeta = c / (2*sqrt(k*m)) = 0.2 / (2*sqrt(1*1))
  = 0.1`, and the undamped natural frequency is `omega_n = sqrt(k/m) =
  1 rad/s`, giving a damped frequency `omega_d = omega_n*sqrt(1-zeta^2) ~=
  0.995 rad/s` -- all the acceptance-check timings above were computed
  directly from the closed-form solution `x(t) = x0 * exp(-zeta*omega_n*dt)
  * (cos(omega_d*dt) + (zeta*omega_n/omega_d)*sin(omega_d*dt))`, dt = t -
  5 s, not estimated.
- There is exactly one event in this whole run (the clamp releasing once).
  Nothing re-engages the clamp, and no external force is ever applied
  again -- any generated model that keeps forcing position or velocity to
  a fixed value after t = 5 s, or that adds an external force/controller
  not stated here, has added something this brief does not call for.
