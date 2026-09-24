# Resolved understanding - Quasi-Static Magnetic Circuit benchmark

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 1.0 s |
| output samples | 1001 |
| solver tolerance | 1e-06 |

**Domains:** `magnetic_circuit`

## Engineering brief

Canonical entities and aliases. The system is the benchmark magnetic circuit / quasi-static magnetic circuit / magnetic circuit. It consists of a rectangular iron core / iron core / IronCore, one discrete air gap / air gap / AirGap / GAP-1 useful branch element, one leakage flux path / leakage branch / LEAK-1 in parallel with the useful air-gap path, one exciting coil / ExcitingCoil wound on the left leg, one measuring coil / MeasuringCoil located at the air-gap region, one useful-flux sensor / flux sensor / FluxSensor sensing useful air-gap flux, one electric ground / ElectricGround / electrical ground defining zero electric potential, and one magnetic ground / MagneticGround / magnetic ground defining zero magnetic scalar potential. The reference drawing note shows the coil wound on the leg, the mmf source N.I associated with that coil, and the useful flux arrow crossing the right-side air-gap opening. Reported model variables shall be: time_s [s] = simulation time; I_rms_A [A RMS] = exciting-current phasor magnitude; mmf_At [A-turn] = exciting-coil magnetomotive force magnitude N_exc*I_rms_A; Phi_core_Wb [Wb] = total core flux magnitude before the branch split; Phi_gap_Wb [Wb] = useful air-gap flux magnitude through GAP-1; Phi_leak_Wb [Wb] = leakage-branch flux magnitude through LEAK-1; Phi_gap_over_Phi_core [1] = useful/core flux ratio; B_core_T [T] = flux density magnitude in the constant-area core elements based on Phi_core_Wb; B_gap_T [T] = flux density magnitude in the air gap based on Phi_gap_Wb; H_core_A_m [A/m] = magnetic field strength magnitude in iron; H_gap_A_m [A/m] = magnetic field strength magnitude in air gap; Vm_core_At [A-turn] = total magnetic potential drop magnitude across the series iron path; Vm_gap_At [A-turn] = magnetic potential drop magnitude across the air-gap branch, equal also to the leakage-branch magnetic potential difference because GAP-1 and LEAK-1 are parallel; U_exc_induced_V_rms [V RMS] = exciting-coil induced-voltage magnitude; U_meas_induced_signed_V_rms [V RMS] = measuring-coil induced voltage with sign convention negative relative to the positive air-gap flux arrow.

Resolved topology. The magnetic path is left leg / CORE-L in series with upper yoke / CORE-U, then in series with right leg iron / CORE-R. After CORE-R the flux splits into two parallel branches: useful air gap / GAP-1 and leakage branch / LEAK-1. Both branches rejoin before the lower yoke / CORE-D, which then returns to magnetic ground. The exciting coil couples electrically to the current source CurrentRamp and magnetically to the left-leg/core magnetic path, providing positive magnetic mmf for positive exciting-coil current. The exciting coil electrical circuit references electric ground. GAP-1 provides useful flux to the flux sensor and magnetically couples to the measuring coil, whose induced-voltage orientation is opposite to the exciting coil orientation in the benchmark and specifically negative relative to the positive useful air-gap flux arrow. The topology is explicitly a magnetic circuit with a series iron path and a parallel useful-gap/leakage split; it is not a nonlinear or force-producing actuator model.

Resolved geometry and parameters for the released nominal benchmark configuration. The square core cross-section side is a = 25 mm = 0.025 m. The constant cross-sectional area is A = a*a = 0.0006250000000000001 m^2; one dataset note writes the area unit as m, but this is inconsistent with the requirement and element listings, so the intended area unit is m^2 as used in the register element areas. The mean outside magnetic-circuit reference dimension is l = 150 mm = 0.15 m. The nominal benchmark air-gap length is delta = 1.50 mm = 0.00150 m. The separate as-built prototype gap is 1.58 mm = 0.00158 m, measured by shim stack + feeler gauge cross-check with stated uncertainty 2e-05 m, but that as-built value is retained as a distinct prototype configuration and is not to silently replace the nominal AV-11 benchmark geometry. Mean flux-line lengths for the released nominal geometry are left leg = l-a = 0.125 m, upper yoke = l-a = 0.125 m, right leg iron = l-a-delta = 0.1235 m, and lower yoke = l-a = 0.125 m. Exciting coil turns are N_exc = 600 turns. Measuring coil turns are N_meas = 50 turns for the released benchmark; 40 turns is archived/superseded legacy content. Quasi-static excitation frequency is f = 50 Hz. Effective relative permeability for the linear iron benchmark is mu_r = 1200; mu_r = 1000 is superseded/archived legacy or catalog content. Leakage coefficient is sigma = 0.08 for the released nominal benchmark; sigma = 0.05 is superseded/archived legacy content. The useful/core flux ratio is therefore Phi_gap/Phi_core = 1-sigma = 0.92, and Phi_leak/Phi_core = sigma = 0.08.

