# Resolved engineering brief - Two-Tank Sequence Controller

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 900.0 s |
| output samples | 9000 |
| solver tolerance | 1e-06 |

**Domains:** `fluid_level_and_flow`, `batch_sequential_process`

## Engineering brief

Canonical entities and aliases: Tank 1 is TK-101, also called tank1 and T1. Tank 2 is TK-102, also called tank2 and T2. Inlet valve V1 is XV-101, also called valve1. Transfer valve V2 is XV-102, also called valve2. Drain valve V3 is XV-103, also called valve3. The controller is PLC-101, also called tankController, Controller, PLC, and in one diagram tankController1. Level transmitter LT-101 is also level1 and AI-101; LT-102 is also level2 and AI-102. START, STOP, and SHUT are momentary operator commands, implemented as PB-START/DI-101, PB-STOP/DI-102, and PB-SHUT/DI-103 in the engineering register. Boundary source SRC-101 supplies V1; boundary sink DRN-101 receives V3 discharge.

Topology from the notes: SRC-101 supplies liquid to V1; V1 feeds Tank 1; Tank 1 discharges through V2; V2 feeds Tank 2; Tank 2 discharges through V3; V3 drains to DRN-101. LT-101 sends Tank 1 level measurement to PLC-101, and LT-102 sends Tank 2 level measurement to PLC-101. START, STOP, and SHUT commands are digital inputs to PLC-101. PLC-101 provides Boolean valve-open commands to V1, V2, and V3. The datasheet states that for the hackathon simulation dynamic valve stroke is neglected and each valve is treated as an ideal Boolean flow switch, even though the valves have 0.8 s full-open and 0.6 s full-close stroke times on the datasheet.

Resolved parameter set and statuses: Tank 1 cross-section area is 1.2 m^2 from the engineering register; Tank 2 cross-section area is 1.4 m^2. Tank heights are 1 m each, with max working level 0.9 m for each tank. Initial levels are 0.05 m for both tanks. Valve nominal flows are V1 0.006 m^3/s, V2 0.0045 m^3/s, and V3 0.0050 m^3/s from the engineering register, corroborated by the datasheet. LT-101 and LT-102 engineering range is 0.0..1.0 m; the requirements register also states level values shall be represented internally in metres with nominal valid range 0.0 to 1.0 m. PLC scan time is 0.1 s. All three valves fail closed / de-energize-to-close on loss of power.

Resolved thresholds and delays: Tank 1 high-level threshold T1_High is resolved to 0.80 m, not 0.78 m. Evidence: CR-004 is approved in the email thread, the engineering register marks 0.80 m current/active and 0.78 m superseded, and the test procedure uses effective high-level setpoint 0.80 m. Tank 1 low threshold T1_Low is 0.05 m current/active. Tank 2 low threshold T2_Low is 0.05 m current/active. Level comparisons include equality: transitions use LT-101 >= T1_High and LT-101 <= T1_Low, LT-102 <= T2_Low. WAIT_AFTER_FILL delay is 10 s from the requirement specification and current requirements register requirement URS-FUN-004. The post-transfer delay between Tank 1 reaching low and opening V3 is resolved to 12 s from URS-PER-005 [current], design review approved delay, and observed dataset wait_remaining_s range up to 12 s with WAIT_AFTER_TRANSFER starting at 440 s and DRAIN_T2 at 452 s. The inter-cycle delay after Tank 2 reaches low before next fill is resolved to 8 s from URS-PER-006 [current], design review approved delay, approved email note, and observed dataset WAIT_AFTER_DRAIN at 632 s followed by FILL_T1 at 640 s.

Controller states established by the design note and observed in the dataset: IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, and SHUTDOWN. Legacy names map as follows: FILL->FILL_T1, HOLD1->WAIT_AFTER_FILL, TRANSFER->TRANSFER_T1_T2, HOLD2->WAIT_AFTER_TRANSFER, DRAIN->DRAIN_T2, HOLD3->WAIT_AFTER_DRAIN.

