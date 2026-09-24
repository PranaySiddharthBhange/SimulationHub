# Series RLC Ringing — Pre-Charged Capacitor Released Into A Resistor And Inductor

## System

A capacitor is charged to a fixed voltage and held there by an open
switch. The switch closes once, at a fixed time, connecting the capacitor
into a loop with a resistor and an inductor in series. From that instant
the capacitor discharges through the loop with no external source of any
kind -- the electrical analog of the spring-mass-release case in this same
folder, and it should show the same underdamped shape: the capacitor
voltage overshoots past zero and rings before settling, rather than
discharging smoothly to zero.

- Capacitor: C = 1 F, charged to 10 V and held there (switch open) from
  t = 0 to t = 5 s.
- Switch: open (no current can flow) from t = 0 to t = 5 s. Closes once at
  t = 5 s and never opens again for the rest of the run.
- Resistor: R = 0.2 Ohm, in series with the inductor once the switch
  closes.
- Inductor: L = 1 H, in series with the resistor once the switch closes.
- Governing equation once the switch closes:
  `L*C*d^2(v_C)/dt^2 + R*C*d(v_C)/dt + v_C = 0`, starting from
  v_C = 10 V and current 0 A at the instant of closing.
- Nothing else acts on this loop at any point: no source, no second
  switch event, no controller.

## Requirements

- REQ-SIM-001: Simulate for 150 seconds and report the capacitor voltage,
  the loop current, and the switch's open/closed state for the whole run.
- REQ-FUN-001: While the switch is open (t = 0 to t = 5 s), capacitor
  voltage shall stay exactly at 10 V and current shall stay exactly at 0 A.
- REQ-FUN-002: At t = 5 s the switch shall close once, and capacitor
  voltage shall begin falling from 10 V.
- REQ-FUN-003: Given the stated R, L, C values, the response shall be
  underdamped: capacitor voltage shall swing negative (overshoot past
  0 V) before settling, rather than decaying monotonically to zero.
- REQ-FUN-004: The ringing shall decay over time and the capacitor voltage
  shall settle at 0 V well before the end of the run.

## Acceptance checks

- AC-01 switch open pre-close: `switch_closed == 0` at t = 4 s.
- AC-02 voltage and current frozen while open: `capacitor_voltage_V ==
  10.0` and `loop_current_A == 0.0` at t = 4 s (absolute tolerance 0.01).
- AC-03 switch closes on schedule: `switch_closed == 1` at t = 6 s.
- AC-04 voltage overshoots past zero (confirms genuine ringing, not a
  smooth discharge): `capacitor_voltage_V <= -5.0` becomes true at some
  point during the run (ever value == 1.0). Expected around t = 8.16 s,
  where voltage reaches about -7.29 V.
- AC-05 current is near zero at the overshoot trough: `abs(loop_current_A)
  <= 0.05` at t = 8.16 s -- the loop momentarily stops discharging there
  before ringing back.
- AC-06 crosses zero before the overshoot trough: `capacitor_voltage_V <=
  0.0` becomes true at some point between t = 5 s and t = 8 s (ever value
  == 1.0). Expected around t = 6.68 s.
- AC-07 settled by the end of the run: `capacitor_voltage_V == 0.0` and
  `loop_current_A == 0.0` at t = 150 s (absolute tolerance 0.05).
- AC-08 stays settled, not still ringing: `abs(capacitor_voltage_V) <=
  0.3` holds for the entire interval t = 50 s to t = 150 s.

## Notes

- This case is the electrical counterpart to `simple_spring_mass_release`
  in this same folder, by direct analogy (`L <-> m`, `R <-> c`,
  `1/C <-> k`). The damping ratio and natural frequency are identical:
  `zeta = (R/2)*sqrt(C/L) = 0.1`, `omega_n = 1/sqrt(L*C) = 1 rad/s`, so
  every acceptance-check timing above is the same closed-form solution
  used there, scaled by the 10 V starting voltage instead of 0.10 m --
  confirmed numerically, not estimated.
- `Modelica.Electrical.Analog` provides the resistor, inductor, capacitor,
  and ideal switch components this case needs directly; there is no
  reason to hand-roll the electrical equations here.
- There is exactly one event in this run (the switch closing once).
  Nothing re-opens the switch, and no source is ever connected again.
