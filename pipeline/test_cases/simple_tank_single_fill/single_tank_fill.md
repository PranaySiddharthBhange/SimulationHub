# Single Tank Fill — One Valve, One Threshold

## System

One atmospheric, open tank is filled from a single supply through one inlet
valve. There is no operator command, no second tank, and no multi-step
sequence: the valve is simply open whenever the tank level is below its fill
target, and closed once the target is reached. Once closed, the valve never
reopens during this run (there is no drain and nothing lowers the level
again).

- Tank: cross-sectional area 0.5 m^2, height 1.0 m, empty at the start
  (level = 0 m at t = 0).
- Inlet valve: on/off, supplies a constant nominal inflow of 0.01 m^3/s
  (10 L/s) whenever it is open.
- Fill target: the valve closes as soon as the tank level reaches 0.80 m,
  and stays closed for the rest of the run.

## Requirements

- REQ-SIM-001: Simulate for 100 seconds and report the tank level and the
  inlet valve's open/closed command for the whole run.
- REQ-FUN-001: Starting from empty, the tank shall fill until its level
  reaches the 0.80 m fill target, at which point the inlet valve shall close
  and the level shall stop rising.

## Acceptance checks

- AC-01 fill target reached: `tank_level_m >= 0.80` becomes true at some
  point during the run (ever value == 1.0). Expected around t = 40 s, given
  a 0.5 m^2 tank area and a 0.01 m^3/s inflow (0.80 m * 0.5 m^2 / 0.01 m^3/s
  = 40 s).
- AC-02 no overfill: `tank_level_m <= 0.85` holds for the entire run (always
  value == 1.0) -- the level must not run away past the fill target.
- AC-03 valve open early: `valve_open_cmd == 1` at t = 5 s (the valve is open
  while the tank is still filling).
- AC-04 valve closed at the end: `valve_open_cmd == 0` at t = 100 s (the
  valve has closed after reaching the fill target and stayed closed).
- AC-05 final level holds the target: `tank_level_m == 0.80` at t = 100 s
  (absolute tolerance 0.01 m) -- once the valve closes, nothing changes the
  level again.

## Notes

- This case has exactly one state (the tank level) and exactly one
  transition (the valve closing once, never reopening), so it deliberately
  has no pause/resume behavior, no scheduled operator commands, and no
  second controlled unit.
