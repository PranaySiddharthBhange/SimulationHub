# Fan spin-up with viscous and quadratic aerodynamic losses

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 60.0 s |
| output samples | 1000 |
| solver tolerance | 1e-06 |

**Domains:** `mechanical_dynamics`

## Engineering brief

Canonical entities and topology: The system contains a fan wheel mounted on a shaft, driven by a motor and opposed by two loss mechanisms: bearing friction and aerodynamic load. The fan wheel and shaft rotate together as the fan's single rotational degree of freedom. Reported variables for the model output are: fan_speed_rad_s [rad/s], the fan angular speed; motor_on_cmd [1], the motor on/off command where 0 means off and 1 means on; motor_torque_Nm [N*m], the applied motor torque delivered to the shaft. Parameters from 01_fan_nonideal_spinup.txt are: shaft rotational inertia J = 0.02 kg*m^2 [current]; motor torque magnitude = 0.5 N*m [current]; motor start time = 5 s [current]; bearing friction coefficient b = 0.01 N*m*s/rad [current]; aerodynamic load coefficient k_fan = 0.0004 N*m*s^2/rad^2 [current]; fan initial speed = 0 rad/s [current]; fan rated/nameplate speed = 30 rad/s [nominal]; fan steady-state speed = 25 rad/s [required]; simulation duration = 60 s [required]. Continuous physical relationships explicitly stated are T_friction = b * omega, T_aero = k_fan * omega^2, and J * domega/dt = T_motor - b*omega - k_fan*omega^2. Unit check: b*omega gives (N*m*s/rad)*(rad/s) = N*m; k_fan*omega^2 gives (N*m*s^2/rad^2)*(rad^2/s^2) = N*m, so the torque balance is dimensionally consistent. Derived consequence: at steady state domega/dt = 0, so T_motor = b*omega + k_fan*omega^2. Substituting the stated current values gives 0.5 = 0.01*omega + 0.0004*omega^2, whose exact positive solution is omega = 25 rad/s; this matches the required steady-state speed and supports REQ-FUN-004 and AC-08. Command behavior: motor_on_cmd is 0 before t = 5 s and 1 from t = 5 s onward, because the note states the motor turns on at t = 5 s and gives a fixed, constant driving torque. Therefore motor_torque_Nm is 0 N*m while motor_on_cmd = 0 and 0.5 N*m while motor_on_cmd = 1. Required behavior: from t = 0 s to t = 5 s, while the motor is off, the fan speed remains exactly 0 rad/s. At t = 5 s the motor turns on and the fan spins up from 0 rad/s under the stated torque balance. The speed rises smoothly toward a real steady-state equilibrium, stays strictly below the 30 rad/s rated/nameplate speed for the entire run, and settles to 25 rad/s for the remainder of the run. Acceptance behavior stated by the note includes: fan_speed_rad_s == 0 at t = 4 s; motor_on_cmd == 0 at t = 4 s and motor_on_cmd == 1 at t = 6 s; fan_speed_rad_s >= 15 rad/s at t = 6 s; abs(fan_speed_rad_s - 25) <= 0.5 rad/s at t = 10 s; fan_speed_rad_s == 25 rad/s at t = 60 s with absolute tolerance 0.05 rad/s; fan_speed_rad_s <= 29.9 from t = 5 s to t = 60 s; fan_speed_rad_s <= 25.05 for the entire run; and at t = 60 s the steady-state torque balance residual motor_torque_Nm - (0.01*fan_speed_rad_s + 0.0004*fan_speed_rad_s*fan_speed_rad_s) equals 0 within 0.01 N*m absolute tolerance. The note contains no additional states, modes, pause/resume behavior, abort/reset logic, or scheduled commands beyond the single motor turn-on at t = 5 s.

## Acceptance checks (10)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | at 4 s | `fan_speed_rad_s == 0` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-01> |
| 2 | at 4 s | `motor_on_cmd == 0` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-02> |
| 3 | at 6 s | `motor_on_cmd == 1` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-02> |
| 4 | ever | `fan_speed_rad_s > 0` | 1 | 0 | 01_fan_nonideal_spinup.txt <REQ-FUN-002> |
| 5 | at 6 s | `fan_speed_rad_s >= 15.0` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-03> |
| 6 | at 10 s | `abs(fan_speed_rad_s - 25.0) <= 0.5` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-04> |
| 7 | final | `fan_speed_rad_s` | 25 | 0.05 | 01_fan_nonideal_spinup.txt <AC-05> |
| 8 | always | `fan_speed_rad_s <= 29.9` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-06> |
| 9 | always | `fan_speed_rad_s <= 25.05` | 1 | 0 | 01_fan_nonideal_spinup.txt <AC-07> |
| 10 | final | `motor_torque_Nm - (0.01*fan_speed_rad_s + 0.0004*fan_speed_rad_s*fan_speed_rad_s)` | 0 | 0.01 | 01_fan_nonideal_spinup.txt <AC-08> |

## Assumptions (1)

- Because the note states the motor applies a fixed, constant driving torque and turns on at t = 5 s, motor_torque_Nm is modeled as 0 N*m for t < 5 s and 0.5 N*m for t >= 5 s. This is a modeling choice needed to make the explicit reported variable motor_torque_Nm executable; the note does not separately state an off-state torque value in the equations.
