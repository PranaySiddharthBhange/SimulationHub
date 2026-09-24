# Held Mass Released Onto A Spring-Damper — Underdamped Oscillation To Rest

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 150.0 s |
| output samples | 1500 |
| solver tolerance | 1e-06 |

**Domains:** `mechanical_dynamics`

## Engineering brief

Canonical entities and aliases: Mass (the moving mass), Spring, Damper, Clamp, and fixed wall. The Spring connects the Mass to the fixed wall. The Damper also connects the Mass to the fixed wall, and the Damper is in parallel with the Spring. The Clamp holds the Mass fixed at position x = 0.10 m while engaged. Reported variables for the model output are: position_m [m], the Mass position relative to the spring natural-length position; velocity_m_s [m/s], the Mass velocity; clamp_engaged [1], clamp state with 1 for engaged and 0 for released.

Resolved parameter values from the requirement specification: Mass mass = 1 kg [current]; Spring stiffness = 1 N/m [current]; Damper damping coefficient = 0.2 N*s/m [current]; Spring natural length position = 0 m [current]; Clamp held position = 0.10 m [current]; Clamp start time = 0 s [current]; Clamp release time = 5 s [current]. The entity list gives Mass position = 0.10 m [current] and velocity = 0 m/s [current], and also position = 0 m [current], velocity = 0 m/s [current], and position = -0.0729 m [current]. These additional position entries are not identified as initial conditions or final/current state times. The explicit behavioral requirements resolve the executable initial behavior instead: while the Clamp is engaged from t = 0 s to t = 5 s, position stays at 0.10 m and velocity stays at 0 m/s; therefore the model uses position_m = 0.10 m and velocity_m_s = 0 m/s throughout that interval. The 0 m and -0.0729 m position entries are preserved as unresolved note content with no stated timing or role.

Behavior and sequence: the system is a command-driven mechanical dynamics case with one discrete event. From t = 0 s until t = 5 s, the Clamp is engaged and holds the Mass fixed at x = 0.10 m, with velocity 0 m/s. At t = 5 s, the Clamp releases once. After release, the Mass moves back toward the Spring natural length, so position decreases from 0.10 m and velocity becomes negative. The requirements state the motion is underdamped, overshoots past the natural length so that position becomes negative before settling, and eventually comes to rest at the natural length rather than approaching 0 m monotonically.

Physical relationships explicitly stated: m*x'' + c*x' + k*x = 0. With the stated current parameters, zeta = c / (2*sqrt(k*m)) = 0.2 / (2*sqrt(1*1)) = 0.1, omega_n = sqrt(k/m) = 1 rad/s, and omega_d = omega_n*sqrt(1-zeta^2) ~= 0.995 rad/s. Units are consistent for the governing equation: m [kg] times x'' [m/s^2] gives N, c [N*s/m] times x' [m/s] gives N, and k [N/m] times x [m] gives N, so all terms balance as force. The stated closed-form expression x(t) = x0 * exp(-zeta*omega_n*dt) * (cos(omega_d*dt) + (zeta*omega_n/omega_d)*sin(omega_d*dt)) is included as explicit evidence for post-release displacement relative to the release instant dt, but the note does not explicitly define dt beyond the time after release, nor does it explicitly define whether this expression applies only for t >= 5 s. That applicability is a necessary executable interpretation recorded as an assumption.

Simulation requirements: simulate for 150 s and report the Mass position, Mass velocity, and Clamp engaged/released state for the whole run. Acceptance behavior explicitly recorded in the requirement specification: at t = 4 s, position_m == 0.10 and velocity_m_s == 0.0 with absolute tolerance 0.001; at t = 6 s, velocity_m_s <= -0.04; position_m <= -0.05 must become true at some point during the run; abs(velocity_m_s) <= 0.01 at t = 8.16 s; position_m <= 0.0 must become true at some point before t = 8 s, checked over 5 s to 8 s; at t = 150 s, position_m == 0.0 and velocity_m_s == 0.0 with absolute tolerance 0.005; abs(position_m) <= 0.003 must hold for the entire interval t = 50 s to t = 150 s.

