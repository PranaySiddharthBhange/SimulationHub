# Resolved understanding - Two-Tank Sequence Controller

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 900.0 s |
| output samples | 1000 |
| solver tolerance | 1e-06 |

**Domains:** `fluid_level_and_flow`, `batch_sequential_process`

## Engineering brief

Canonical entities and aliases: PLC-101 is the controller, also called tankController, controller, PLC, and tankController (PLC-101). TK-101 is Tank 1, also called T1 and tank1. TK-102 is Tank 2, also called T2 and tank2. XV-101 is valve V1/valve1, XV-102 is valve V2/valve2, and XV-103 is valve V3/valve3. LT-101 is the Tank 1 level measurement input to PLC-101, also called level1/AI-101. LT-102 is the Tank 2 level measurement input to PLC-101, also called level2/AI-102. PB-START/START, PB-STOP/STOP, and PB-SHUT/SHUT are the operator digital commands to PLC-101 via DI-101, DI-102, and DI-103 respectively. PLC-101 commands XV-101, XV-102, and XV-103 via DO-101, DO-102, and DO-103. SRC-101 is the upstream liquid source feeding XV-101. DRN-101 is the downstream drain/sink receiving flow from XV-103.

Physical topology established by the notes: SRC-101 fluidOut connects to XV-101 inlet; XV-101 outlet connects to TK-101 inlet; TK-101 outlet connects to XV-102 inlet; XV-102 outlet connects to TK-102 inlet; TK-102 outlet connects to XV-103 inlet; XV-103 outlet connects to DRN-101 fluidIn. This topology is stated in the engineering register interface matrix and is consistent with the requirement specification, control diagram, and legacy architecture draft. The control diagram note has one conflicting-looking connection text, ambient1 connected_to valve3 and valve3 connected_to tank2, but it is lower-authority than the engineering register and inconsistent with all other notes, so the resolved fluid direction is tank2 -> valve3 -> DRN-101.

Resolved parameter set and statuses: Tank 1 initial level is 0.05 m. Tank 2 initial level is 0.05 m. Tank 1 low-level setpoint is 0.05 m. Tank 2 low-level setpoint is 0.05 m. Tank 1 high-level setpoint is resolved to 0.80 m current/active/effective, superseding 0.78 m. Tank 1 cross-section area is 1.2 m^2. Tank 2 cross-section area is 1.4 m^2. Tank heights are 1 m each, with max working level 0.9 m each. LT-101 and LT-102 nominal ranges are 0.0 to 1.0 m, matching the controller internal level representation range. PLC-101 scan time is 0.1 s current. Valve commands are Boolean open/closed commands. XV-101 nominal demo flow coefficient equivalent is 0.0060 m^3/s, XV-102 is 0.0045 m^3/s, and XV-103 is 0.0050 m^3/s. Datasheet full stroke times are 0.8 s open and 0.6 s close for the VXS-24 family used by all three project valves, but the same datasheet explicitly states that for the hackathon simulation dynamic valve stroke is neglected and each valve is treated as an ideal Boolean flow switch. Valves are energized open at 24 VDC and fail closed on loss of electrical power.

Resolved timing set: WAIT_AFTER_FILL after Tank 1 reaches the high-level limit is 10 s approved/current. WAIT_AFTER_TRANSFER after Tank 1 reaches the low-level limit is resolved to 12 s current/approved, superseding 10 s. WAIT_AFTER_DRAIN after Tank 2 reaches the low-level limit is resolved to 8 s current/approved, superseding 10 s. A 900 s demonstration/simulation run is current and approved. Scheduled demonstration commands are START at 20 s, STOP at 220 s, START at 280 s, STOP at 650 s, and SHUT at 700 s.

Controller state model grounded by the design notes and corroborated by the recorded dataset: IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, and SHUTDOWN. Legacy names map as follows: FILL -> FILL_T1, HOLD1 -> WAIT_AFTER_FILL, TRANSFER -> TRANSFER_T1_T2, HOLD2 -> WAIT_AFTER_TRANSFER, DRAIN -> DRAIN_T2, HOLD3 -> WAIT_AFTER_DRAIN.

Normal automatic sequence behavior: From IDLE, a valid START edge begins FILL_T1. In FILL_T1, PLC-101 commands XV-101 open and XV-102/XV-103 closed to fill Tank 1. When LT-101 >= Tank 1 high-level setpoint, XV-101 closes and the controller transitions to WAIT_AFTER_FILL. In WAIT_AFTER_FILL, all three valve commands are false while a 10 s delay counts down. When the wait timer expires, the controller transitions to TRANSFER_T1_T2. In TRANSFER_T1_T2, PLC-101 commands XV-102 open and XV-101/XV-103 closed, transferring liquid from Tank 1 to Tank 2. When LT-101 <= Tank 1 low-level setpoint, XV-102 closes and the controller transitions to WAIT_AFTER_TRANSFER. In WAIT_AFTER_TRANSFER, all three valve commands are false while a 12 s delay counts down. When that timer expires, the controller transitions to DRAIN_T2. In DRAIN_T2, PLC-101 commands XV-103 open and XV-101/XV-102 closed, draining Tank 2. When LT-102 <= Tank 2 low-level setpoint, XV-103 closes and the controller transitions to WAIT_AFTER_DRAIN. In WAIT_AFTER_DRAIN, all three valve commands are false while an 8 s delay counts down. When that timer expires, the controller transitions back to FILL_T1 and the cycle continues unless interrupted by STOP or SHUT.

