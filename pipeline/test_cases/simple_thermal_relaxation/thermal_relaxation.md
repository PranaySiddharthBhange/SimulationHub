# Two Thermal Masses Reaching A Shared Equilibrium Temperature

## System

Two solid blocks at different starting temperatures are brought into
thermal contact once, at a fixed time, through a fixed conductance -- for
example, an insulating layer between them is removed once and never
replaced. From that instant, heat conducts from the hotter block into the
colder one until both reach a single shared equilibrium temperature. This
is the pure-conduction, no-fluid-flow counterpart to the two-tank gravity
case in this folder: the same first-order relaxation mathematics, in the
thermal domain instead of the hydraulic one.

- Block A: heat capacity 1000 J/K, starts at 80 degC at t = 0.
- Block B: heat capacity 1000 J/K, starts at 20 degC at t = 0.
- Thermal contact: no heat flows between the blocks from t = 0 to t = 5 s
  (they are thermally isolated from each other, and each stays at its own
  starting temperature). At t = 5 s the contact is established once and
  never broken again, with a fixed conductance G = 50 W/K between them.
- Neither block exchanges heat with anything else (no ambient loss, no
  heater) -- the only heat path in this system, at any point in the run,
  is directly between Block A and Block B once contact is made.
- Governing equations from t = 5 s onward:
  `C_A * dT_A/dt = -G*(T_A - T_B)`,
  `C_B * dT_B/dt = +G*(T_A - T_B)`,
  starting from T_A = 80 degC and T_B = 20 degC at the instant contact is
  made.

## Requirements

- REQ-SIM-001: Simulate for 150 seconds and report both block temperatures
  and the contact's connected/isolated state for the whole run.
- REQ-FUN-001: While isolated (t = 0 to t = 5 s), both temperatures shall
  stay exactly at their starting values, 80 degC and 20 degC.
- REQ-FUN-002: At t = 5 s the contact shall be made once, and heat shall
  begin flowing from Block A (hotter) into Block B (colder), so Block A's
  temperature falls and Block B's temperature rises from that point on.
- REQ-FUN-003: Given the stated equal heat capacities and conductance, the
  two blocks shall relax toward a shared equilibrium temperature of
  50 degC (the average of the two starting temperatures, since the
  capacities are equal) and hold there for the remainder of the run.

## Acceptance checks

- AC-01 isolated pre-contact: `contact_made == 0` at t = 4 s.
- AC-02 temperatures frozen while isolated: `block_A_temp_C == 80.0` and
  `block_B_temp_C == 20.0` at t = 4 s (absolute tolerance 0.01).
- AC-03 contact made on schedule: `contact_made == 1` at t = 6 s.
- AC-04 heat is visibly flowing shortly after contact: `block_A_temp_C <=
  75.0` and `block_B_temp_C >= 25.0` at t = 15 s (10 s after contact) --
  expected values are about 61.04 degC and 38.96 degC.
- AC-05 approaching equilibrium: `abs(block_A_temp_C - 50.0) <= 1.0` and
  `abs(block_B_temp_C - 50.0) <= 1.0` at t = 45 s (40 s after contact,
  four time constants given `tau = C/(2*G) = 10 s`). Expected values are
  about 50.55 degC and 49.45 degC.
- AC-06 settled at equilibrium: `block_A_temp_C == 50.0` and
  `block_B_temp_C == 50.0` at t = 150 s (absolute tolerance 0.01 degC).
- AC-07 energy conservation, the whole run: `block_A_temp_C +
  block_B_temp_C == 100.0` holds at all times from t = 0 s to t = 150 s
  (absolute tolerance 0.01 degC) -- with equal heat capacities and no
  other heat path, total thermal energy (and hence the sum of the two
  temperatures) never changes, contact made or not.

## Notes

- This case is the deliberate thermal twin of `simple_two_tank_
  equilibrium` in this folder: identical relaxation mathematics
  (`tau = 10 s` in both cases), just with temperature and thermal
  conductance in place of tank level and hydraulic conductance. Every
  timing and value above reuses that same closed-form solution, verified
  numerically, not estimated.
- `Modelica.Thermal.HeatTransfer.Components.ThermalConductor` and
  `HeatCapacitor` model this directly; there is no reason to build a
  fluid-based model or introduce a working fluid anywhere in this case --
  it is pure solid-to-solid conduction, no flow of any kind.
- Equal heat capacities were chosen deliberately so the equilibrium
  temperature (50 degC) and the conservation identity
  (`T_A + T_B = 100`) are both exact, closed-form numbers to check
  against, the same reasoning `simple_two_tank_equilibrium` uses for equal
  tank areas.