Derived interpretation from explicit requirements: because the Clamp holds the Mass fixed through t = 5 s and then releases once, clamp_engaged should be 1 from t = 0 s through the pre-release interval and 0 after release. Because REQ-FUN-003 requires overshoot rather than monotonic approach, at least one negative position must occur after release. Because REQ-FUN-004 requires settling well before the end of the run and AC-09 requires |position_m| <= 0.003 from 50 s onward, the later portion of the run must remain near equilibrium. No external force, actuator other than the Clamp, nonlinear spring law, travel limit, gravity term, or additional state is stated in the notes, so none is included.

## Acceptance checks (11)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | at 4 s | `position_m == 0.10` | 1 | 0 | 01_spring_mass_release.txt <AC-02> |
| 2 | at 4 s | `velocity_m_s == 0.0` | 1 | 0 | 01_spring_mass_release.txt <AC-02> |
| 3 | at 4 s | `clamp_engaged == 1` | 1 | 0 | 01_spring_mass_release.txt <REQ-FUN-001> |
| 4 | at 6 s | `clamp_engaged == 0` | 1 | 0 | 01_spring_mass_release.txt <REQ-FUN-002> |
| 5 | at 6 s | `velocity_m_s <= -0.04` | 1 | 0 | 01_spring_mass_release.txt <AC-04> |
| 6 | ever | `position_m <= -0.05` | 1 | 0 | 01_spring_mass_release.txt <AC-05> |
| 7 | at 8.16 s | `abs(velocity_m_s) <= 0.01` | 1 | 0 | 01_spring_mass_release.txt <AC-06> |
| 8 | ever | `position_m <= 0.0` | 1 | 0 | 01_spring_mass_release.txt <AC-07> |
| 9 | at 150 s | `abs(position_m - 0.0) <= 0.005` | 1 | 0 | 01_spring_mass_release.txt <AC-08> |
| 10 | at 150 s | `abs(velocity_m_s - 0.0) <= 0.005` | 1 | 0 | 01_spring_mass_release.txt <AC-08> |
| 11 | always | `abs(position_m) <= 0.003` | 1 | 0 | 01_spring_mass_release.txt <AC-09> |

## Conflicts resolved (1)

### Mass state before clamp release

**Adopted:** position = 0.10 m and velocity = 0 m/s from t = 0 s to t = 5 s

**Not adopted:**

- Mass position = 0 m [current] as an initial/current state, rejected because REQ-FUN-001 explicitly requires position to stay at 0.10 m while the clamp is engaged.
- Mass position = -0.0729 m [current] as an initial/current state, rejected because REQ-FUN-001 explicitly requires position to stay at 0.10 m while the clamp is engaged.

**Evidence:** The requirement specification explicitly states Clamp held position = 0.10 m [current], release time = 5 s [current], and REQ-FUN-001 requires position = 0.10 m and velocity = 0 m/s while the clamp is engaged from t = 0 s to t = 5 s. That explicit behavior governs the executable initial/held state despite additional unlabeled position entries in the entity list.

## Open questions (1)

1. What role and timing should be assigned to the extra Mass position entries 0 m [current] and -0.0729 m [current] listed under Entities, since the note does not state whether they are milestone values, observed extrema, or erroneous duplicates?

## Assumptions (4)

- For execution, the clamp state is represented by clamp_engaged with value 1 while engaged and 0 after release; the note requests reporting engaged/released state but does not prescribe a numeric encoding.
- For execution, the post-release governing equation m*x'' + c*x' + k*x = 0 applies only after the clamp release event at t = 5 s; before release, clamp holding overrides free motion.
- For execution of the stated closed-form displacement expression, dt is interpreted as time elapsed since clamp release, dt = t - 5 s, for t >= 5 s.
- The acceptance criterion AC-07 is implemented as an ever-condition over the run because the schema does not represent a restricted search window; its narrative source states this should occur before t = 8 s and be checked over 5 s to 8 s.
