# Two Tanks, One Above The Other — Gravity Flow To Equilibrium

## System

Two open tanks stand at different heights and are joined by a single pipe
with an on/off valve. Tank A is mounted physically above Tank B, so once the
valve opens, gravity drives liquid from A (higher level) down into B (lower
level) until their levels settle at a shared equilibrium — nothing keeps
pumping afterward, and nothing drains the pair from outside. There is no
operator command sequence and no controller: the valve is closed for a
fixed interval, then opens once, and stays open for the rest of the run.

- Tank A (upper): cross-sectional area 0.5 m^2, height 1.0 m, starts full to
  0.80 m at t = 0.
- Tank B (lower): cross-sectional area 0.5 m^2, height 1.0 m, starts empty
  (level = 0 m) at t = 0.
- Connecting valve: closed from t = 0 to t = 5 s (no flow, both levels held
  at their starting values). At t = 5 s the valve opens once and never
  closes again for the rest of the run.
- Once open, the connecting flow is driven by the two tanks' own level
  difference: `q = k * (level_A - level_B)`, with `k = 0.025 m^2/s`. Flow
  runs from A to B while `level_A > level_B` and relaxes toward zero as the
  difference closes -- there is no pump and no fixed nominal rate once the
  valve is open, unlike a supply-fed fill.
- The two tanks have equal area and no other inflow or outflow anywhere in
  the system, so total liquid volume is conserved for the whole run:
  `level_A + level_B` is constant at 0.80 m from t = 0 onward, before and
  after the valve opens.

## Requirements

- REQ-SIM-001: Simulate for 150 seconds and report both tank levels and the
  connecting valve's open/closed command for the whole run.
- REQ-FUN-001: The valve shall stay closed and both levels shall stay
  exactly at their starting values (0.80 m and 0.00 m) for the entire
  closed interval, t = 0 to t = 5 s.
- REQ-FUN-002: At t = 5 s the valve shall open and flow shall begin from
  Tank A into Tank B, so Tank A's level falls and Tank B's level rises from
  that point on.
- REQ-FUN-003: Given equal tank areas and the stated conductance `k`, the
  system shall relax toward a shared equilibrium level of 0.40 m in each
  tank (the starting 0.80 m of liquid split evenly across two equal-area
  tanks) and shall stay there for the remainder of the run once reached.

## Acceptance checks

- AC-01 valve closed pre-open: `valve_open_cmd == 0` at t = 4 s.
- AC-02 levels frozen while closed: `level_A_m == 0.80` and
  `level_B_m == 0.00` at t = 4 s (absolute tolerance 0.001 m) -- unchanged
  from the initial condition right up to the moment before the valve opens.
- AC-03 valve opens on schedule: `valve_open_cmd == 1` at t = 6 s (one
  second after the scheduled open time, clear of the switching instant
  itself).
- AC-04 flow has visibly started: `level_A_m <= 0.75` and
  `level_B_m >= 0.05` at t = 15 s (10 s after the valve opened) -- Tank A
  is draining and Tank B is filling.
- AC-05 approaching equilibrium: `abs(level_A_m - 0.40) <= 0.02` and
  `abs(level_B_m - 0.40) <= 0.02` at t = 45 s (40 s after the valve opened,
  four time constants given `tau = area / (2*k) = 10 s`).
- AC-06 settled at equilibrium: `level_A_m == 0.40` and `level_B_m == 0.40`
  at t = 150 s (absolute tolerance 0.005 m) -- both tanks have visibly
  stopped moving by the end of the run.
- AC-07 volume conservation, the whole run: `level_A_m + level_B_m == 0.80`
  holds at all times (absolute tolerance 0.001 m), from t = 0 through
  t = 150 s -- no liquid appears or disappears anywhere in this system,
  valve open or closed.
- AC-08 no overflow/underflow: `level_A_m >= 0` and `level_A_m <= 1.0`, and
  `level_B_m >= 0` and `level_B_m <= 1.0`, hold for the entire run.

## Notes

- This case has exactly one discrete event (the valve opening once, never
  closing again) and one continuous relaxation afterward, so it
  deliberately has no controller, no setpoint, no pause/resume behavior,
  and no second command. It exists to exercise gravity-driven flow between
  two vessels and a genuine asymptotic equilibrium, neither of which the
  single-tank-fill or sequenced-valve cases in this folder cover.
- Equal tank areas were chosen deliberately so the equilibrium level
  (0.40 m each) and the conservation identity (`level_A + level_B = 0.80`)
  are both exact, closed-form numbers to check against -- not because equal
  areas are required by the physics. A future variant with unequal areas
  would still conserve total VOLUME (`A_A*level_A + A_B*level_B` constant),
  just not total level.
- "Tank A mounted above Tank B" is the physical framing for why gravity
  drives flow from A to B once the valve opens; the model itself only needs
  each tank's own level and the stated level-difference-driven flow law, not
  a separate elevation state -- there is no requirement to model absolute
  pipe geometry or hydrostatic pressure explicitly.
