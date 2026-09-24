# Resolved understanding - Quasi-Static Magnetic Circuit benchmark

## Simulation

| setting | value |
| --- | --- |
| start time | 0.0 s |
| stop time | 1.0 s |
| output samples | 1000 |
| solver tolerance | 1e-06 |

**Domains:** `magnetic_circuit`

## Engineering brief

The system is a quasi-static magnetic-circuit benchmark comprising one rectangular linear iron core, one discrete air gap, one leakage-flux branch in parallel with the useful air-gap branch, one exciting coil, one measuring coil located in the air-gap region, one useful-flux sensor, one electric ground, and one magnetic ground. Canonical names used here are: benchmark magnetic circuit (system); exciting coil / ExcitingCoil; measuring coil / MeasuringCoil; useful-flux sensor / FluxSensor; electric ground / ElectricGround; magnetic ground / MagneticGround; left leg / CORE-L; upper yoke / CORE-U; right leg iron / CORE-R; lower yoke / CORE-D; air gap / GAP-1; leakage path / LEAK-1. The topology resolved from 01_01_system_requirement_specification.txt, 02_02_magnetic_engineering_register.txt, 05_04_model_definition_notes.txt, 10_07_legacy_magnetic_circuit.txt, and 15_12_geometry_metrology_export.txt is: the exciting coil couples magnetically to the series core path CORE-L -> CORE-U -> CORE-R; after CORE-R the magnetic circuit splits into two parallel branches, GAP-1 for useful flux and LEAK-1 for leakage flux; both branches rejoin before CORE-D; CORE-D returns to magnetic ground. GAP-1 provides useful flux to FluxSensor and is magnetically coupled to MeasuringCoil. ExcitingCoil is referenced to ElectricGround. The system includes both electric and magnetic reference potentials because multiple higher-authority notes require both grounds.

The baseline benchmark is explicitly linear and quasi-static. Flux, flux density, field strength, magnetic potential difference, and electric quantities are represented as complex phasors. For linear reluctance elements, reluctance is real-valued, so magnetic potential difference and flux share phasor angle. The benchmark excludes nonlinear B-H behavior, saturation, hysteresis, eddy-current loss, frequency-dependent permeability, and force interaction; the notes explicitly state that nonlinear behavior belongs only to a separate model variant and must not be inferred into the baseline.

Resolved released nominal geometry and parameters for the benchmark configuration are: cross-section side a = 0.025 m; reference dimension l = 0.150 m; nominal air-gap length delta = 0.00150 m; effective iron relative permeability mu_r = 1200; leakage coefficient sigma = 0.08; exciting-coil turns N_exc = 600 turn; measuring-coil turns N_meas = 50 turn; excitation frequency f = 50 Hz. The geometry-derived constant cross-sectional area is A = a*a = 0.0006250000000000001 m^2. The mean flux-line lengths for the nominal analytic benchmark are left leg = l-a = 0.125 m, upper yoke = l-a = 0.125 m, lower yoke = l-a = 0.125 m, and right leg iron = l-a-delta = 0.1235 m. The released total iron-path length is l_core = 3*(l-a) + (l-a-delta). With the nominal values above, l_core = 0.4985 m, consistent with the segment lengths listed in 02_02_magnetic_engineering_register.txt and 15_12_geometry_metrology_export.txt.

The notes also preserve a distinct as-built prototype gap for prototype comparison rather than for the released nominal benchmark: measured shim gap / prototype gap = 0.00158 m as-built, with one dataset giving uncertainty 2e-05 m. Correspondence in 09_05_magnetics_email_thread.txt and the runbook in 13_14_lab_validation_runbook.txt explicitly require keeping nominal 1.50 mm and as-built 1.58 mm distinct and using the nominal 1.50 mm gap for AV-11 and the released analytic benchmark. Therefore the executable benchmark model for the released nominal case uses delta = 0.00150 m, while retaining the 0.00158 m as-built value as separate evidence for prototype comparison only.

The excitation is a commanded RMS current-phasor magnitude ramp applied by CurrentRamp to ExcitingCoil: 0 A until t = 0.10 s, linear ramp to 2.0 A by t = 0.50 s, then hold at 2.0 A through t = 1.0 s. The requirement specification and test procedures state that these values are RMS phasor magnitudes and are not to be converted to peak values unless an explicit representation conversion is modeled. A scratch note records both 2 Arms and 2.828 A peak, but higher-authority notes define the benchmark current as RMS phasor magnitude, so the model input remains RMS magnitude 0 to 2.0 A over the stated schedule.