Threshold comparisons use equality as established in the design note: LT-101 >= high threshold causes fill completion; LT-101 <= low threshold causes transfer completion; LT-102 <= low threshold causes drain completion; shutdown completion requires LT-101 <= T1 low and LT-102 <= T2 low.

STOP/PAUSE behavior: STOP has higher priority than START and lower priority than SHUT. STOP is accepted from any normal running or wait state and places the controller in PAUSED with all three valve outputs false. START from PAUSED restores the interrupted stored state rather than forcing a new initialization. START while already running is ignored. If STOP occurs in a wait state, the remaining delay is retained/frozen and START resumes with that remaining delay; the timer is not restarted. This pause/resume retention is explicitly grounded in the design note, engineering register, and design review minutes. STOP commands received during SHUTDOWN are ignored until shutdown is complete.

SHUTDOWN behavior: A valid SHUT edge from any non-shutdown state immediately abandons any stored resume context and enters SHUTDOWN. In SHUTDOWN, PLC-101 inhibits XV-101 and commands XV-102 and XV-103 open together to empty both tanks. START and STOP commands received during SHUTDOWN are ignored and do not interrupt the shutdown sequence. The simultaneous-open restriction for XV-102 and XV-103 is explicitly waived only in SHUTDOWN. SHUTDOWN completion requires both LT-101 and LT-102 to be at or below their low-level setpoints. When shutdown emptying is achieved, XV-102 and XV-103 close, XV-101 remains closed, the controller returns to IDLE, and a new START is required to begin another fill cycle.

Interlocks and prohibitions: XV-101 shall never be commanded open while XV-102 is open. During normal automatic operation, XV-102 and XV-103 shall not be open simultaneously. During SHUTDOWN, XV-102 and XV-103 may be open simultaneously. On loss of controller power, all process valves shall move to or remain in the closed position; equivalently, output commands shall be false and the actuators fail closed.

Continuous physical relationships supported by the notes: The legacy model provides archived tank level balance equations using fixed nominal flow rates and tank cross-sectional areas. These equations are dimensionally consistent because volumetric flow rate [m^3/s] divided by area [m^2] gives level rate [m/s]. Derived for the resolved model, under the explicit assumption that the nominal demo flow coefficients are used as constant flow rates when a valve is commanded open and zero when commanded closed, the level states are h1 and h2 with units of m and obey dh1/dt = (u1*qFill - u2*qTransfer)/A1 and dh2/dt = (u2*qTransfer - u3*qDrain)/A2, where A1 = 1.2 m^2, A2 = 1.4 m^2, qFill = 0.0060 m^3/s, qTransfer = 0.0045 m^3/s, qDrain = 0.0050 m^3/s, and u1/u2/u3 are Boolean valve-open commands represented numerically as 1 for open and 0 for closed. Initial conditions are h1(0)=0.05 m and h2(0)=0.05 m. The notes do not state any overflow, saturation, leakage, compressibility, or pressure-dependent flow relationship, so none is added beyond the stated levels, areas, and nominal constant flows. The notes also do not establish whether controller scan discretization must be represented explicitly in the plant/control simulation; scan time is recorded as component data.

Reported variables contract for later stages: time_s [s] is simulation time. tank1_level_m [m] is Tank 1 liquid level corresponding to LT-101. tank2_level_m [m] is Tank 2 liquid level corresponding to LT-102. valve1_open_cmd [-] is PLC-101 Boolean command to XV-101, 1=open and 0=closed. valve2_open_cmd [-] is PLC-101 Boolean command to XV-102, 1=open and 0=closed. valve3_open_cmd [-] is PLC-101 Boolean command to XV-103, 1=open and 0=closed. controller_state_id [-] is a numeric encoding of controller state with the declared mapping: IDLE=0, FILL_T1=1, WAIT_AFTER_FILL=2, TRANSFER_T1_T2=3, WAIT_AFTER_TRANSFER=4, DRAIN_T2=5, WAIT_AFTER_DRAIN=6, PAUSED=7, SHUTDOWN=8. wait_remaining_s [s] is the active remaining wait timer value, zero when no wait state is active.

