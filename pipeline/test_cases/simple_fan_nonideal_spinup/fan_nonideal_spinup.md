# Fan Spin-Up — Real Losses Keep It Below Its Rated Speed

## System

A single fan wheel is mounted on a shaft with its own rotational inertia.
A motor applies a fixed, constant driving torque to that shaft starting at
a fixed time; before that, the motor is off and the fan is at rest. The
fan's nameplate rates it for 30 rad/s under idealized, no-loss conditions --
but this model includes the two loss mechanisms a real fan actually has,
so the simulation is expected to show the fan settling BELOW its rated
speed, not at it. This is deliberately not an idealized result: it exists
to show what a non-ideal machine's simulated performance looks like
compared to its nameplate rating.

- Fan + shaft rotational inertia: J = 0.02 kg*m^2.
- Motor torque: a constant 0.5 N*m, applied starting at t = 5 s. Before
  t = 5 s the motor is off (zero torque) and the fan is at rest (speed
  0 rad/s).
- Bearing friction (a real loss an idealized fan model would ignore):
  linear viscous torque opposing rotation, `T_friction = b * omega`, with
  b = 0.01 N*m*s/rad.
- Aerodynamic load (the other real loss): the air the fan is moving pushes
  back with a torque that grows with the SQUARE of speed, the standard fan
  affinity-law relationship, `T_aero = k_fan * omega^2`, with
  k_fan = 0.0004 N*m*s^2/rad^2.
- Governing equation once the motor is on:
  `J * domega/dt = T_motor - b*omega - k_fan*omega^2`, starting from
  omega = 0 rad/s at the instant the motor turns on.
- Rated/nameplate speed (an idealized reference value the datasheet
  quotes, representing what the fan would reach with NEITHER loss term
  present -- not a value this model should ever actually reach): 30 rad/s.
- No controller, no speed feedback, and no torque change of any kind after
  t = 5 s: the motor simply holds its one constant torque value for the
  rest of the run, and the fan's own physics (inertia against a growing
  aerodynamic load) is what brings it to rest at a lower, real equilibrium
  speed than the rated value.

## Requirements

- REQ-SIM-001: Simulate for 60 seconds and report the fan's angular speed,
  the motor's on/off command, and the applied motor torque for the whole
  run.
- REQ-FUN-001: While the motor is off (t = 0 to t = 5 s), the fan's speed
  shall stay exactly at 0 rad/s.
- REQ-FUN-002: At t = 5 s the motor shall turn on and the fan shall begin
  spinning up under the stated torque balance, with speed increasing from
  0 rad/s.
- REQ-FUN-003: The fan's speed shall rise smoothly toward a real
  steady-state equilibrium and shall NOT reach, and shall stay strictly
  below, the 30 rad/s rated/nameplate speed for the entire run -- the
  friction and aerodynamic loss terms are what make this a non-ideal,
  realistic result rather than the idealized nameplate figure.
- REQ-FUN-004: Given the stated torque, friction coefficient, and
  aerodynamic coefficient, the fan shall settle at a steady-state speed of
  25 rad/s (where motor torque exactly balances the combined friction and
  aerodynamic load) and hold there for the remainder of the run.

## Acceptance checks

- AC-01 fan at rest before motor starts: `fan_speed_rad_s == 0` at t = 4 s.
- AC-02 motor off pre-start, on after: `motor_on_cmd == 0` at t = 4 s, and
  `motor_on_cmd == 1` at t = 6 s.
- AC-03 fast initial spin-up: `fan_speed_rad_s >= 15.0` at t = 6 s (1 s
  after the motor turns on) -- expected value is about 17.47 rad/s.
- AC-04 close to steady state well before the run ends: `abs(fan_speed_rad_s
  - 25.0) <= 0.5` at t = 10 s (5 s after start) -- expected value is about
  24.98 rad/s, already 99.9% of the way to equilibrium.
- AC-05 settled at the real (non-ideal) equilibrium: `fan_speed_rad_s ==
  25.0` at t = 60 s (absolute tolerance 0.05 rad/s).
- AC-06 never reaches the idealized rated speed, for the entire run once
  the motor is on: `fan_speed_rad_s <= 29.9` holds at all times from
  t = 5 s to t = 60 s -- the whole point of this case: the result stays
  meaningfully below the 30 rad/s nameplate value, not at or above it.
- AC-07 no overshoot past the real equilibrium: `fan_speed_rad_s <= 25.05`
  holds at all times for the entire run -- unlike an underdamped
  spring-mass system, this nonlinear, purely-dissipative spin-up rises
  smoothly and never exceeds its own steady-state value.
- AC-08 torque balance holds at steady state: `motor_torque_Nm -
  (0.01*fan_speed_rad_s + 0.0004*fan_speed_rad_s^2) == 0` at t = 60 s
  (absolute tolerance 0.01 N*m) -- confirms the reported speed is
  consistent with the stated friction and aerodynamic loss terms, not just
  a plausible-looking number.

## Notes

- This is the third first-time domain in this folder (after the two-tank
  gravity case and the spring-mass release case): a rotational
  mechanical system driven to a NONLINEAR equilibrium, because the
  aerodynamic load term is quadratic in speed, not linear. The rise to
  equilibrium is smooth and monotonic (no overshoot, unlike the spring-mass
  case) but does not have a closed-form exponential solution the way the
  two-tank case does -- the acceptance-check values above were computed by
  direct numerical integration (RK4) of the stated ODE, not estimated.
- The point of this case is specifically to demonstrate a NON-ideal
  simulated result: a naive or idealized model would just report the
  30 rad/s nameplate speed once the motor is on. A correct model of this
  brief must show the fan falling meaningfully short of that number
  because of the two loss terms this brief explicitly states -- a model
  that reports fan_speed_rad_s reaching 30 rad/s has dropped the friction
  and/or aerodynamic terms and should be treated as wrong, not as an
  idealized best case.
- There is exactly one event in this run (the motor turning on once, and
  never off again, never changing torque). No feedback controller, no
  speed governor, and no second event of any kind belong in this model.