The magnetic and induced-voltage relationships explicitly grounded in the notes are as follows. Magnetic mmf source: F = N_exc * I_rms, where positive exciting-coil RMS current magnitude produces positive magnetomotive force. For each linear flux-tube element, reluctance is Rm = length / (mu0*mu_r*A) in iron and R_gap = delta / (mu0*A) in air, with mu_r = 1 for the air gap. Flux density is B = Phi / A for constant cross-section elements. Field strength is H_core = B_core / (mu0*mu_r) in iron and H_gap = B_gap / mu0 in the air gap. Magnetic potential difference of an element is Vm = H * length. The parallel branch conditions are Vm_gap = Vm_leak because GAP-1 and LEAK-1 are in parallel, and flux continuity at the split is Phi_core = Phi_gap + Phi_leak. The useful-flux ratio is Phi_gap / Phi_core = 1 - sigma and the leakage-flux ratio is Phi_leak / Phi_core = sigma. The leakage-path reluctance is R_leak = R_gap*(1-sigma)/sigma. The parallel equivalent reluctance is R_par = 1/(1/R_gap + 1/R_leak). The total reluctance for the released analytic benchmark is R_total = R_core + R_par, where R_core = l_core/(mu0*mu_r*A). The total core flux is Phi_core = F / R_total. Useful air-gap flux is Phi_gap = (1-sigma)*Phi_core and leakage flux is Phi_leak = sigma*Phi_core. The series core magnetic potential drop plus the branch drop balance the exciting-coil mmf: N*I - Vm_core - Vm_gap = 0, equivalently the sum of series core drops plus the air-gap branch drop equals the exciting-coil mmf. Induced-voltage phasor magnitude for sinusoidal flux satisfies |U| = 2*pi*f*N*|Phi|. The exciting-coil induced voltage is oriented positive with respect to the defined positive electric direction. The measuring-coil induced voltage is oriented negative with respect to the positive useful-flux / air-gap flux direction.

Using the released nominal benchmark parameters from 12_09_analytic_verification_procedure.txt for the 2.0 A RMS endpoint, the expected analytic values are: Total core reluctance R_total = 5.289249e+05 A/Wb; air-gap reluctance R_gap = 1.909859e+06 A/Wb; equivalent gap/leak reluctance R_par = 1.757071e+06 A/Wb; total core flux Phi_core = 5.249354e-04 Wb; useful air-gap flux Phi_gap = 4.829406e-04 Wb; leakage flux Phi_leak = 4.199483e-05 Wb; core flux density B_core = 0.839897 T; gap flux density B_gap = 0.772705 T; core magnetic drop Vm_core = 277.651 A-turn; gap magnetic drop Vm_gap = 922.349 A-turn; exciting induced-voltage magnitude |U_exc| = 98.948 V RMS; measuring induced-voltage magnitude |U_meas| = 7.586 V RMS. These values are consistent with the observed ranges in 14_10_quasistatic_ramp_results.txt for the recorded nominal run, which reaches the same endpoint values and a useful/core ratio of 0.92, but the dataset remains reference evidence about one run rather than a commanded input.

Reported variables for later stages shall be exactly these names, with units and meanings: time_s [s], simulation time; I_rms_A [A], exciting-coil RMS current-phasor magnitude; mmf_At [A-turn], exciting-coil magnetomotive force magnitude N_exc*I_rms_A; Phi_core_Wb [Wb], total core flux magnitude before the split; Phi_gap_Wb [Wb], useful air-gap flux magnitude through GAP-1 and reported by FluxSensor with positive sign in the documented arrow direction; Phi_leak_Wb [Wb], leakage-branch flux magnitude through LEAK-1; Phi_gap_over_Phi_core [1], useful/core flux ratio; B_core_T [T], core flux density magnitude based on Phi_core_Wb and A; B_gap_T [T], air-gap flux density magnitude based on Phi_gap_Wb and A; H_core_A_m [A/m], iron field-strength magnitude; H_gap_A_m [A/m], air-gap field-strength magnitude; Vm_core_At [A-turn], total magnetic potential drop across the iron core path; Vm_gap_At [A-turn], magnetic potential drop across the air-gap branch; U_exc_induced_V_rms [V], exciting-coil induced-voltage magnitude with positive orientation; U_meas_induced_signed_V_rms [V], measuring-coil induced voltage with sign, negative for positive useful-flux direction in the released configuration. These names are chosen to align with the dataset variable names where available and to make the checks mechanically evaluable.

