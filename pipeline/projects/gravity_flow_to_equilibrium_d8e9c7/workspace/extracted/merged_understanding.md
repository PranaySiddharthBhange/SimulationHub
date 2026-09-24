# Two Tanks, One Above The Other — Gravity Flow To Equilibrium

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 150.0 s |
| output samples | 1000 |
| solver tolerance | 0.001 |

**Domains:** `fluid_level_and_flow`

## Engineering brief

Canonical entities and reported variables:
- Tank A (upper tank; alias: Tank A (upper)). Report variable `level_A_m` in m: liquid level in Tank A.
- Tank B (lower tank; alias: Tank B (lower)). Report variable `level_B_m` in m: liquid level in Tank B.
- Connecting valve. Report variable `valve_open_cmd` as 0 or 1: commanded closed/open state of the on/off valve.
- Connecting flow. Report variable `q_m3s` in m^3/s: volumetric flow through the single connecting pipe and valve, defined by the stated physical relationship when the valve is open.

System topology and parameters from 01_two_tank_equilibrium.txt:
- Tank A is physically above Tank B.
- Two open tanks are joined by a single pipe with the Connecting valve.
- Tank A cross-sectional area is 0.5 m^2 [current]. Tank B cross-sectional area is 0.5 m^2 [current].
- Tank A height is 1.0 m [current]. Tank B height is 1.0 m [current].
- Tank A starting level is 0.80 m at starting time 0 s [current]. Tank B starting level is 0.00 m at starting time 0 s [current].
- Connecting flow conductance `k` is 0.025 m^2/s [current].
- The system total level sum is 0.80 m [current]. The requirement also states the shared equilibrium level is 0.40 m in each tank because the starting 0.80 m of liquid is split evenly across two equal-area tanks.
- The stated time constant is `tau = area / (2*k) = 10 s` [current]. Derived check: with area = 0.5 m^2 and k = 0.025 m^2/s, `tau = 0.5 / (2*0.025) = 10 s`, units `(m^2)/(m^2/s) = s`, so the stated relationship is numerically and dimensionally consistent.

Command behavior and sequence:
- The Connecting valve closed interval starts at 0 s and ends at 5 s [current]. The valve open time is 5 s [current].
- Requirement REQ-FUN-001 states the valve shall stay closed and both levels shall stay exactly at their starting values for the entire closed interval, t = 0 to t = 5 s.
- Requirement REQ-FUN-002 states that at t = 5 s the valve shall open and flow shall begin from Tank A into Tank B, so Tank A's level falls and Tank B's level rises from that point on.
- Explicit commanded samples are given as `valve_open_cmd == 0` at t = 4 s and `valve_open_cmd == 1` at t = 6 s.

Physical relationships and model meaning:
- Explicit physical relationship: `q = k * (level_A - level_B)` [current]. This note does not explicitly state a separate equation for the valve-closed case; however REQ-FUN-001 requires both levels to stay exactly at their starting values for t = 0 to 5 s while the valve is closed, and REQ-FUN-002 requires flow to begin once the valve opens at 5 s. Therefore the executable interpretation is that the connecting flow is inhibited while `valve_open_cmd = 0` and follows the stated relation after opening.
- Explicit behavior: if `level_A > level_B`, flow runs from A to B and relaxes toward zero as the difference closes.
- Explicit conserved quantity: `level_A + level_B` is constant at 0.80 m from t = 0 onward, before and after the valve opens. Requirement AC-07 makes this an acceptance condition over the full run. Because the tank areas are equal and constant, this is consistent with conservation of total liquid volume up to the common area factor.
- Requirement REQ-FUN-003 states the system shall relax toward a shared equilibrium level of 0.40 m in each tank and shall stay there for the remainder of the run once reached.
- Tank level constraints AC-08 require `level_A_m` and `level_B_m` each to remain within [0, 1.0] m throughout the run.

Simulation and reporting:
- REQ-SIM-001 requires simulation for 150 seconds and reporting of both tank levels and the connecting valve open/closed command for the whole run.
- The requirement note also names acceptance/check times: pre-open at 4 s, post-open at 6 s, flow-visible at 15 s, equilibrium-approach at 45 s, and acceptance at 150 s.

No additional entities, documents, aliases, modes, interlocks, pause/resume behavior, abort/reset behavior, tables, or datasets are present in the provided notes.

## Acceptance checks (9)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | at 4 s | `valve_open_cmd == 0` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-01> |
| 2 | at 4 s | `(abs(level_A_m - 0.80) <= 0.001) and (abs(level_B_m - 0.00) <= 0.001)` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-02> |
| 3 | at 6 s | `valve_open_cmd == 1` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-03> |
| 4 | at 15 s | `(level_A_m <= 0.75) and (level_B_m >= 0.05)` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-04> |
| 5 | at 45 s | `(abs(level_A_m - 0.40) <= 0.02) and (abs(level_B_m - 0.40) <= 0.02)` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-05> |
| 6 | final | `(abs(level_A_m - 0.40) <= 0.005) and (abs(level_B_m - 0.40) <= 0.005)` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-06> |
| 7 | always | `abs((level_A_m + level_B_m) - 0.80) <= 0.001` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-07> |
| 8 | always | `(level_A_m >= 0) and (level_A_m <= 1.0) and (level_B_m >= 0) and (level_B_m <= 1.0)` | 1 | 0 | 01_two_tank_equilibrium.txt <AC-08> |
| 9 | ever | `q_m3s > 0` | 1 | 0 | 01_two_tank_equilibrium.txt <REQ-FUN-002> |

## Conflicts resolved (1)

### How the stated flow law applies during the valve-closed interval

**Adopted:** During 0 to 5 s with `valve_open_cmd = 0`, connecting flow is zero; after opening, `q_m3s = k * (level_A_m - level_B_m)` with k = 0.025 m^2/s.

**Not adopted:**

- Applying `q = k * (level_A - level_B)` regardless of valve state loses because it contradicts REQ-FUN-001, which requires both levels to remain exactly at starting values for the entire closed interval.

**Evidence:** Within 01_two_tank_equilibrium.txt, the requirement specification is self-consistent only if the valve blocks flow while closed. REQ-FUN-001 and REQ-FUN-002 govern behavior, and the separate physical relationship is therefore interpreted as the open-valve relation.

## Assumptions (3)

- The reported variable `q_m3s` is included so that the requirement 'flow shall begin' can be checked mechanically; the note requires reporting both tank levels and valve command, but does not explicitly require reporting flow.
- For executable modeling, the connecting-flow relation `q = k * (level_A - level_B)` is applied only when the valve is open; while the valve is closed from 0 to 5 s, flow is taken as zero so that REQ-FUN-001 is satisfied. The note states the relation and the required closed-interval behavior separately but does not write one combined equation.
- A simulation tolerance of 0.001 is chosen because the note states level acceptance tolerances at the millimeter scale (0.001 m and 0.005 m) but does not state a solver tolerance.
