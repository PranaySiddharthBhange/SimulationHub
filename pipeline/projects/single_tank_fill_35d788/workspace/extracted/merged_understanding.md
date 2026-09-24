# Single Tank Fill — One Valve, One Threshold

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 100.0 s |
| output samples | 1000 |
| solver tolerance | 1e-06 |

**Domains:** `fluid_level_and_flow`

## Engineering brief

Canonical entities and aliases:
- Tank: a tank with cross-sectional area 0.5 m^2 [current], height 1.0 m [current], and initial level 0 m [current], from 01_single_tank_fill.txt.
- Inlet valve: the single inlet valve feeding the tank. Its nominal inflow is stated as 0.01 m^3/s [nominal], also given equivalently as 10 L/s [nominal].
- Single supply: upstream supply feeding the tank via the inlet valve.
- Fill target: a level setpoint of 0.80 m [current]. The note also states an expected time of 40 s for reaching this target.
- Reported variables contract for later stages:
  - tank_level_m [m]: tank liquid level over the run.
  - valve_open_cmd [1]: inlet valve open/closed command, with 1 meaning open and 0 meaning closed.

Topology and relationships:
- The single supply fills through the Inlet valve.
- The Inlet valve feeds the Tank.
- The Inlet valve closes at the Fill target: it closes as soon as tank level reaches the 0.80 m target and stays closed.

Behavior and control:
- Starting from empty, the tank fills until its level reaches the 0.80 m fill target, at which point the inlet valve closes and the level stops rising. This is explicitly required in <REQ-FUN-001>.
- The valve is open whenever tank level is below the fill target, and closed once the target is reached.
- Once closed, the valve never reopens during this run.
- The command schedule implied by the requirements and acceptance criteria is not an externally forced input schedule. Instead, acceptance criteria state that valve_open_cmd must be 1 at t = 5 s and 0 at t = 100 s, consistent with level-triggered closure.

Physical relationship:
- The note explicitly gives 0.80 m * 0.5 m^2 / 0.01 m^3/s = 40 s <AC-01>. Units are consistent: m * m^2 / (m^3/s) = s. Derived meaning: with constant inflow at the nominal value and constant cross-sectional area, filling from 0 m to 0.80 m requires 0.40 m^3, so the expected fill time is 40 s.

Requirements and acceptance:
- Simulate for 100 s and report tank_level_m and valve_open_cmd for the whole run <REQ-SIM-001>.
- Acceptance criteria recorded in the note:
  - tank_level_m >= 0.80 must become true at some point during the run <AC-01>.
  - tank_level_m <= 0.85 must hold for the entire run <AC-02>.
  - valve_open_cmd == 1 at t = 5 s <AC-03>.
  - valve_open_cmd == 0 at t = 100 s <AC-04>.
  - tank_level_m == 0.80 at t = 100 s with absolute tolerance 0.01 m <AC-05>.

Model content supported by the note:
- This is a fluid level and flow system with one tank and one inlet valve.
- The behavior is event-driven by the level threshold at 0.80 m; no outlet, leakage, or other flow path is stated.
- No additional dynamics for valve motion, supply pressure variation, or level-dependent area are stated in the note, so they are not included as facts.
- The note states the tank height is 1.0 m; acceptance also limits the level to 0.85 m through the run. The target 0.80 m is therefore below the stated height.

## Acceptance checks (5)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | ever | `tank_level_m >= 0.80` | 1 | 0 | 01_single_tank_fill.txt <AC-01> |
| 2 | always | `tank_level_m <= 0.85` | 1 | 0 | 01_single_tank_fill.txt <AC-02> |
| 3 | at 5 s | `valve_open_cmd == 1` | 1 | 0 | 01_single_tank_fill.txt <AC-03> |
| 4 | at 100 s | `valve_open_cmd == 0` | 1 | 0 | 01_single_tank_fill.txt <AC-04> |
| 5 | at 100 s | `tank_level_m` | 0.8 | 0.01 | 01_single_tank_fill.txt <AC-05> |

## Assumptions (4)

- No outlet, leak, evaporation, or other mass loss path is stated in the note; the model omits such paths.
- The stated nominal inflow 0.01 m^3/s is treated as constant while the inlet valve is commanded open, because no other inflow dependence or valve characteristic is stated.
- The tank cross-sectional area is treated as constant at 0.5 m^2, consistent with the explicit fill-time relationship given in the note.
- The initial condition is tank_level_m = 0 m at t = 0 s, based on the Tank entity and the phrase 'Starting from empty.'