Simulation horizon for the released benchmark is 0 to 1.0 s because the engineering register and test procedures state stop time 1.0 s and the current ramp completes and holds within that interval. The notes do not state a solver tolerance directly; a numerical tolerance is therefore assigned only for simulation configuration, while acceptance tolerances come from the requirements and test procedure.

Acceptance behavior for this brief is based on the released nominal benchmark and analytic verification procedure. The model must instantiate both grounds, implement the stated current ramp, attain the 2.0 A RMS endpoint, produce positive mmf for positive exciting current, preserve the useful/core flux ratio of 0.92, satisfy mmf balance at 2.0 A within 0.5% of N*I, and match the released analytic endpoint magnitudes within 1% for fluxes, B values, and induced-voltage magnitudes. Because the measuring-coil polarity requirement is about sign orientation, the reported signed variable U_meas_induced_signed_V_rms is required and is checked to become negative during positive excitation; the analytic magnitude 7.586 V RMS is checked on its magnitude by negating the signed endpoint value under the released sign convention.

## Acceptance checks (13)

| # | when | expression | expected | tolerance | source |
| --- | --- | --- | --- | --- | --- |
| 1 | at 0.1 s | `I_rms_A <= 1e-9` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-ELC-003 |
| 2 | ever | `I_rms_A` | 2 | 0.001 | 02_02_magnetic_engineering_register.txt REQ-ELC-003 |
| 3 | final | `I_rms_A` | 2 | 0.001 | 02_02_magnetic_engineering_register.txt REQ-ELC-003 |
| 4 | ever | `mmf_At > 0` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-FUN-001 |
| 5 | final | `Phi_gap_over_Phi_core` | 0.92 | 0.002 | 02_02_magnetic_engineering_register.txt REQ-VV-002 |
| 6 | final | `abs(mmf_At - Vm_core_At - Vm_gap_At) / mmf_At <= 0.005` | 1 | 0 | 12_09_analytic_verification_procedure.txt |
| 7 | final | `Phi_core_Wb` | 0.000524935 | 5.24935e-06 | 12_09_analytic_verification_procedure.txt |
| 8 | final | `Phi_gap_Wb` | 0.000482941 | 4.82941e-06 | 12_09_analytic_verification_procedure.txt |
| 9 | final | `B_core_T` | 0.839897 | 0.00839897 | 12_09_analytic_verification_procedure.txt |
| 10 | final | `B_gap_T` | 0.772705 | 0.00772705 | 12_09_analytic_verification_procedure.txt |
| 11 | final | `U_exc_induced_V_rms` | 98.948 | 0.98948 | 12_09_analytic_verification_procedure.txt |
| 12 | ever | `U_meas_induced_signed_V_rms < 0` | 1 | 0 | 02_02_magnetic_engineering_register.txt REQ-IND-002 |
| 13 | final | `-U_meas_induced_signed_V_rms` | 7.586 | 0.07586 | 12_09_analytic_verification_procedure.txt |

## Conflicts resolved (6)

### Leakage coefficient sigma for the released benchmark

**Adopted:** sigma = 0.08 [current/effective, approved/released]

**Not adopted:**

- sigma = 0.05 rejected because it is tagged superseded/archived in 02_02_magnetic_engineering_register.txt, 05_04_model_definition_notes.txt, 09_05_magnetics_email_thread.txt, and 10_07_legacy_magnetic_circuit.txt.

**Evidence:** The engineering register states sigma 0.08 as current/effective and REQ-PER-001 requires it for the released benchmark configuration; CR-MAG-006 in the email thread approves 0.08; older 0.05 values are explicitly archived or superseded.

### Effective iron relative permeability for the linear benchmark

**Adopted:** mu_r = 1200 [current/effective, approved/released]

**Not adopted:**

- mu_r = 1000 rejected because it is tagged superseded/archived in 02_02_magnetic_engineering_register.txt, 05_04_model_definition_notes.txt, 10_07_legacy_magnetic_circuit.txt, and 11_08_core_coil_datasheet.txt.