Normal sequence behavior: From IDLE, a START edge begins FILL_T1. In FILL_T1, V1=1, V2=0, V3=0 and Tank 1 fills. FILL_T1 transitions to WAIT_AFTER_FILL when LT-101 >= T1_High; on that transition V1 is set to 0 and the wait timer starts. In WAIT_AFTER_FILL all valves are 0; when the 10 s timer expires, the controller enters TRANSFER_T1_T2 and sets V2=1. In TRANSFER_T1_T2, V1=0, V2=1, V3=0 and liquid transfers from Tank 1 to Tank 2 until LT-101 <= T1_Low. Then the controller enters WAIT_AFTER_TRANSFER, sets V2=0, and starts the post-transfer timer. In WAIT_AFTER_TRANSFER all valves are 0; when the 12 s timer expires, the controller enters DRAIN_T2 and sets V3=1. In DRAIN_T2, V1=0, V2=0, V3=1 and Tank 2 drains until LT-102 <= T2_Low. Then the controller enters WAIT_AFTER_DRAIN, sets V3=0, and starts the inter-cycle timer. In WAIT_AFTER_DRAIN all valves are 0; when the 8 s timer expires, the controller returns automatically to FILL_T1 and sets V1=1. The automatic process continues cyclically unless interrupted by STOP or SHUT.

Pause and resume behavior: STOP is accepted from any normal running or wait state and places the controller in PAUSED with all valve outputs false. PAUSED preserves the interrupted sequence state and, if STOP occurred during WAIT_AFTER_FILL, WAIT_AFTER_TRANSFER, or WAIT_AFTER_DRAIN, it also preserves the remaining timer value; START resumes the stored state and restores that state's outputs. A START after STOP continues the process from the point at which STOP was accepted rather than forcing a new initialization. START while already running is ignored. Derived consequence: because PAUSED stores the interrupted state and restores state outputs on START, STOP during a running state such as TRANSFER_T1_T2 resumes that same running state, not a wait or fill state; this is also directly corroborated by AC-03 and the observed run at 280 s.

Shutdown behavior and priorities: Command precedence is SHUT > STOP > START. Any valid SHUT edge from any non-SHUTDOWN state immediately abandons any stored resume context and enters SHUTDOWN with V1=0, V2=1, V3=1. SHUT is a controlled process shutdown/drain, not an emergency-stop or power-loss event. During SHUTDOWN, START and STOP are ignored until shutdown is complete. Shutdown completion requires both LT-101 <= T1_Low and LT-102 <= T2_Low. While SHUTDOWN is active, V2 and V3 stay commanded open until both low-level conditions are satisfied; then the controller closes V2 and V3 and goes to IDLE. After shutdown completion the controller is in the initial idle configuration with all valves closed, and a later START begins a new fill cycle. V1 remains inhibited during SHUTDOWN.

Valve-command prohibitions and allowed concurrency: V1 shall never be commanded open while V2 is open. During normal automatic operation, V2 and V3 shall not be open simultaneously. The simultaneous-open restriction for V2 and V3 is explicitly waived in SHUTDOWN, and the test procedure requires V2 and V3 to be open together at 700 s during SHUT. On loss of controller power, all process valves move to or remain closed; in the simulation this is represented by false output commands, but no power-loss command schedule is provided for the demonstration run.

Physical relationships grounded in the notes: The archived legacy model provides the only explicit dynamic equations, and they are unit-consistent with the current geometry and flow values when valves are ideal Boolean switches. Using reported variables tank1_level_m [m], tank2_level_m [m], valve1_cmd [-], valve2_cmd [-], valve3_cmd [-], the continuous balances are: d(tank1_level_m)/dt = (valve1_cmd*qFill - valve2_cmd*qTransfer)/A1 and d(tank2_level_m)/dt = (valve2_cmd*qTransfer - valve3_cmd*qDrain)/A2, where qFill=0.006 m^3/s, qTransfer=0.0045 m^3/s, qDrain=0.0050 m^3/s, A1=1.2 m^2, A2=1.4 m^2. Derived from those balances and the stated areas/flows, normal-state level rates are: Tank 1 fill rate 0.005 m/s, Tank 1 transfer depletion rate 0.00375 m/s, Tank 2 transfer rise rate approximately 0.0032142857 m/s, and Tank 2 drain depletion rate approximately 0.0035714286 m/s. These equations are adopted as a modeling basis because they are explicit note evidence from a legacy model and match the current register's geometry and flow parameters, except for later-resolved thresholds and delays.