Acceptance behavior grounded in the approved test procedure and requirement notes: the 900 s demonstration applies the stated command schedule. Tank 1 must reach 0.80 m before first transfer begins. All valve commands must be 0 throughout the paused intervals 220-280 s and 650-700 s. The START at 280 s must resume transfer rather than restart filling, so transfer must occur after that START. After completion of the first Tank 2 drain, another fill cycle must begin after the effective 8 s inter-cycle delay. At 700 s SHUTDOWN must have XV-101 closed and XV-102/XV-103 open together. After shutdown draining completes, the controller must return to IDLE with all valves closed and remain there through 900 s because no further START is scheduled. Normal automatic operation must never command XV-101 and XV-102 simultaneously, nor XV-102 and XV-103 simultaneously. The SHUTDOWN simultaneous-opening exception for XV-102/XV-103 is preserved in the narrative rather than expressed as a mode-conditioned algebraic check because the notes do not define a separate reported normal-operation flag beyond the state variable; the checks therefore use controller_state_id to scope the prohibition.

Recorded dataset use and consistency: The 900 s observed run is reference evidence, not a required input. It starts in IDLE with both tanks at 0.05 m and all valves closed. It shows transitions at 20 s to FILL_T1, 170 s to WAIT_AFTER_FILL, 180 s to TRANSFER_T1_T2, 220 s to PAUSED, 280 s back to TRANSFER_T1_T2, 440 s to WAIT_AFTER_TRANSFER, 452 s to DRAIN_T2, 632 s to WAIT_AFTER_DRAIN, 640 s to FILL_T1, 650 s to PAUSED, 700 s to SHUTDOWN, and 714 s to IDLE, then remaining in IDLE through 900 s. Derived from those observed transition times: the observed first fill duration 20->170 s matches a 0.75 m rise at qFill/A1 = 0.0060/1.2 = 0.005 m/s, reaching 0.80 m exactly, which supports resolving the effective high-level setpoint to 0.80 m over older 0.78 m values. The observed waits 170->180 s, 440->452 s, and 632->640 s support the resolved 10 s, 12 s, and 8 s delay set respectively. These observations support but do not replace the governing current/approved requirement and test-procedure values.

Simulation setup for later stages: run from 0 s to 900 s. The notes do not state a required output interval count. The test procedure allows +/-2 s for state-boundary comparisons when the effective parameter set is used. No solver tolerance is stated in the notes; a small numerical tolerance is therefore chosen as a modeling assumption for continuous integration only, while acceptance uses explicit absolute tolerances per check.

## Acceptance checks (12)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | ever | `tank1_level_m >= 0.80 and controller_state_id == 3` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-01 |
| 2 | at 250 s | `valve1_open_cmd == 0 and valve2_open_cmd == 0 and valve3_open_cmd == 0` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-02 |
| 3 | at 282 s | `controller_state_id == 3 and valve2_open_cmd == 1 and valve1_open_cmd == 0` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-03 |
| 4 | at 640 s | `controller_state_id == 1 and valve1_open_cmd == 1` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-04 |
| 5 | at 675 s | `valve1_open_cmd == 0 and valve2_open_cmd == 0 and valve3_open_cmd == 0` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-05 |
| 6 | at 700 s | `valve1_open_cmd == 0 and valve2_open_cmd == 1 and valve3_open_cmd == 1 and controller_state_id == 8` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-06 |
| 7 | final | `controller_state_id == 0 and valve1_open_cmd == 0 and valve2_open_cmd == 0 and valve3_open_cmd == 0` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-07 |
| 8 | always | `not (valve1_open_cmd > 0.5 and valve2_open_cmd > 0.5)` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-08 |
| 9 | always | `not (valve2_open_cmd > 0.5 and valve3_open_cmd > 0.5 and controller_state_id != 8)` | 1 | 0 | 09_09_test_procedure_TP17.txt AC-08 |
| 10 | ever | `tank1_level_m >= 0.80 and valve1_open_cmd == 0` | 1 | 0 | 02_02_engineering_data_register.txt URS-FUN-003 |
| 11 | ever | `controller_state_id == 7` | 1 | 0 | 02_02_engineering_data_register.txt URS-MOD-001 |
| 12 | ever | `tank1_level_m <= 0.05 and tank2_level_m <= 0.05 and controller_state_id == 0` | 1 | 1e-06 | 02_02_engineering_data_register.txt URS-MOD-004 |

## Conflicts resolved (4)

### Tank 1 high-level setpoint

**Adopted:** 0.80 m effective/current/active high-level setpoint for Tank 1

**Not adopted:**

