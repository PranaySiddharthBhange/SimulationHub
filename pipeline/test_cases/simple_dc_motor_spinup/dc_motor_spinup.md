# DC Motor Spin-Up — Electrical And Mechanical Domains Coupled Together

## System

A DC motor's armature circuit (resistor and inductor in series, with a
back-EMF that depends on shaft speed) drives a rotational inertia against
viscous friction. A fixed voltage is applied to the armature starting at a
fixed time; before that, the motor is unpowered and at rest. This is
deliberately a TWO-DOMAIN case -- the electrical current and the
mechanical speed are coupled to each other through the same two equations
at every instant, unlike every other case in this folder, which stays in
one domain at a time. Because the armature has real inductance, current
and speed both overshoot their final values before settling, rather than
rising smoothly to steady state.

- Armature resistance: R_a = 1 Ohm.
- Armature inductance: L_a = 0.5 H.
- Back-EMF constant: k_e = 0.1 V*s/rad.
- Torque constant: k_t = 0.1 N*m/A (numerically equal to k_e, as required
  by energy conservation in SI units).
- Rotor + load inertia: J = 0.01 kg*m^2.
- Mechanical (viscous) friction: b_m = 0.01 N*m*s/rad.
- Applied armature voltage: 0 V from t = 0 to t = 5 s (motor off, at
  rest); a constant 12 V from t = 5 s onward, held for the rest of the
  run.
- Governing equations, from t = 5 s onward:
  `L_a * di/dt = V - R_a*i - k_e*omega`,
  `J * domega/dt = k_t*i - b_m*omega`,
  starting from i = 0 A and omega = 0 rad/s at t = 5 s. There is no
  separate mechanical load beyond the stated friction term.

## Requirements

- REQ-SIM-001: Simulate for 60 seconds and report armature current, shaft
  angular speed, and the applied voltage command for the whole run.
- REQ-FUN-001: While the applied voltage is 0 V (t = 0 to t = 5 s), current
  and speed shall both stay exactly at 0.
- REQ-FUN-002: At t = 5 s the voltage shall step to 12 V, and both current
  and speed shall begin rising from 0.
- REQ-FUN-003: Given the stated R_a, L_a, k_e, k_t, J, and b_m, both
  current and speed shall overshoot their eventual steady-state values
  before settling -- this is a genuinely coupled second-order response,
  not two independent first-order rises.
- REQ-FUN-004: The motor shall settle at a steady-state speed of 60 rad/s
  and a steady-state current of 6 A (where applied voltage exactly balances
  resistive drop, back-EMF, and friction losses) and hold there for the
  remainder of the run.

## Acceptance checks

- AC-01 at rest before power is applied: `motor_speed_rad_s == 0` and
  `armature_current_A == 0` at t = 4 s.
- AC-02 voltage command state: `applied_voltage_V == 0` at t = 4 s, and
  `applied_voltage_V == 12` at t = 6 s.
- AC-03 fast initial current rise: `armature_current_A >= 7.0` at
  t = 5.5 s (0.5 s after power is applied) -- expected value is about
  7.05 A.
- AC-04 speed overshoots its own steady-state value (confirms genuine
  coupled second-order behavior, not a simple first-order rise):
  `motor_speed_rad_s >= 61.0` becomes true at some point during the run
  (ever value == 1.0). Expected peak of about 61.70 rad/s at about
  t = 7.375 s.
- AC-05 current also overshoots before settling: `armature_current_A >=
  8.0` becomes true at some point between t = 5.5 s and t = 6.5 s (ever
  value == 1.0). Expected peak of about 8.12 A near t = 6.0 s.
- AC-06 settled current at steady state: `armature_current_A == 6.0` at
  t = 60 s (absolute tolerance 0.02 A).
- AC-07 settled speed at steady state: `motor_speed_rad_s == 60.0` at
  t = 60 s (absolute tolerance 0.05 rad/s).
- AC-08 power balance at steady state: `applied_voltage_V*armature_current_A
  - armature_current_A^2*1.0 - motor_speed_rad_s^2*0.01 == 0` at t = 60 s
  (absolute tolerance 0.5 W) -- electrical power in equals resistive loss
  plus friction loss once settled, with no armature-inductance or
  inertia term left over.

## Notes

- The coupled system's eigenvalues (computed directly from the two
  equations' 2x2 state matrix) are `-1.5 +/- 1.323j`, confirming this
  response is genuinely underdamped/oscillatory before settling, not
  merely fast -- the overshoot figures above come from direct RK4
  integration of the coupled pair, not from treating current and speed as
  independent.
- `Modelica.Electrical.Analog` and `Modelica.Mechanics.Rotational` do not
  need to be combined through a full `Modelica.Electrical.Machines` motor
  model for this brief -- the two coupled equations above are simple
  enough to write directly, and doing so keeps the electrical and
  mechanical sides' coupling (via k_e and k_t) explicit rather than hidden
  inside a library component's internals.
- There is exactly one event in this run (voltage turning on once, and
  never changing again). No speed controller, no current limiter, and no
  second voltage level belong in this model.
