# RM-201 Indoor Air Quality Control - Resolved Engineering Brief

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 86400.0 s |
| output samples | 1440 |
| solver tolerance | 1e-06 |

**Domains:** `fluid_level_and_flow`, `species_concentration_balance`, `batch_sequential_process`

## Engineering brief

System and scope: RM-201 is a single-zone room CO2 feedback-control demonstration for Seminar / Project Room 201, alias RM-201, with zone alias ZON-201. The room is represented as one well-mixed air volume of 100 m3. The topology established across the requirement specification, engineering register, diagrams, engineering notes, BIM export, and test procedure is: outdoor-air source SRC-OA-201 / freshAir supplies a supply duct DUCT-IN-201 / ductIn / supply duct; that duct connects to the room volume ZON-201 / room / volume; the room connects to exhaust duct DUCT-OUT-201 / ductOut / exhaust duct; the exhaust duct discharges to pressure boundary BND-201 / boundary4 / exhaust boundary. A people CO2 source SRC-CO2-201 / peopleSource / Occupants injects trace substance into the room. A room CO2 sensor SEN-CO2-201 / traceVolume / room CO2 measurement measures room trace-substance mass fraction and feeds a normalization gain GAIN-NORM-201 / gainSensor, which feeds controller CTL-CO2-201 / PID. Setpoint SET-CO2-201 / CO2Set also feeds the controller. Controller output passes through airflow conversion gain GAIN-AIR-201 / gain1 to the outdoor-air source mass-flow command. Outdoor-air concentration constant SET-OA-201 / CAtm feeds the outdoor-air source. Occupancy schedule SCH-OCC-201 / NumberOfPeople / OCC-SCH-04 feeds occupancy gain GAIN-PEO-201 / gain, which feeds the people source carrier mass flow.

Canonical parameters and resolved values: Room volume is 100 m3, supported by owner requirement URS-IAQ-001, engineering register IAQ-PER-001, commissioning procedure, and BIM export constraint that BIM is authoritative for room volume. Outdoor CO2 concentration for the baseline demonstration is 300 ppm absolute, represented internally as C_out = 0.3*C_nominal = 4.557E-4 kg/kg by current/approved records. The 350 ppm outdoor value appears only as archived or superseded/stale evidence and is not adopted. Nominal room concentration used for normalization is C_nominal = 1.519E-3 kg/kg, corresponding to 1000 ppm absolute under the benchmark conversion using molecular weights 44.01 kg/kmol for CO2 and 28.97 kg/kmol for dry air. Normalization is defined as normalized_CO2 = C_room / C_nominal, so a measured concentration of 1.519E-3 kg/kg produces normalized value 1.0. Controller setpoint is 1.0 normalized units. Nominal air density for ACH-to-mass-flow conversion is 1.2 kg/m3. Design occupant CO2 generation is 8.18E-6 kg/s per person. The people-source implementation uses a numerical trace concentration parameter C_source = 100 kg/kg and people-source carrier mass flow m_peopleCarrier = G_CO2 / 100, with total injected CO2 equal to m_peopleCarrier * 100 = G_CO2 = occupants * 8.18E-6 kg/s. Multiple notes explicitly prohibit interpreting C_source = 100 kg/kg as a physical room or outdoor concentration.

Controller and sign convention: The effective released reference-run tuning after CR-IAQ-007 is proportional-only control with integral action disabled. Current tuning is Kp = 6.0 ACH per normalized concentration error, output bias = 3.5 ACH, lower limit = 0.2 ACH, upper limit = 6.0 ACH. Earlier Kp = 4.0 and older archived occupancy peak 12 persons are superseded. The controller output represents ACH command. Physical supply mass flow is computed as m_supply_physical = ACH_command * V * rho / 3600, where V = 100 m3 and rho = 1.2 kg/m3, giving 0.0333333333 kg/s per ACH. Because of the Modelica source-port sign convention, the outdoor-air source command is opposite in sign to the physical supply flow: m_supply_sourceCommand = -m_supply_physical. The owner requirement explicitly requires distinguishing physical outdoor-air flow direction from implementation-specific source sign convention; correspondence also warns not to turn that into a negative physical ventilation requirement.