Demonstration scenario and timing: The current requirements register and approved test procedure define a 900 s demonstration run from 0 s through 900 s. The scheduled commands are START at 20 s, STOP at 220 s, START at 280 s, STOP at 650 s, and SHUT at 700 s. The operator log and the recorded dataset corroborate the same schedule as observations. The dataset is evidence about one past run, not an input schedule; it is classified as reference. The design and test notes establish that sequence operation, stop/resume behavior, and controlled shutdown are to be demonstrated in simulation.

Reported variables contract for later stages: time_s [s] is simulation time. tank1_level_m [m] is Tank 1 liquid level corresponding to LT-101. tank2_level_m [m] is Tank 2 liquid level corresponding to LT-102. valve1_cmd [-] is Boolean command to XV-101/V1, with 1=open and 0=closed. valve2_cmd [-] is Boolean command to XV-102/V2, with 1=open and 0=closed. valve3_cmd [-] is Boolean command to XV-103/V3, with 1=open and 0=closed. controller_state_id [-] is integer-coded controller state with the following declared mapping for evaluable checks: IDLE=0, FILL_T1=1, WAIT_AFTER_FILL=2, TRANSFER_T1_T2=3, WAIT_AFTER_TRANSFER=4, DRAIN_T2=5, WAIT_AFTER_DRAIN=6, PAUSED=7, SHUTDOWN=8. wait_remaining_s [s] is the remaining active wait timer value, zero when no wait timer is active or when the implementation does not expose a stored remaining time outside a wait context.

Checks are written against those reported variables and the approved schedule. State-boundary timing checks use the test procedure's acceptable +/-2 s tolerance where timing is the subject. Because checks compare variable values rather than event times, event occurrence is represented by 'ever' attainment of the required state or level condition, and interval conditions are checked at instants well inside stated intervals or with always checks over valve combinations. The run is expected to show at least one complete fill, one resumed transfer after STOP, one drain, one inter-cycle restart after 8 s, a second pause, SHUTDOWN with V2 and V3 open together, and return to IDLE before 900 s.

Evidence distinctions preserved: the control diagram contains a conflicting relation 'ambient1 connects to valve3' and 'valve3 feeds tank2'; higher-authority engineering register and legacy architecture both show Tank 2 discharging to V3 and V3 draining to ambient/DRN-101, so the diagram relation is treated as non-governing inconsistency. The operator log mentions an observed 12 s 'dead time' and Jin's old model high target 0.78 as archived prior art; those do not override current approved values. The dataset shows one observed maximum tank2_level_m of 0.69286 m and observed state entry times such as 170 s, 180 s, 440 s, 452 s, 632 s, 640 s, 700 s, and 714 s; these are used only as reference evidence consistent with the resolved parameters, not as requirements or direct forcing inputs.

