# Large-Angle Pendulum — Genuine Nonlinearity, Not The Small-Angle Approximation

## System

A simple pendulum -- a point mass on a massless rigid rod of fixed length,
pivoting freely with no friction at the pivot -- is released from rest at
a large starting angle and swings under gravity alone. The starting angle
is large enough (90 degrees from vertical) that the true motion visibly
disagrees with the familiar small-angle formula: the real period is about
18% longer than the small-angle estimate. This case exists specifically to
check that a generated model keeps the exact nonlinear restoring term
rather than silently linearizing it the way the small-angle approximation
would.

- Pendulum length: L = 1 m.
- Gravity: g = 9.81 m/s^2.
- No friction anywhere (pivot or air) -- the swing does not decay in this
  case; it is a genuinely conservative system.
- Starting condition: angle = 90 degrees (pi/2 rad) from the vertical
  (straight down = 0), released from rest (angular velocity 0 rad/s) at
  t = 0.
- Governing equation (the exact nonlinear pendulum equation -- do not
  substitute the small-angle `sin(theta) ~= theta` approximation):
  `d^2(theta)/dt^2 = -(g/L) * sin(theta)`.
- Angle convention: 0 rad is straight down (the pendulum's rest position);
  positive and negative angles are the two sides of the swing.

## Requirements

- REQ-SIM-001: Simulate for 12 seconds and report the pendulum's angle and
  angular velocity for the whole run.
- REQ-FUN-001: Released from 90 degrees at rest, the pendulum shall swing
  down through vertical and reach the opposite side, coming momentarily to
  rest again near -90 degrees, before swinging back.
- REQ-FUN-002: With no friction anywhere, the pendulum shall keep swinging
  between approximately +90 degrees and -90 degrees for the entire run,
  never settling and never exceeding its starting amplitude.
- REQ-FUN-003: The true (nonlinear) period of this swing shall be
  noticeably longer than the small-angle estimate `2*pi*sqrt(L/g)` =
  2.006 s -- specifically, the time for the pendulum to first reach its
  momentary rest on the opposite side shall be close to 1.18 s
  (half of a period of about 2.37 s), not close to 1.00 s (half of the
  small-angle period).

## Acceptance checks

- AC-01 starts at the stated angle, at rest: `pendulum_angle_rad == 1.5708`
  and `pendulum_angular_vel_rad_s == 0.0` at t = 0 s (absolute tolerance
  0.001).
- AC-02 swings down through vertical: `pendulum_angle_rad <= 0.0` becomes
  true at some point between t = 0.4 s and t = 0.9 s (ever value == 1.0).
- AC-03 reaches the far side close to the true nonlinear period, not the
  small-angle estimate: `pendulum_angle_rad <= -1.55` becomes true at some
  point between t = 1.10 s and t = 1.26 s (ever value == 1.0). Expected at
  about t = 1.184 s. (A model that used the small-angle approximation
  instead of the true nonlinear equation would reach this point closer to
  t = 1.00 s and fail this window.)
- AC-04 momentarily at rest at the far side: `abs(pendulum_angular_vel_rad_s)
  <= 0.05` at t = 1.184 s.
- AC-05 never exceeds its own starting amplitude, for the whole run:
  `pendulum_angle_rad <= 1.58` and `pendulum_angle_rad >= -1.58` hold at
  all times from t = 0 s to t = 12 s -- a frictionless pendulum released
  from rest cannot swing higher than its release point.
- AC-06 still swinging near the end of the run, not damped out: at
  t = 11 s, `abs(pendulum_angular_vel_rad_s) >= 0.5` -- confirms the
  amplitude has not decayed (there is no friction to decay it), unlike
  every damped case in this folder.
- AC-07 completes a second full swing back past the far side: `pendulum_
  angle_rad <= -1.55` becomes true again at some point between t = 3.4 s
  and t = 3.7 s (ever value == 1.0, evaluated as a second occurrence)
  -- confirms a full nonlinear period (about 2.37 s) has elapsed since the
  first far-side arrival at t = 1.184 s.

## Notes

- Every timing figure above (1.184 s to the far side, ~2.37 s true
  period) was computed by direct RK4 numerical integration of the exact
  nonlinear equation, not from the small-angle approximation and not
  estimated by eye -- confirmed against the elliptic-integral correction
  known for a 90-degree amplitude (about an 18% longer period than the
  small-angle estimate, which matches).
- This case has no damping and no external torque at any point -- unlike
  most of this folder, it is not asking for an equilibrium or a settled
  final state, but for a SUSTAINED, undamped, nonlinear oscillation that
  keeps going for the entire run.
- `Modelica.Mechanics.Rotational` components model torque/inertia/damping
  directly but do not have a built-in gravity-pendulum block; the
  `sin(theta)` restoring term is simple and explicit enough to write as a
  plain differential equation on the angle, which is the simplest correct
  way to represent this brief.