Excitation schedule and simulation scenario. The current input is a quasi-static RMS current phasor magnitude, not an instantaneous sinusoidal waveform and not a peak phasor magnitude unless an explicit representation conversion is added, which these notes do not include. The required schedule is: 0 A RMS until 0.10 s, then a linear ramp from 0 A to 2.0 A RMS between 0.10 s and 0.50 s, then hold 2.0 A RMS through 1.0 s. Positive current produces positive mmf. The recorded dataset is evidence that one run followed a 0..1 s interval and reached 2 A, 1200 A-turn, and the expected flux and voltage magnitudes; it is reference evidence about the released nominal configuration, not an input table that drives the model.

Physical relationships explicitly established. Flux, flux density, field strength, magnetic potential difference, and electric quantities are represented as complex phasors under quasi-static assumptions. For linear reluctance elements in the released baseline, reluctance is real-valued, so flux and magnetic potential difference share phasor angle. Magnetic reluctance for a constant-area linear flux-tube element is Rm = length/(mu0*mu_r*A). Derived from the notes: this has units A/Wb because mu0*mu_r*A/length has permeability-times-area-over-length dimensions corresponding to Wb/A. Flux density is B = Phi/A for constant cross-section elements. Iron field strength is H_core = B_core/(mu0*mu_r). Air-gap field strength is H_gap = B_gap/mu0. Magnetic potential difference of an element is Vm = H*length. The branch equality condition is Vm across GAP-1 equals Vm across LEAK-1 because those elements are in parallel. Flux continuity at the split is Phi_core = Phi_gap + Phi_leak. Useful air-gap flux is modeled as Phi_gap = (1-sigma)*Phi_core, and leakage flux as Phi_leak = sigma*Phi_core. The leakage reluctance relationship is R_leak = R_gap*(1-sigma)/sigma, and the equivalent parallel branch reluctance is R_parallel = 1/(1/R_gap + 1/R_leak). The exciting coil mmf is F = N_exc*I_rms_A, reported as mmf_At. The total-flux relationship in the analytic note is Phi_core = F/R_total with R_total = R_core + R_parallel, where R_core is the series sum of the four iron-element reluctances. The series magnetic potential drops across the iron path plus the air-gap branch drop balance the exciting-coil mmf: Vm_core_At + Vm_gap_At = mmf_At, equivalently mmf_At - Vm_core_At - Vm_gap_At = 0. Induced-voltage phasor magnitudes satisfy |U| = 2*pi*f*N*|Phi| for sinusoidal flux. For the exciting coil the physical relationships list 2*pi*f*N_exc*Phi_core; for the measuring coil they list 2*pi*f*N_meas*Phi_gap. The engineering register requirement states the exciting-coil induced voltage is oriented positive with respect to the defined positive electric direction, while the measuring-coil induced voltage is oriented negative with respect to the air-gap flux direction shown in the reference configuration; therefore U_meas_induced_signed_V_rms should be negative when Phi_gap_Wb is positive.

Analytic benchmark values stated for AV-11 at the final 2.0 A RMS point, using the released nominal configuration. Total core reluctance = 5.289249e+05 A/Wb. Air-gap reluctance = 1.909859e+06 A/Wb. Equivalent gap/leak reluctance = 1.757071e+06 A/Wb. Total core flux Phi_core_Wb = 5.249354e-04 Wb. Useful air-gap flux Phi_gap_Wb = 4.829406e-04 Wb. Leakage flux Phi_leak_Wb = 4.199483e-05 Wb. Core flux density B_core_T = 0.839897 T. Gap flux density B_gap_T = 0.772705 T. Core magnetic drop Vm_core_At = 277.651 A-turn. Gap magnetic drop Vm_gap_At = 922.349 A-turn. Exciting induced-voltage magnitude U_exc_induced_V_rms = 98.948 V RMS. Measuring induced-voltage magnitude is 7.586 V RMS in magnitude, with the signed reported variable negative by orientation, i.e. U_meas_induced_signed_V_rms = -7.586 V RMS at the final point under the stated sign convention. Derived numerical consistency check from the evidence: at 2 A RMS and 600 turns, mmf = 1200 A-turn. The stated drops 277.651 + 922.349 = 1200.000 A-turn, exactly matching the stated mmf balance. Also 0.92 * 5.249354e-04 = 4.82940568e-04 Wb, consistent with the stated useful flux to within the printed precision, and 0.08 * 5.249354e-04 = 4.1994832e-05 Wb, consistent with the stated leakage flux.