## Acceptance checks (14)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | ever | `tank1_level_m >= 0.80` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-01 |
| 2 | at 250 s | `(valve1_cmd == 0) and (valve2_cmd == 0) and (valve3_cmd == 0)` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-02 |
| 3 | at 280 s | `controller_state_id == 3 and valve2_cmd == 1 and valve1_cmd == 0 and valve3_cmd == 0` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-03 |
| 4 | ever | `controller_state_id == 1 and valve1_cmd == 1` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-04 |
| 5 | at 675 s | `(valve1_cmd == 0) and (valve2_cmd == 0) and (valve3_cmd == 0)` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-05 |
| 6 | at 700 s | `valve1_cmd == 0 and valve2_cmd == 1 and valve3_cmd == 1` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-06 |
| 7 | final | `controller_state_id == 0 and valve1_cmd == 0 and valve2_cmd == 0 and valve3_cmd == 0` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-07 |
| 8 | always | `not (valve1_cmd > 0.5 and valve2_cmd > 0.5)` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-08 |
| 9 | always | `not (valve2_cmd > 0.5 and valve3_cmd > 0.5 and controller_state_id != 8)` | 1 | 0 | 11_09_test_procedure_TP17.txt AC-08 |
| 10 | ever | `controller_state_id == 3 and valve2_cmd == 1` | 1 | 0 | 02_02_engineering_data_register.txt URS-FUN-004 |
| 11 | ever | `controller_state_id == 4` | 1 | 0 | 02_02_engineering_data_register.txt URS-PER-005 |
| 12 | ever | `controller_state_id == 5 and valve3_cmd == 1` | 1 | 0 | 02_02_engineering_data_register.txt URS-FUN-007 |
| 13 | ever | `controller_state_id == 8` | 1 | 0 | 02_02_engineering_data_register.txt URS-MOD-003 |
| 14 | ever | `tank1_level_m <= 0.05 and tank2_level_m <= 0.05` | 1 | 1e-06 | 02_02_engineering_data_register.txt URS-CTL-005 |

## Conflicts resolved (7)

### Tank 1 high-level setpoint

**Adopted:** 0.80 m effective/current high-level limit

**Not adopted:**

- 0.78 m from 01_01_customer_URS.txt is an older released baseline but is superseded by later approved/current records.
- 0.78 m archived/current inconsistency in 08_05_controls_email_thread.txt loses because the same note explicitly says CR-004 approved and 'Treat 0.80 m as the effective T1 high limit'.
- 0.78 m in legacy model and operator note is archived prior art.

**Evidence:** 02_02_engineering_data_register.txt marks 0.80 m current/active and 0.78 m superseded; 08_05_controls_email_thread.txt gives approved CR-004 requiring 0.80 m effective high limit; 11_09_test_procedure_TP17.txt uses 0.80 m as the effective acceptance value.

### Delay after Tank 1 reaches low before opening V3

**Adopted:** 12 s

**Not adopted:**

- 10 s in 01_01_customer_URS.txt is an earlier released baseline.
- 10 s in archived legacy model is prior art.
- URS-FUN-006 in 02_02_engineering_data_register.txt says after Tank 1 low wait before V3, but the timing content there is superseded by URS-PER-005 current parameter value.

**Evidence:** 02_02_engineering_data_register.txt gives post-transfer waiting time 12 s as current in URS-PER-005; 06_06_design_review_minutes.txt records 12 s approved; 08_05_controls_email_thread.txt records approved behavior 'After T1 reaches low level, wait 12 s before opening the drain valve'; observed dataset shows WAIT_AFTER_TRANSFER for 12 s.

### Delay after Tank 2 reaches low before next fill

**Adopted:** 8 s

**Not adopted:**

- 10 s in 01_01_customer_URS.txt is an earlier released baseline.
- 10 s in archived legacy model is prior art.
- URS-FUN-008 in 02_02_engineering_data_register.txt giving 10 s return-to-fill behavior is marked superseded.

**Evidence:** 02_02_engineering_data_register.txt gives inter-cycle waiting time 8 s as current in URS-PER-006; 06_06_design_review_minutes.txt records 8 s approved; 08_05_controls_email_thread.txt records approved 8 s and says it supersedes 10 s; observed dataset shows WAIT_AFTER_DRAIN from 632 s to 640 s.

### Whether V2 and V3 may be open simultaneously

**Adopted:** V2 and V3 are not simultaneous in normal automatic operation but are commanded open together in SHUTDOWN

**Not adopted:**

- Any interpretation that V2 and V3 may never be simultaneous loses because multiple higher-authority and later notes explicitly waive the restriction in SHUTDOWN.
- The ambiguous control diagram relation around valve3 topology is rejected for concurrency semantics because the diagram is lower authority and inconsistent with the register/test procedure.