Control law and modes: The archived legacy model gives achCmd = min(uMax, max(uMin, uBias + Kp*(yCO2 - 1))), where yCO2 = CRoom / C_nominal. Current engineering notes describe the same proportional law as Bias + Kp*(C/Cnom - 1), with integral disabled and output limited to 0.2..6.0 ACH. Derived: using the current values, AUTO_CO2 requested command before saturation is 3.5 + 6.0*(normalized_CO2 - 1.0) ACH. Mode behavior explicitly established in engineering notes and supported by the recorded run consists of: AUTO_MIN when CO2 is sufficiently below setpoint such that the P-law requests less than or equal to the lower limit; output is 0.2 ACH. AUTO_CO2 when 0.2 < requested ACH < 6.0; output is bias + Kp*(normalized_CO2 - 1). AUTO_MAX when requested ACH >= 6.0; output is 6.0 ACH. SENSOR_FAULT when the room CO2 sensor signal is invalid continuously for more than 60 s; output is 4.0 ACH and sensor-fault indication is raised. The engineering notes state exit from SENSOR_FAULT occurs when valid signal is restored and reset logic is satisfied, but the supplied notes do not define the reset logic further. The baseline reference run did not inject the sensor-fault fallback and the recorded run observed only AUTO_MIN and AUTO_CO2, not AUTO_MAX or SENSOR_FAULT.

Occupancy schedule and simulation scenario: The approved weekday occupancy schedule is OCC-SCH-04 Rev C, to be treated as piecewise constant. The dataset note for OCC-SCH-04 is evidence of the schedule values used by the approved reference run and aligns with the scheduled command note in correspondence. The schedule is: 0 occupants from 00:00 to 07:00; 2 from 07:00 to 08:00; 8 from 08:00 to 10:00; 12 from 10:00 to 12:00; 4 from 12:00 to 13:00; 15 from 13:00 to 15:00; 10 from 15:00 to 17:00; 3 from 17:00 to 18:00; 0 from 18:00 to 24:00. Peak occupancy is therefore 15 persons in the current approved run; older 12-person references are archived. The commissioning procedure requires initializing room concentration to outdoor concentration at 00:00 with zero occupants, executing continuously through 24:00, and evaluating the controller at an internal integration step no larger than 1 s. The reference run is a 24-hour run ending at 24:00 = 86400 s. Logging interval is 60 s, yielding 1441 rows including both 00:00 and 24:00 endpoints.

Physical relationships to include in the model: (1) Well-mixed room trace-substance balance is required by CP-23, but the supplied notes do not write the full differential equation explicitly; later modeling stages should implement the well-mixed zone concentration balance consistent with the established inflow, outflow, and source terms. (2) Outdoor concentration conversion basis is set by IAQ-DAT-001: C_ppm to kg/kg uses molecular weights MW_CO2 = 44.01 kg/kmol and MW_air = 28.97 kg/kmol. Explicitly stated examples are C_nominal = 1000 ppm -> 1.519E-3 kg/kg and C_out = 300 ppm -> approximately 4.557E-4 kg/kg. (3) G_CO2 = occupants * 8.18E-6 kg/s. (4) m_peopleCarrier = G_CO2 / 100. (5) Trace injection by people source equals m_peopleCarrier * C_source = G_CO2. (6) normalized_CO2 = C_room / C_nominal. (7) m_supply_physical = ACH_command * V * rho / 3600. (8) m_supply_sourceCommand = -m_supply_physical.