Baseline exclusions and modeling boundaries. Force interaction shall not be modeled. Saturation, nonlinear B-H behavior, hysteresis, eddy-current loss, and frequency-dependent permeability are excluded from the baseline linear benchmark. A nonlinear inductor example may exist elsewhere but is explicitly not authority for this case. The model shall preserve the distinction between model parameter values, as-built measurements, and verification configuration. AV-11 and the released nominal benchmark use the nominal 1.50 mm gap, while the 1.58 mm measured gap belongs to a distinct prototype/as-built configuration retained for traceability or separate validation context.

Evidence handling for tables and datasets. The quasistatic_ramp_results dataset is a reference table because it records one observed run from 0 to 1 s, including observed ranges for current, mmf, fluxes, B, H, magnetic drops, induced voltages, and Phi_gap/Phi_core, and it confirms the 0.92 useful/core ratio at observed times 0.105 s and 1.0 s. The geometry_metrology_export dataset is supporting because it records nominal and as-built geometry values, the AV-11 nominal configuration usage, and metrology provenance; it does not itself prescribe the simulation input schedule. No note provides a tabulated commanded input file; the commanded schedule is textual and captured in the narrative and checks instead.

Acceptance behavior to be checked against the reported variables. The model must demonstrate the staged excitation actually occurs: current is zero before ramp, reaches the final 2.0 A RMS value during the run, and holds that value at the end. The flux split must actually occur with Phi_gap_over_Phi_core reaching 0.92, not merely remaining bounded. The final 2.0 A RMS nominal benchmark point must reproduce the released analytic values within the stated tolerances: mmf balance residual within 0.5% of N*I, useful/core ratio 0.92 within 0.002 absolute, and flux, B, H, and induced-voltage magnitudes within 1% of the released analytic result. Because the measuring-coil sign convention is explicit, its signed final voltage should be negative and its magnitude should match 7.586 V RMS within 1%.

## Acceptance checks (14)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | at 0 s | `I_rms_A <= 1e-06` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-ELC-003 |
| 2 | ever | `I_rms_A >= 1.999` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-ELC-003 |
| 3 | final | `I_rms_A` | 2 | 0.001 | 02_02_magnetic_engineering_register.txt REQ-ELC-003 |
| 4 | final | `abs((mmf_At - Vm_core_At - Vm_gap_At)/mmf_At) <= 0.005` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-VV-001 |
| 5 | final | `Phi_gap_over_Phi_core` | 0.92 | 0.002 | 02_02_magnetic_engineering_register.txt REQ-VV-002 |
| 6 | ever | `Phi_gap_over_Phi_core >= 0.918` | 1 | 0 | 12_09_analytic_verification_procedure.txt |
| 7 | final | `Phi_core_Wb` | 0.000524935 | 5.24935e-06 | 12_09_analytic_verification_procedure.txt |
| 8 | final | `Phi_gap_Wb` | 0.000482941 | 4.82941e-06 | 12_09_analytic_verification_procedure.txt |
| 9 | final | `Phi_leak_Wb` | 4.19948e-05 | 4.19948e-07 | 12_09_analytic_verification_procedure.txt |
| 10 | final | `B_core_T` | 0.839897 | 0.00839897 | 12_09_analytic_verification_procedure.txt |
| 11 | final | `B_gap_T` | 0.772705 | 0.00772705 | 12_09_analytic_verification_procedure.txt |
| 12 | final | `U_exc_induced_V_rms` | 98.948 | 0.98948 | 12_09_analytic_verification_procedure.txt |
| 13 | final | `U_meas_induced_signed_V_rms` | -7.586 | 0.07586 | 12_09_analytic_verification_procedure.txt |
| 14 | final | `U_meas_induced_signed_V_rms < 0` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-IND-002 |

## Conflicts resolved (5)

### Released leakage coefficient sigma

**Adopted:** sigma = 0.08 for the released nominal benchmark

**Not adopted:**

