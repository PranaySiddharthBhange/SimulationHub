package Quasi_Static_Magnetic_Circuit_Benchmark {

part def Coil {
    attribute turns : ScalarValues::Integer;
    attribute current_rms_A : ScalarValues::Real;
    attribute induced_voltage_V : ScalarValues::Real;
    attribute polarity_note : ScalarValues::String;
}

part def MagneticElement {
    attribute length_m : ScalarValues::Real;
    attribute area_m2 : ScalarValues::Real;
    attribute reluctance_A_per_Wb : ScalarValues::Real;
    attribute flux_Wb : ScalarValues::Real;
    attribute flux_density_T : ScalarValues::Real;
    attribute magnetic_potential_At : ScalarValues::Real;
}

part def GroundRef {
    attribute reference_value : ScalarValues::Real;
}

action def Initial_Condition {
    doc /* source -> current_profile_active; at t = 0.0 s; command: exciting current RMS phasor magnitude = 0 A because profile is 0 A before 0.10 s; next: Current_Profile */
}

action def Current_Profile {
    doc /* source -> final_hold_checkpoint; command: exciting current RMS phasor magnitude is 0 A for t < 0.10 s, linear ramp from 0 A to 2.0 A for 0.10 s <= t <= 0.50 s, and 2.0 A for 0.50 s < t <= 1.0 s; duration: 0.0 s to 1.0 s; priority: textual ramp definition confirmed by clar_ramp_encoding_conflict; no scheduled valve or process commands apply */
}

action def Final_Hold_Checkpoint {
    doc /* source -> complete; at t = 1.0 s and held condition; report: N_exc*I, Phi_core, Phi_gap, Phi_leak, B and H, abs(U_exc), abs(U_meas); held-condition excerpt shows constant values from 0.93 s to 1.0 s */
}

state def Benchmark_Flow {
    doc /* ordered operating flow: Initial_Condition then Current_Profile then Final_Hold_Checkpoint; this benchmark is quasi-static commanded input, not a discrete-state control system; no valid pause/resume, shutdown, reset, stop interlock, or sequential valve logic is established */
}

requirement REQ_VV_001 {
    doc /* source: 02_02_magnetic_engineering_register_chunk01.txt REQ-VV-001; 12_09_analytic_verification_procedure.txt; at t=1.0: abs(residual)/(N_exc*I_rms) == 0.0 with absolute tolerance 0.005 */
}

requirement REQ_VV_002 {
    doc /* source: 02_02_magnetic_engineering_register_chunk01.txt REQ-VV-002; 12_09_analytic_verification_procedure.txt; at t=1.0: Phi_gap/Phi_core == 0.92 with absolute tolerance 0.002 */
}

requirement REQ_VV_003 {
    doc /* source: 02_02_magnetic_engineering_register_chunk01.txt REQ-VV-003; 12_09_analytic_verification_procedure.txt; at t=1.0: Phi_core == 0.0005249354167056515 Wb, Phi_gap == 0.00048294058336919936 Wb, B_core == 0.839897 T, B_gap == 0.772705 T, abs(U_exc) == 98.94799492389429 V, abs(U_meas) == 7.586012944165229 V; each with absolute tolerance 1e-06 */
}

requirement REQ_Leakage_Flux_Final_Hold {
    doc /* source: 12_09_analytic_verification_procedure.txt; at t=1.0: Phi_leak == 4.1994833336452115e-05 Wb with absolute tolerance 1e-06 */
}

requirement REQ_Gap_Magnetic_Potential_Final_Hold {
    doc /* source: 12_09_analytic_verification_procedure.txt; 02_02_magnetic_engineering_register_chunk03.txt; at t=1.0: Vm_gap == 922.3485727546998 A-turn with absolute tolerance 1e-06 */
}

part Quasi_Static_Magnetic_Circuit_Benchmark {
    attribute description : ScalarValues::String = "Released understanding of quasi-static linear magnetic-circuit benchmark with air gap and leakage branch";
    attribute simulation_start_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_s : ScalarValues::Real = 1.0;
    attribute simulation_tolerance : ScalarValues::Real = 0.005;
    attribute frequency_Hz : ScalarValues::Real = 50.0;
    attribute mu0_H_per_m : ScalarValues::Real = 1.2566370614359173e-06;
    attribute mu_r : ScalarValues::Real = 1200.0;
    attribute sigma : ScalarValues::Real = 0.08;
    attribute side_a_m : ScalarValues::Real = 0.025;
    attribute reference_dimension_l_m : ScalarValues::Real = 0.150;
    attribute cross_section_area_m2 : ScalarValues::Real = 0.000625;
    attribute gap_delta_m : ScalarValues::Real = 0.00150;
    attribute final_current_rms_A : ScalarValues::Real = 2.0;
    attribute applied_mmf_At : ScalarValues::Real = 1200.0;
    attribute total_iron_length_m : ScalarValues::Real = 0.4985;
    attribute core_reluctance_A_per_Wb : ScalarValues::Real = 528924.9275420654;
    attribute gap_reluctance_A_per_Wb : ScalarValues::Real = 1909859.3171027435;
    attribute leakage_reluctance_A_per_Wb : ScalarValues::Real = 21963382.14668155;
    attribute parallel_reluctance_A_per_Wb : ScalarValues::Real = 1757070.5717345239;
    attribute total_reluctance_A_per_Wb : ScalarValues::Real = 2285995.499276589;
    attribute core_drop_At : ScalarValues::Real = 277.651;
    attribute mmf_balance_residual_At : ScalarValues::Real = -4.547473508864641e-13;
    attribute useful_to_core_flux_ratio : ScalarValues::Real = 0.92;
    attribute prototype_gap_delta_m : ScalarValues::Real = 0.00158;
    attribute note : ScalarValues::String = "Electric ground and magnetic ground are present; released analytic benchmark and AV-11 use nominal 1.50 mm gap; 1.58 mm is retained only for prototype comparison";

    part Exciting_Coil : Coil {
        attribute turns : ScalarValues::Integer = 600;
        attribute current_rms_A : ScalarValues::Real = 2.0;
        attribute induced_voltage_V : ScalarValues::Real = 98.94799492389429;
        attribute polarity_note : ScalarValues::String = "positive exciting-coil RMS current produces positive mmf; exciting-coil induced voltage oriented positive with respect to the defined positive electric direction";
    }

    part Measuring_Coil : Coil {
        attribute turns : ScalarValues::Integer = 50;
        attribute current_rms_A : ScalarValues::Real = 0.0;
        attribute induced_voltage_V : ScalarValues::Real = -7.586012944165229;
        attribute polarity_note : ScalarValues::String = "measuring-coil induced voltage is oriented negative relative to the positive useful air-gap flux direction";
    }

    part Electric_Ground : GroundRef {
        attribute reference_value : ScalarValues::Real = 0.0;
    }

    part Magnetic_Ground : GroundRef {
        attribute reference_value : ScalarValues::Real = 0.0;
    }

    part Iron_Core {
        attribute relative_permeability : ScalarValues::Real = 1200.0;
        attribute total_reluctance_A_per_Wb : ScalarValues::Real = 528924.9275420654;

        part Left_Leg : MagneticElement {
            attribute length_m : ScalarValues::Real = 0.125;
            attribute area_m2 : ScalarValues::Real = 0.000625;
            attribute reluctance_A_per_Wb : ScalarValues::Real = 132628.11121917438;
            attribute flux_Wb : ScalarValues::Real = 0.0005249354167056515;
            attribute flux_density_T : ScalarValues::Real = 0.839897;
            attribute magnetic_potential_At : ScalarValues::Real = 0.0;
        }

        part Upper_Yoke : MagneticElement {
            attribute length_m : ScalarValues::Real = 0.125;
            attribute area_m2 : ScalarValues::Real = 0.000625;
            attribute reluctance_A_per_Wb : ScalarValues::Real = 132628.11121917438;
            attribute flux_Wb : ScalarValues::Real = 0.0005249354167056515;
            attribute flux_density_T : ScalarValues::Real = 0.839897;
            attribute magnetic_potential_At : ScalarValues::Real = 0.0;
        }

        part Right_Leg_Iron_Section : MagneticElement {
            attribute length_m : ScalarValues::Real = 0.1235;
            attribute area_m2 : ScalarValues::Real = 0.000625;
            attribute reluctance_A_per_Wb : ScalarValues::Real = 131040.59388454222;
            attribute flux_Wb : ScalarValues::Real = 0.0005249354167056515;
            attribute flux_density_T : ScalarValues::Real = 0.839897;
            attribute magnetic_potential_At : ScalarValues::Real = 0.0;
        }

        part Lower_Yoke : MagneticElement {
            attribute length_m : ScalarValues::Real = 0.125;
            attribute area_m2 : ScalarValues::Real = 0.000625;
            attribute reluctance_A_per_Wb : ScalarValues::Real = 132628.11121917438;
            attribute flux_Wb : ScalarValues::Real = 0.0005249354167056515;
            attribute flux_density_T : ScalarValues::Real = 0.839897;
            attribute magnetic_potential_At : ScalarValues::Real = 0.0;
        }

        part Air_Gap : MagneticElement {
            doc /* aliases: AirGap, GAP-1, Gap-1; contains measuring coil and flux sensor in the established sense */
            attribute length_m : ScalarValues::Real = 0.00150;
            attribute area_m2 : ScalarValues::Real = 0.000625;
            attribute reluctance_A_per_Wb : ScalarValues::Real = 1909859.3171027435;
            attribute flux_Wb : ScalarValues::Real = 0.00048294058336919936;
            attribute flux_density_T : ScalarValues::Real = 0.772705;
            attribute magnetic_potential_At : ScalarValues::Real = 922.3485727546998;
        }

        part Leakage_Branch : MagneticElement {
            doc /* aliases: Leakage Branch, leakage, LEAK-1, Leak-1; parallel with useful air-gap branch */
            attribute length_m : ScalarValues::Real = 0.0;
            attribute area_m2 : ScalarValues::Real = 0.000625;
            attribute reluctance_A_per_Wb : ScalarValues::Real = 21963382.14668155;
            attribute flux_Wb : ScalarValues::Real = 4.1994833336452115e-05;
            attribute flux_density_T : ScalarValues::Real = 0.06719173333832338;
            attribute magnetic_potential_At : ScalarValues::Real = 922.3485727546998;
        }
    }

    part Flux_Sensor {
        attribute sensed_flux_Wb : ScalarValues::Real = 0.00048294058336919936;
        attribute sign_note : ScalarValues::String = "positive sign defined by the air-gap flux arrow; sensor senses useful air-gap flux Phi_gap";
    }

    connection Exciting_Coil_to_Iron_Core connect Exciting_Coil to Iron_Core;
    connection Measuring_Coil_to_Air_Gap connect Measuring_Coil to Iron_Core.Air_Gap;
    connection Flux_Sensor_to_Air_Gap connect Flux_Sensor to Iron_Core.Air_Gap;
    connection Iron_Core_to_Magnetic_Ground connect Iron_Core to Magnetic_Ground;
    connection Exciting_Coil_to_Electric_Ground connect Exciting_Coil to Electric_Ground;
    connection Measuring_Coil_to_Electric_Ground connect Measuring_Coil to Electric_Ground;
    connection Left_Leg_to_Upper_Yoke connect Iron_Core.Left_Leg to Iron_Core.Upper_Yoke;
    connection Upper_Yoke_to_Right_Leg_Iron_Section connect Iron_Core.Upper_Yoke to Iron_Core.Right_Leg_Iron_Section;
    connection Right_Leg_Iron_Section_to_Air_Gap connect Iron_Core.Right_Leg_Iron_Section to Iron_Core.Air_Gap;
    connection Right_Leg_Iron_Section_to_Leakage_Branch connect Iron_Core.Right_Leg_Iron_Section to Iron_Core.Leakage_Branch;
    connection Air_Gap_to_Lower_Yoke connect Iron_Core.Air_Gap to Iron_Core.Lower_Yoke;
    connection Leakage_Branch_to_Lower_Yoke connect Iron_Core.Leakage_Branch to Iron_Core.Lower_Yoke;

    state Operating_Flow : Benchmark_Flow;

    doc /* topology: exciting coil provides magnetic potential source N*I to the rectangular iron core. The series path is Left_Leg then Upper_Yoke then Right_Leg_Iron_Section. After the right-leg branch point, the useful path through Air_Gap and the leakage path through Leakage_Branch are connected in parallel and rejoin before Lower_Yoke. Flux sensor is connected to useful air-gap flux Phi_gap. Measuring coil is magnetically coupled to the air gap. Continuous relationships established in the notes: B = Phi / A; H_iron = B / (mu0 * mu_r); H_air = B / mu0; Vm = H * length; iron reluctance = length / (mu0 * mu_r * A); R_gap = delta / (mu0 * A); Phi_core = Phi_gap + Phi_leak; branch magnetic potential across Air_Gap and Leakage_Branch is equal; Phi_gap = (1 - sigma) * Phi_core; Phi_leak = sigma * Phi_core; R_leak = R_gap * (1 - sigma) / sigma; R_par = 1 / (1 / R_gap + 1 / R_leak); R_total = R_core + R_par. Rejected as stray contamination: valve names, tank text, and unsupported IF/THEN valve logic. Rejected dimensional conflict: N*I = 0.92 * Phi_core is not accepted. */
}

}