Reported variables contract for later stages: report time_s [s], occupants_person [person] meaning scheduled occupant count; outdoor_co2_ppm [ppm] meaning outdoor CO2 concentration; outdoor_co2_mass_fraction_kgkg [kg/kg] meaning outdoor CO2 mass fraction used by the model; room_co2_ppm [ppm] meaning room CO2 concentration converted from model mass fraction; room_co2_mass_fraction_kgkg [kg/kg] meaning well-mixed room CO2 mass fraction; normalized_co2_feedback [1] meaning controller feedback equal to room_co2_mass_fraction_kgkg/C_nominal; ach_command_1_per_h [1/h] meaning controller ACH output after limits or fallback; source_m_flow_command_kg_s [kg/s] meaning Modelica source mass-flow command to outdoor-air source, negative for physical inflow; physical_supply_m_flow_kg_s [kg/s] meaning positive physical outdoor-air supply flow into the room; people_source_carrier_m_flow_kg_s [kg/s] meaning carrier flow sent to people source; actual_co2_generation_kg_s [kg/s] meaning actual occupant CO2 generation rate; controller_mode [state code] meaning active controller mode among AUTO_MIN, AUTO_CO2, AUTO_MAX, SENSOR_FAULT; sensor_fault_indication [Boolean] meaning whether the fault indication is raised. These names are chosen to match the commissioning procedure and recorded reference dataset where available.

Acceptance behavior and evidence: Compliance criterion is absolute room CO2 not greater than 1000 ppm during the approved occupied schedule and during the approved 24-hour reference run. The owner limit is explicitly absolute, and the 1300 ppm interpretation is rejected by decision record DR-IAQ-05 and reinforced by current requirements and test procedure. Outdoor concentration remains 300 ppm during the baseline run. ACH command must remain within 0.2..6.0 ACH during automatic operation. Source command sign and physical supply flow sign must be opposite. One-person people-source carrier flow must be 8.18E-8 kg/s with corresponding actual CO2 injection 8.18E-6 kg/s. The reference run dataset is reference evidence of one past run, not an input schedule for the model except insofar as it corroborates the separate occupancy schedule and current parameters. That recorded run shows: run length 86400 s with 1441 rows; occupants from 0 to 15; outdoor CO2 fixed at 300 ppm / 0.0004557 kg/kg; room CO2 from 300 to 996.524 ppm; normalized feedback from 0.3 to 0.996524; ach command from 0.2 to 3.47914 1/h; source command negative and physical supply positive with equal magnitude; people-source carrier flow from 0 to 1.227e-06 kg/s; actual CO2 generation from 0 to 1.227e-04 kg/s; observed controller modes AUTO_MIN and AUTO_CO2. Observed transitions in that run include AUTO_MIN at 00:00, AUTO_CO2 by 07:30, return to AUTO_MIN by 19:35, and end in AUTO_MIN at 24:00.

Evidence boundaries and omissions: The BIM export is authoritative for spatial identity and room volume only, not controls design. The CO2 transmitter datasheet describes a physical device outputting/displaying ppm and sensor characteristics such as 0-2000 ppm range, 1 ppm resolution, ±(40 ppm + 3% of reading) accuracy at 25 C, and 90 s T63, while ICD-IAQ-03 freezes the internal simulation/controller concentration signal in kg/kg followed by normalization gain. The draft architecture note that assumed sensor output in ppm is archived and superseded by the kg/kg internal interface plus normalization. The source notes do not provide the full sensor reset logic after SENSOR_FAULT, do not provide an explicit mathematical differential equation for the well-mixed zone balance beyond requiring that it be used, and do not provide a separate commanded schedule for sensor invalidity in the baseline run.