**Evidence:** 02_02_engineering_data_register.txt URS-SAF-004 and URS-SAF-005 distinguish normal operation from SHUT; 05_04_control_logic_design_notes.txt and 06_06_design_review_minutes.txt explicitly waive the restriction in SHUTDOWN; 11_09_test_procedure_TP17.txt AC-06 requires V2/V3 open together at 700 s.

### Behavior of START after STOP

**Adopted:** START after STOP resumes the interrupted state and any remaining wait time, rather than restarting from IDLE/FILL

**Not adopted:**

- Any restart-from-beginning interpretation loses because the URS, requirements register, design note, design review, test procedure, operator log, and observed dataset all support resume behavior.

**Evidence:** 01_01_customer_URS.txt URS-M-002 requires continuation rather than new initialization; 02_02_engineering_data_register.txt URS-MOD-002 and URS-CTL-001 require resume with frozen wait timer; 05_04_control_logic_design_notes.txt defines PAUSED restore behavior; 11_09_test_procedure_TP17.txt AC-03 requires the 280 s START to resume interrupted transfer; 12_10_demo_run_900s.txt observed run resumes TRANSFER_T1_T2 at 280 s.

### Tank areas and nominal valve flows for simulation

**Adopted:** A1=1.2 m^2, A2=1.4 m^2, qFill=0.006 m^3/s, qTransfer=0.0045 m^3/s, qDrain=0.0050 m^3/s

**Not adopted:**

- Archived legacy values are not rejected numerically because they match, but their status is archived rather than current.
- Any use of valve stroke times as dynamic flow modulation is rejected for this hackathon simulation because the datasheet explicitly says to neglect dynamic valve stroke and use ideal Boolean flow switching.

**Evidence:** 02_02_engineering_data_register.txt gives current equipment values; 10_08_valve_datasheet.txt corroborates the same nominal demo flow equivalents and explicitly directs ideal Boolean flow-switch treatment for the hackathon simulation.

### Direction of valve3 connection

**Adopted:** Tank 2 discharges to V3 and V3 drains to DRN-101/ambient1

**Not adopted:**

- 03_03_reference_control_diagram.txt relation 'ambient1 connects to valve3' and 'valve3 feeds tank2' is inconsistent with higher-authority topology notes and is not adopted.

**Evidence:** 02_02_engineering_data_register.txt interface matrix explicitly states Tank 2 discharges to V3 and V3 drains to DRN-101; 04_11_partial_legacy_architecture.txt states tank2 flows_to valve3 and valve3 flows_to ambient1; 01_01_customer_URS.txt describes XV-103 as the drain valve for TK-102.

## Assumptions (4)

- For mechanically evaluable checks, controller_state_id is reported as an integer-coded state variable with mapping IDLE=0, FILL_T1=1, WAIT_AFTER_FILL=2, TRANSFER_T1_T2=3, WAIT_AFTER_TRANSFER=4, DRAIN_T2=5, WAIT_AFTER_DRAIN=6, PAUSED=7, SHUTDOWN=8; the notes establish the state names but not a numeric encoding.
- The model uses ideal Boolean valve commands directly as flow switches and neglects valve stroke dynamics, following 10_08_valve_datasheet.txt [page 1] for the hackathon simulation.
- Checks at exact command times 280 s and 700 s assume the reported outputs reflect the commanded controller response at those sample times; the notes provide a PLC scan time of 0.1 s but do not prescribe a separate command-processing latency model.
- No explicit requirement states whether tank levels are clipped at 0 and tank height; later stages should preserve physical plausibility, but no additional saturation law beyond the stated valid measurement range 0.0..1.0 m is introduced here.

## Source tables

| document | role | why |
| --- | --- | --- |
| 12_10_demo_run_900s.txt | `reference` | Document kind is dataset and the notes state it records one run over time_s from 0 to 900 s with observed values; per notes, observed runs are evidence about the past and must not drive the model. |