- sigma = 0.05 rejected because it is archived/superseded legacy content in CR-MAG-006-related notes, the legacy model, and scratch notes

**Evidence:** Requirement specification in 02_02_magnetic_engineering_register.txt <REQ-PER-001> sets sigma to 0.08 [current/effective]; 05_04_model_definition_notes.txt and 09_05_magnetics_email_thread.txt record 0.08 as approved/released and 0.05 as archived/superseded; dataset run reaches Phi_gap/Phi_core = 0.92, consistent with sigma = 0.08.

### Effective relative permeability for linear benchmark

**Adopted:** mu_r = 1200

**Not adopted:**

- mu_r = 1000 rejected because it is superseded/archived legacy or catalog content replaced by approved CR-MAG-004 and released benchmark records

**Evidence:** 02_02_magnetic_engineering_register.txt <REQ-PER-002> sets effective relative permeability to 1200 [current/effective]; 05_04_model_definition_notes.txt, 06_06_design_review_minutes.txt, 09_05_magnetics_email_thread.txt, 11_08_core_coil_datasheet.txt, and 12_09_analytic_verification_procedure.txt all support 1200 as approved/current for the released linear benchmark.

### Measuring-coil turn count

**Adopted:** N_meas = 50 turns

**Not adopted:**

- 40 turns rejected because it is archived/superseded legacy or old prototype content

**Evidence:** 02_02_magnetic_engineering_register.txt <REQ-ELC-002> sets 50 turns [current/effective]; 05_04_model_definition_notes.txt, 06_06_design_review_minutes.txt, 09_05_magnetics_email_thread.txt, 11_08_core_coil_datasheet.txt, and 12_09_analytic_verification_procedure.txt all identify 50 as approved/released and 40 as archived/superseded.

### Gap length for released nominal benchmark versus as-built prototype

**Adopted:** Use nominal delta = 1.50 mm for the released nominal benchmark and AV-11; retain measured/as-built delta = 1.58 mm as a separate prototype configuration

**Not adopted:**

- delta = 1.58 mm as the benchmark gap rejected because multiple notes explicitly require preserving nominal and as-built configurations separately and AV-11 uses nominal geometry

**Evidence:** 02_02_magnetic_engineering_register.txt <REQ-GEO-003> sets nominal delta to 1.50 mm; 09_05_magnetics_email_thread.txt explicitly says not to silently replace the 1.50 mm nominal gap in the analytic benchmark; 12_09_analytic_verification_procedure.txt uses delta = 0.00150 m [current/nominal benchmark]; 13_14_lab_validation_runbook.txt says use nominal 1.50 mm gap for AV-11; 15_12_geometry_metrology_export.txt states AV-11 uses nominal geometry and retains the as-built prototype distinctly.

### Meaning of the commanded current values

**Adopted:** Current schedule values are RMS current phasor magnitudes, not peak values and not an instantaneous waveform

**Not adopted:**

- 2.828 A peak rejected as the commanded benchmark input because scratch notes list it only as a converted peak value for 2 Arms and multiple authoritative notes prohibit silent conversion

**Evidence:** 02_02_magnetic_engineering_register.txt <REQ-ELC-003> specifies RMS current magnitude; 05_04_model_definition_notes.txt and 06_06_design_review_minutes.txt explicitly state EP-03/current input is RMS phasor magnitude and not to be converted to peak without explicit representation conversion.

## Assumptions (4)

- Reported variable names were chosen to match the recorded dataset where available and to make the checks mechanically evaluable; the notes do not provide one single mandated report-variable list.
- The final checks are evaluated at simulation end time 1.0 s because the commanded hold extends through 1.0 s and AV-11 gives final expected values at the 2.0 A RMS point.
- Although one dataset note writes cross-section area unit as m, the resolved model uses m^2 because the requirement and engineering register define area and list A = 0.0006250000000000001 m^2 for the magnetic elements.
- H_core_A_m and H_gap_A_m are declared reported variables because AV-11 requires H magnitudes to agree within 1%, but the procedure note does not state final expected H values explicitly; therefore no numeric H check is written.

## Source tables

| document | role | why |
| --- | --- | --- |
| 14_10_quasistatic_ramp_results.txt | `reference` | Document kind is dataset and all values are marked [observed], recording one run from 0 to 1 s; instructions state recorded runs are evidence about the past, not model input. |
| 15_12_geometry_metrology_export.txt | `supporting` | Dataset supplies nominal and as-built geometry values and states AV-11 uses nominal geometry while prototype geometry is distinct; it supports parameter provenance rather than driving the run. |