## Acceptance checks (17)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | always | `room_co2_ppm <= 1000` | 1 | 0 | 09_09_commissioning_test_procedure_CP23.txt AC-01 |
| 2 | always | `outdoor_co2_ppm == 300` | 1 | 0 | 09_09_commissioning_test_procedure_CP23.txt AC-02 |
| 3 | always | `ach_command_1_per_h >= 0.2` | 1 | 0 | 09_09_commissioning_test_procedure_CP23.txt AC-03 |
| 4 | always | `ach_command_1_per_h <= 6.0` | 1 | 0 | 09_09_commissioning_test_procedure_CP23.txt AC-03 |
| 5 | always | `physical_supply_m_flow_kg_s + source_m_flow_command_kg_s == 0` | 1 | 1e-06 | 09_09_commissioning_test_procedure_CP23.txt AC-04 |
| 6 | always | `actual_co2_generation_kg_s == occupants_person*8.18e-6` | 1 | 1e-10 | 09_09_commissioning_test_procedure_CP23.txt AC-05 |
| 7 | always | `people_source_carrier_m_flow_kg_s == actual_co2_generation_kg_s/100` | 1 | 1e-12 | 09_09_commissioning_test_procedure_CP23.txt |
| 8 | ever | `people_source_carrier_m_flow_kg_s == 8.18e-8` | 1 | 1e-12 | 09_09_commissioning_test_procedure_CP23.txt |
| 9 | ever | `actual_co2_generation_kg_s == 8.18e-6` | 1 | 1e-10 | 09_09_commissioning_test_procedure_CP23.txt |
| 10 | at 0 s | `room_co2_mass_fraction_kgkg == outdoor_co2_mass_fraction_kgkg and occupants_person == 0` | 1 | 0 | 09_09_commissioning_test_procedure_CP23.txt |
| 11 | ever | `occupants_person == 15` | 1 | 0 | 05_05_bms_controls_email_thread.txt DR-IAQ-05 |
| 12 | ever | `controller_mode == 1` | 1 | 0 | 04_04_control_sequence_and_modeling_notes.txt |
| 13 | final | `controller_mode == 0 and occupants_person == 0` | 1 | 0 | 11_11_reference_run_24h.txt |
| 14 | always | `normalized_co2_feedback == room_co2_mass_fraction_kgkg/0.001519` | 1 | 1e-06 | 02_02_iaq_engineering_register.txt IAQ-CTL-001 |
| 15 | always | `outdoor_co2_mass_fraction_kgkg == 0.0004557` | 1 | 1e-07 | 09_09_commissioning_test_procedure_CP23.txt |
| 16 | final | `time_s == 86400` | 1 | 0 | 09_09_commissioning_test_procedure_CP23.txt |
| 17 | ever | `ach_command_1_per_h > 0.2` | 1 | 0 | 11_11_reference_run_24h.txt |

## Conflicts resolved (7)

### Baseline outdoor CO2 concentration

**Adopted:** 300 ppm absolute, represented internally as 0.0004557 kg/kg (approximately 0.3*1.519E-3 kg/kg).

**Not adopted:**

- 350 ppm outdoor CO2 from 04_04_control_sequence_and_modeling_notes.txt archived value and 07_07_legacy_co2_control.txt superseded/stale value, rejected because later current requirements, review minutes, test procedure, and recorded run all use 300 ppm.

**Evidence:** Owner requirement URS-IAQ-005, engineering register IAQ-FUN-004 and IAQ-PER-006, design review minutes, commissioning procedure CP-23, correspondence, and the recorded 24 h run all support 300 ppm as the current baseline value; older 350 ppm evidence is explicitly archived or stale.

### Compliance interpretation of the 1000 ppm limit

**Adopted:** Absolute room CO2 concentration limit of 1000 ppm, not 1000 ppm above ambient.

**Not adopted:**

- 1000 ppm above ambient, around 1300 ppm total, from 05_05_bms_controls_email_thread.txt proposed constraint, rejected because DR-IAQ-05 explicitly states owner intent is 1000 ppm absolute and rejects the 1300 ppm interpretation.

**Evidence:** URS-IAQ-004, IAQ-FUN-003, IAQ-CTL-007, current engineering notes, design review minutes, and CP-23 all use absolute 1000 ppm. Correspondence DR-IAQ-05 explicitly rejects the 1300 ppm interpretation.

### Controller proportional gain Kp

**Adopted:** Kp = 6.0 ACH per normalized concentration error.

**Not adopted:**

- Kp = 4.0 ACH per normalized concentration error from superseded IAQ-CTL-008, archived legacy model, and archived old model file, rejected because CR-IAQ-007 approved 6.0 and later current records adopt it.