- 0.78 m approved in 01_01_customer_URS.txt lost because later engineering register marks 0.78 m superseded by 0.80 m current/active.
- 0.78 m archived/proposed values in 04_04_control_logic_design_notes.txt, 06_06_design_review_minutes.txt, and 07_07_legacy_tank_demo.txt lost because they are archived or proposed rather than current.
- 0.78 m current mentioned in 05_05_controls_email_thread.txt lost because the same correspondence also records 0.80 m approved/accepted under CR-004, and the test procedure uses 0.80 m as effective.

**Evidence:** 02_02_engineering_data_register.txt marks 0.80 m as current/active superseding 0.78 m; 05_05_controls_email_thread.txt records CR-004 approved 0.80 m; 09_09_test_procedure_TP17.txt uses 0.80 m as the effective high-level setpoint; 10_10_demo_run_900s.txt observed first fill reaches 0.80 m before transfer.

### Delay after Tank 1 reaches low level before opening V3

**Adopted:** 12 s post-transfer waiting time

**Not adopted:**

- 10 s approved in 01_01_customer_URS.txt lost because later current requirement URS-PER-005 sets 12 s.
- 10 s superseded text in 02_02_engineering_data_register.txt URS-FUN-006 lost because that requirement entry is explicitly superseded.
- 10 s current in 05_05_controls_email_thread.txt lost because the same note marks 12 s approved/accepted superseding 10 s.
- 10 s archived wait2 in 07_07_legacy_tank_demo.txt lost because it is archived prior art.

**Evidence:** 02_02_engineering_data_register.txt states URS-PER-005 current post-transfer waiting time 12 s; 05_05_controls_email_thread.txt records approved CR-004 change from 10 s to 12 s; 10_10_demo_run_900s.txt shows 440 s to 452 s WAIT_AFTER_TRANSFER duration, consistent with 12 s.

### Inter-cycle delay after Tank 2 reaches low level before next fill

**Adopted:** 8 s inter-cycle waiting time

**Not adopted:**

- 10 s approved in 01_01_customer_URS.txt lost because later current requirement URS-PER-006 sets 8 s.
- 10 s superseded text in 02_02_engineering_data_register.txt URS-FUN-008 lost because that requirement entry is explicitly superseded.
- 10 s current/accepted legacy wording in 05_05_controls_email_thread.txt lost because the same note marks 8 s approved/accepted superseding 10 s.
- 10 s archived wait3 in 07_07_legacy_tank_demo.txt lost because it is archived prior art.

**Evidence:** 02_02_engineering_data_register.txt states URS-PER-006 current inter-cycle waiting time 8 s; 05_05_controls_email_thread.txt records approved change from 10 s to 8 s; 09_09_test_procedure_TP17.txt acceptance AC-04 requires another fill after the effective 8 s inter-cycle delay; 10_10_demo_run_900s.txt shows 632 s to 640 s WAIT_AFTER_DRAIN duration, consistent with 8 s.

### Direction of Tank 2 drain path around V3 and DRN-101

**Adopted:** TK-102/Tank 2 flows to XV-103/V3, which flows to DRN-101/ambient1

**Not adopted:**

- 03_03_reference_control_diagram.txt connection wording ambient1 connected_to valve3 and valve3 connected_to tank2 was not adopted as directional topology because it conflicts with the engineering register interface matrix and all other notes.

**Evidence:** 02_02_engineering_data_register.txt interface matrix IF-HYD-05 and IF-HYD-06 explicitly states Tank 2 outlet to V3 inlet and V3 outlet to DRN-101 fluidIn; 01_01_customer_URS.txt says XV-103 is the drain valve for TK-102; 11_11_partial_legacy_architecture.txt matches tank2 -> valve3 -> ambient1.

## Assumptions (5)

- For the executable plant model, the nominal demo flow coefficient equivalents in 08_08_valve_datasheet.txt are used as constant volumetric flow rates when the corresponding valve command is open and zero when closed; this is supported by the archived legacy model but not stated as a current requirement.
- Valve stroke dynamics are neglected and valve commands act as ideal Boolean flow switches, because the datasheet explicitly states this simplification for the hackathon simulation.
- controller_state_id is reported as the numeric encoding IDLE=0, FILL_T1=1, WAIT_AFTER_FILL=2, TRANSFER_T1_T2=3, WAIT_AFTER_TRANSFER=4, DRAIN_T2=5, WAIT_AFTER_DRAIN=6, PAUSED=7, SHUTDOWN=8 so that state-based checks are mechanically evaluable.
- A simulation output grid of 1000 intervals is chosen because the notes state run duration but do not state required sample count or output step.
- A numerical solver tolerance of 1e-6 is chosen because the notes do not specify one; acceptance timing slack comes from the test procedure's +/-2 s state-boundary tolerance rather than from solver tolerance.

## Source tables

| document | role | why |
| --- | --- | --- |
| 10_10_demo_run_900s.txt | `reference` | Document kind is dataset and all values are marked [observed]; it records one 0-900 s run and is evidence for effective current timing/setpoint values, not a commanded input scenario. |