**Evidence:** REQ-PER-002 in the engineering register requires 1200 for the released linear benchmark, CR-MAG-004 approves 1200 in the email thread and model notes, and older 1000 values are explicitly superseded or archived.

### Measuring-coil turns

**Adopted:** N_meas = 50 turn [current/effective, approved/released]

**Not adopted:**

- 40 turn rejected because it is tagged superseded/archived in 02_02_magnetic_engineering_register.txt, 05_04_model_definition_notes.txt, 10_07_legacy_magnetic_circuit.txt, 11_08_core_coil_datasheet.txt, and referenced as outdated in 09_05_magnetics_email_thread.txt.

**Evidence:** REQ-ELC-002 requires 50 turns in the engineering register, the datasheet Rev B gives 50 approved/released, and older 40-turn values are explicitly superseded or archived.

### Air-gap length to use in the released nominal benchmark acceptance case

**Adopted:** delta = 1.50 mm nominal for the released analytic benchmark and AV-11 configuration

**Not adopted:**

- delta = 1.58 mm as-built rejected for the released nominal benchmark because it is prototype/as-built evidence, not the nominal benchmark value; it remains retained for prototype comparison only.

**Evidence:** The test procedure 12_09_analytic_verification_procedure.txt defines the released nominal magnetic circuit with delta 0.00150 m. The runbook 13_14_lab_validation_runbook.txt explicitly says use the nominal 1.50 mm gap for AV-11. The email thread 09_05_magnetics_email_thread.txt explicitly warns not to silently replace the 1.50 mm nominal gap in the analytic benchmark and says both nominal and as-built values are needed.

### Interpretation of the excitation current magnitude

**Adopted:** Current schedule uses RMS current-phasor magnitude, not peak current

**Not adopted:**

- 2.828 A peak rejected as the benchmark input representation because it appears only in uncontrolled scratch notes without an explicit representation-conversion requirement.

**Evidence:** REQ-ELC-003 defines the exciting current RMS phasor magnitude schedule, 12_09_analytic_verification_procedure.txt uses 2.0 A RMS, and 05_04_model_definition_notes.txt explicitly states EP-03 input current values are RMS phasor magnitudes and are not to be converted to peak values unless an explicit representation conversion is modeled.

### Whether to include nonlinear magnetic effects in the baseline model

**Adopted:** Baseline model is linear with constant effective relative permeability and excludes saturation, hysteresis, eddy-current loss, frequency-dependent permeability, and force interaction

**Not adopted:**

- Including nonlinear saturation or other nonlinear magnetic effects rejected because multiple notes explicitly reserve those effects for separate cases or exclude them from the baseline benchmark.

**Evidence:** 01_01_system_requirement_specification.txt states the core is linear in this benchmark and nonlinear saturation belongs only to a separate model variant. 02_02_magnetic_engineering_register.txt REQ-ASM-002 requires linear core reluctance with constant effective relative permeability and REQ-ASM-001 excludes force interaction. 07_13_flux_tube_theory_note.txt excludes nonlinear B-H, hysteresis, eddy-current loss, and frequency-dependent permeability for the baseline benchmark.

## Assumptions (4)

- For the reported endpoint checks, the final sample at 1.0 s represents the held 2.0 A RMS operating point specified by the requirements and test procedures.
- Vm_core_At is reported as the total iron-core magnetic potential drop across CORE-L, CORE-U, CORE-R, and CORE-D combined, because the notes give endpoint totals and mmf-balance checks at that aggregate level rather than requiring per-segment reported outputs.
- The executable released benchmark model uses the nominal 1.50 mm air gap, while the 1.58 mm as-built gap is retained only as separate prototype-comparison evidence and not mixed into the released nominal acceptance case.
- A simulation tolerance of 1e-6 is assigned for numerical configuration because the notes provide acceptance tolerances but do not state a solver tolerance.

## Source tables

| document | role | why |
| --- | --- | --- |
| 14_10_quasistatic_ramp_results.txt | `reference` | Document kind is dataset and all values are [observed], so it records one run for comparison and does not define the commanded input. |
| 15_12_geometry_metrology_export.txt | `supporting` | Provides nominal and as-built geometry evidence, including AV-11 using nominal geometry, but is not itself a time-varying simulation input table. |
