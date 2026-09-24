# Bouncing Ball — Repeated Impact Events With Energy Loss

## System

A ball is dropped from a fixed height above the ground with zero initial
velocity and falls freely under gravity. Each time it hits the ground it
bounces, losing a fixed fraction of its speed at every impact (a
coefficient of restitution), so each successive bounce reaches a lower
peak height than the one before. This is deliberately event-heavy in a way
nothing else in this folder is: instead of one switching event, it has a
whole sequence of impact events, each one reversing and shrinking the
ball's velocity, with no motor, valve, or controller involved anywhere.

- Ball: point mass, drops from height 5 m above the ground, starting at
  rest (velocity 0 m/s) at t = 0.
- Gravity: g = 9.81 m/s^2, constant, acting downward for the whole run.
- Ground: a hard, fixed, flat surface at height 0 m. The ball never passes
  through it.
- Coefficient of restitution: e = 0.7. At the instant of each impact
  (height = 0, moving downward), the ball's velocity reverses sign and is
  scaled by e: `v_after = -e * v_before`. This is the only thing that
  happens at an impact -- height itself does not jump, only velocity.
- Between impacts the ball is in free fall: `d^2(height)/dt^2 = -g`. There
  is no air resistance and no horizontal motion in this case.

## Requirements

- REQ-SIM-001: Simulate for 10 seconds and report the ball's height and
  velocity for the whole run.
- REQ-FUN-001: Starting at 5 m with zero velocity, the ball shall fall
  freely and strike the ground for the first time at approximately
  t = 1.01 s.
- REQ-FUN-002: At each impact, the ball's velocity shall reverse direction
  and its magnitude shall reduce to 70% of the impact speed (the stated
  coefficient of restitution), and the ball shall never go below height
  0 m at any point in the run.
- REQ-FUN-003: Each successive bounce shall reach a lower peak height than
  the previous one, following `height_peak_n = 5 * (0.7)^(2*n)` for the
  n-th peak after the drop.
- REQ-FUN-004: The ball shall never rise back above its most recent peak
  height between bounces, and the peak heights shall keep shrinking for as
  long as the run continues.

## Acceptance checks

- AC-01 stays airborne, falling, before the first impact: `ball_height_m >
  0` holds for all t from 0 s to 1.0 s.
- AC-02 first impact near the expected time: `ball_height_m <= 0.02`
  becomes true at some point between t = 0.95 s and t = 1.05 s (ever value
  == 1.0). Expected at t = 1.0096 s.
- AC-03 never penetrates the ground, for the entire run: `ball_height_m >=
  -0.001` holds at all times from t = 0 s to t = 10 s.
- AC-04 first bounce reaches the expected peak: `abs(ball_height_m - 2.45)
  <= 0.05` becomes true at some point between t = 1.6 s and t = 1.85 s
  (ever value == 1.0). Expected peak height 2.45 m at t = 1.7164 s.
- AC-05 second bounce reaches a smaller, expected peak: `abs(ball_height_m
  - 1.2005) <= 0.03` becomes true at some point between t = 2.8 s and
  t = 3.05 s (ever value == 1.0). Expected peak height 1.2005 m at
  t = 2.9179 s.
- AC-06 each bounce is lower than the one before, for at least the first
  two: `2.45 > 1.2005` -- i.e. treat the two peak values found for AC-04
  and AC-05 as evidence and confirm the second is smaller than the first
  (this is a property of the reported trajectory, not a single-instant
  check).
- AC-07 effectively at rest on the ground well before the run ends:
  `ball_height_m <= 0.05` and `abs(ball_velocity_m_s) <= 0.3` both hold
  for the entire interval t = 8 s to t = 10 s.

## Notes

- This is a classic hard case for event-based simulation on purpose: in
  the idealized physics, the ball bounces infinitely many times in a
  finite total time (about 5.72 s, from `t1*(1+e)/(1-e)` with
  `t1 = 1.0096 s` the first-impact time) -- a Zeno phenomenon, since each
  bounce's duration shrinks by a factor of `e` from the last. A real
  simulation cannot literally resolve infinitely many events, so the
  generated model will need SOME practical resolution (for example,
  treating the ball as at rest once its bounce height or speed drops below
  a small stated threshold) rather than attempting to step through every
  bounce individually forever. That resolution is left to the modeling
  stage; this brief only requires the first two bounces to match the exact
  physics and the ball to be settled by t = 8 s.
- Use `reinit()` on the velocity state at the impact event (detected by a
  zero-crossing on height while moving downward), not a fresh initial
  condition -- this is the standard Modelica idiom for an instantaneous
  velocity reversal at an impact, and avoids re-deriving the ball's
  position from scratch at every bounce.
- There is no horizontal motion, no air resistance, and no second ball or
  surface in this case -- it is deliberately the simplest possible impact
  scenario, to isolate the repeated-event handling from any other
  complexity.