**Evidence:** Engineering register marks 4.0 as superseded and 6.0 as current/active; 04_04 notes cite effective reference-run tuning after CR-IAQ-007 as Kp=6.0; correspondence lists CR-IAQ-007 Kp=6.0 approved; CP-23 requires effective parameters current after CR-IAQ-007.

### Controller output bias

**Adopted:** 3.5 ACH.

**Not adopted:**

- 3.0 ACH from 07_07_legacy_co2_control.txt superseded/stale uBias, rejected because CR-IAQ-007 and current engineering records specify 3.5 ACH.

**Evidence:** Engineering register CTL-CO2-201 current/active output bias is 3.5 ACH; 04_04 note and 05_05 correspondence cite CR-IAQ-007 approved bias 3.5 ACH; CP-23 uses current parameters after CR-IAQ-007.

### Peak occupancy in approved reference run

**Adopted:** 15 persons, with 15 from 13:00 to 15:00 in OCC-SCH-04 Rev C.

**Not adopted:**

- 12 persons from owner released demonstration minimum support requirement and archived/old model references, rejected because later approved schedule revision and current records establish 15-person peak for the approved weekday reference run.

**Evidence:** Engineering register IAQ-SCH-001 requires approved weekday occupancy schedule with maximum 15 occupants; 04_04 engineering note marks 12 archived and 15 current; 05_05 correspondence states peak occupancy is now 15 from 13:00-15:00; 10_10 occupancy schedule dataset revision C and 11_11 recorded run both show 15-person peak.

### Internal controller feedback quantity units

**Adopted:** Internal simulation/controller concentration signal is kg/kg mass fraction, then normalized by gain 1/1.519E-3; physical device display may still be ppm.

**Not adopted:**

- Legacy draft assumption that sensor output is ppm, from 13_13_partial_existing_architecture.txt archived draft, rejected because later ICD-IAQ-03-referenced datasheet and engineering register freeze internal interface in kg/kg with normalization.

**Evidence:** Engineering register IAQ-INT-001 states room CO2 measurement is represented internally as Real-valued trace-substance mass fraction in kg/kg; datasheet says ICD-IAQ-03 defines internal simulation/controller concentration signal in kg/kg followed by normalization gain; archived architecture note explicitly says later ICD freezes kg/kg interface.

### Outdoor-air source command sign convention

**Adopted:** Physical supply mass flow into room is positive by physical meaning, while Modelica source command is equal magnitude and negative: source_m_flow_command = -physical_supply_m_flow.

**Not adopted:**

- Any interpretation that negative command means negative physical ventilation, rejected because owner requirement URS-IAQ-011 and correspondence explicitly distinguish physical flow direction from implementation sign convention.

**Evidence:** Engineering register IAQ-CTL-006, 04_04 engineering note, 06_06 review minutes, 09_09 CP-23 AC-04, and 14_14 field notes all state source command sign is opposite to physical inflow.

## Open questions (1)

1. What reset logic should be modeled for exiting SENSOR_FAULT after a valid sensor signal returns?

## Assumptions (4)

- For mechanically evaluable checks, controller_mode is encoded numerically by the implementation as AUTO_MIN=0, AUTO_CO2=1, AUTO_MAX=2, SENSOR_FAULT=3. The notes name the modes but do not specify a numeric encoding.
- Simulation output is sampled every 60 s to match the required 1441-row trend including both endpoints; this is implemented here as 1440 intervals over 86400 s.
- The full well-mixed zone mass-balance differential equation is not written in the notes; later stages must implement a standard well-mixed trace-substance balance consistent with the explicitly stated inflow, outflow, source, and concentration quantities.
- Boolean expressions in checks are expected to evaluate to 1 when true and 0 when false, per the required schema.

## Source tables

| document | role | why |
| --- | --- | --- |
| 10_10_occupancy_schedule.txt | `input` | CP-23 requires use of occupancy schedule OCC-SCH-04 continuously through 24:00 as piecewise constant; this dataset supplies the approved weekday occupancy profile values. |
| 11_11_reference_run_24h.txt | `reference` | The note explicitly states it is an observation of a run that already happened, not a scenario input and not a command schedule. |
