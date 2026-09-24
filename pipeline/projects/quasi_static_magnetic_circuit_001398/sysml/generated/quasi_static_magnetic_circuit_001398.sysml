package Quasi_Static_Magnetic_Circuit_Benchmark {

  part def IronCoreSegment {
    attribute length_m : ScalarValues::Real;
    attribute area_m2 : ScalarValues::Real;
    attribute mu_r : ScalarValues::Real;
    attribute reluctance_A_per_Wb : ScalarValues::Real;
  }

  part def AirGapSegment {
    attribute length_m : ScalarValues::Real;
    attribute area_m2 : ScalarValues::Real;
    attribute reluctance_A_per_Wb : ScalarValues::Real;
  }

  part def LeakageBranch {
    attribute sigma : ScalarValues::Real;
    attribute reluctance_A_per_Wb : ScalarValues::Real;
  }

  part def Coil {
    attribute turns : ScalarValues::Integer;
  }

  part def CurrentSourceSchedule {
    attribute hold_start_current_A_rms : ScalarValues::Real;
    attribute ramp_start_time_s : ScalarValues::Real;
    attribute ramp_end_time_s : ScalarValues::Real;
    attribute final_time_s : ScalarValues::Real;
    attribute final_current_A_rms : ScalarValues::Real;
    attribute I_rms_A : ScalarValues::Real;
    doc /* RMS current phasor magnitude source; not an instantaneous sinusoidal waveform and not a peak phasor magnitude unless an explicit representation conversion is added, which is not included here. Human-confirmed handling: represent the schedule by source attributes plus explicit ZeroHold, LinearRamp, and FinalHold state progression. */
  }

  part MagneticCircuitBenchmark {
    doc /* benchmark magnetic circuit / quasi-static magnetic circuit / magnetic circuit. Linear quasi-static magnetic circuit benchmark; not a nonlinear or force-producing actuator model. */

    attribute time_s : ScalarValues::Real;
    attribute mu0_H_per_m : ScalarValues::Real = 0.0000012566370614359173;
    attribute frequency_Hz : ScalarValues::Real = 50.0;
    attribute a_m : ScalarValues::Real = 0.025;
    attribute A_m2 : ScalarValues::Real = 0.0006250000000000001;
    attribute l_m : ScalarValues::Real = 0.15;
    attribute delta_nominal_m : ScalarValues::Real = 0.00150;
    attribute delta_as_built_m : ScalarValues::Real = 0.00158;
    attribute delta_as_built_uncertainty_m : ScalarValues::Real = 0.00002;
    attribute simulation_start_time_s : ScalarValues::Real = 0.0;
    attribute simulation_end_time_s : ScalarValues::Real = 1.0;

    attribute I_rms_A : ScalarValues::Real;
    attribute mmf_At : ScalarValues::Real;
    attribute Phi_core_Wb : ScalarValues::Real;
    attribute Phi_gap_Wb : ScalarValues::Real;
    attribute Phi_leak_Wb : ScalarValues::Real;
    attribute Phi_gap_over_Phi_core : ScalarValues::Real;
    attribute B_core_T : ScalarValues::Real;
    attribute B_gap_T : ScalarValues::Real;
    attribute H_core_A_m : ScalarValues::Real;
    attribute H_gap_A_m : ScalarValues::Real;
    attribute Vm_core_At : ScalarValues::Real;
    attribute Vm_gap_At : ScalarValues::Real;
    attribute U_exc_induced_V_rms : ScalarValues::Real;
    attribute U_meas_induced_signed_V_rms : ScalarValues::Real;

    part ElectricGround;
    part MagneticGround;

    part CORE_L : IronCoreSegment {
      attribute length_m : ScalarValues::Real = 0.125;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      attribute mu_r : ScalarValues::Real = 1200.0;
      attribute reluctance_A_per_Wb : ScalarValues::Real = 132319.2;
    }

    part CORE_U : IronCoreSegment {
      attribute length_m : ScalarValues::Real = 0.125;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      attribute mu_r : ScalarValues::Real = 1200.0;
      attribute reluctance_A_per_Wb : ScalarValues::Real = 132319.2;
    }

    part CORE_R : IronCoreSegment {
      attribute length_m : ScalarValues::Real = 0.1235;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      attribute mu_r : ScalarValues::Real = 1200.0;
      attribute reluctance_A_per_Wb : ScalarValues::Real = 130732.3;
    }

    part CORE_D : IronCoreSegment {
      attribute length_m : ScalarValues::Real = 0.125;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      attribute mu_r : ScalarValues::Real = 1200.0;
      attribute reluctance_A_per_Wb : ScalarValues::Real = 132319.2;
    }

    part GAP_1 : AirGapSegment {
      attribute length_m : ScalarValues::Real = 0.00150;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      attribute reluctance_A_per_Wb : ScalarValues::Real = 1909859.0;
      doc /* useful branch element; nominal released benchmark configuration AV_11 uses delta = 1.50 mm. */
    }

    part LEAK_1 : LeakageBranch {
      attribute sigma : ScalarValues::Real = 0.08;
      attribute reluctance_A_per_Wb : ScalarValues::Real = 21963378.5;
      doc /* leakage branch in parallel with GAP_1. Derived from R_leak = R_gap*(1-sigma)/sigma using sigma = 0.08 and GAP_1 reluctance 1909859 A/Wb. */
    }

    part ExcitingCoil : Coil {
      attribute turns : ScalarValues::Integer = 600;
      doc /* wound on the left leg; provides positive magnetic mmf for positive exciting-coil current. Exciting-coil induced voltage is oriented positive with respect to the defined positive electric direction. */
    }

    part MeasuringCoil : Coil {
      attribute turns : ScalarValues::Integer = 50;
      doc /* located at the air-gap region; induced-voltage orientation is opposite to the exciting coil orientation in the benchmark and specifically negative relative to the positive useful air-gap flux arrow. 40 turns is archived superseded legacy content. */
    }

    part FluxSensor {
      doc /* senses useful air-gap flux through GAP_1. */
    }

    part CurrentRamp : CurrentSourceSchedule {
      attribute hold_start_current_A_rms : ScalarValues::Real = 0.0;
      attribute ramp_start_time_s : ScalarValues::Real = 0.10;
      attribute ramp_end_time_s : ScalarValues::Real = 0.50;
      attribute final_time_s : ScalarValues::Real = 1.0;
      attribute final_current_A_rms : ScalarValues::Real = 2.0;
      attribute I_rms_A : ScalarValues::Real = 0.0;
    }

    connect CORE_L to CORE_U;
    connect CORE_U to CORE_R;
    connect CORE_R to GAP_1;
    connect CORE_R to LEAK_1;
    connect GAP_1 to CORE_D;
    connect LEAK_1 to CORE_D;
    connect CORE_D to MagneticGround;
    connect CurrentRamp to ExcitingCoil;
    connect ExcitingCoil to ElectricGround;
    connect ExcitingCoil to CORE_L;
    connect GAP_1 to FluxSensor;
    connect GAP_1 to MeasuringCoil;

    state OperatingFlow {
      entry; then InitialCondition;
      state InitialCondition;
      state ZeroHold;
      state LinearRamp;
      state FinalHold;
      state Complete;

      transition InitialCondition_to_ZeroHold
        first InitialCondition
        if time_s >= simulation_start_time_s
        do action { assign I_rms_A := 0.0; assign mmf_At := 0.0; assign Phi_core_Wb := 0.0; assign Phi_gap_Wb := 0.0; assign Phi_leak_Wb := 0.0; assign Phi_gap_over_Phi_core := 0.92; assign B_core_T := 0.0; assign B_gap_T := 0.0; assign H_core_A_m := 0.0; assign H_gap_A_m := 0.0; assign Vm_core_At := 0.0; assign Vm_gap_At := 0.0; assign U_exc_induced_V_rms := 0.0; assign U_meas_induced_signed_V_rms := 0.0; }
        then ZeroHold;

      transition ZeroHold_to_LinearRamp
        first ZeroHold
        if time_s >= 0.10
        do assign I_rms_A := 0.0
        then LinearRamp;

      transition LinearRamp_to_FinalHold
        first LinearRamp
        if time_s >= 0.50
        do action { assign I_rms_A := 2.0; assign mmf_At := 1200.0; assign Phi_core_Wb := 0.0005249354; assign Phi_gap_Wb := 0.0004829406; assign Phi_leak_Wb := 0.00004199483; assign Phi_gap_over_Phi_core := 0.92; assign B_core_T := 0.839897; assign B_gap_T := 0.772705; assign H_core_A_m := 556.7493743619639; assign H_gap_A_m := 614903.3538098636; assign Vm_core_At := 277.651; assign Vm_gap_At := 922.349; assign U_exc_induced_V_rms := 98.948; assign U_meas_induced_signed_V_rms := -7.586; }
        then FinalHold;

      transition FinalHold_to_Complete
        first FinalHold
        if time_s >= 1.0
        do assign I_rms_A := 2.0
        then Complete;
    }

    requirement REQ_IND_002 {
      doc /* source: 02_02_magnetic_engineering_register.txt REQ-IND-002. Measuring-coil induced-voltage orientation is negative relative to the positive air-gap flux direction shown in the reference configuration. */
    }

    requirement REQ_PARALLEL_BRANCH_EQUALITY {
      doc /* source: Resolved understanding physical relationships. The magnetic potential difference across GAP_1 equals the magnetic potential difference across LEAK_1 because those elements are in parallel. */
    }

    requirement REQ_BASELINE_EXCLUSIONS {
      doc /* source: Baseline exclusions and modeling boundaries. Force interaction shall not be modeled. Saturation, nonlinear B-H behavior, hysteresis, eddy-current loss, and frequency-dependent permeability are excluded from the baseline linear benchmark. */
    }

    doc /* released nominal benchmark configuration uses mu_r = 1200, sigma = 0.08, N_meas = 50 turns, and nominal delta = 0.00150 m. Separate prototype/as-built configuration retains delta = 0.00158 m with stated uncertainty 2e-05 m and is not used to replace AV_11 nominal geometry. */
    doc /* reported variables shall be: time_s, I_rms_A, mmf_At, Phi_core_Wb, Phi_gap_Wb, Phi_leak_Wb, Phi_gap_over_Phi_core, B_core_T, B_gap_T, H_core_A_m, H_gap_A_m, Vm_core_At, Vm_gap_At, U_exc_induced_V_rms, U_meas_induced_signed_V_rms. */
    doc /* total core reluctance stated for AV_11 final point: 5.289249e+05 A/Wb. Equivalent gap/leak reluctance stated: 1.757071e+06 A/Wb. Final nominal analytic values at 2.0 A RMS: Phi_core_Wb 5.249354e-04, Phi_gap_Wb 4.829406e-04, Phi_leak_Wb 4.199483e-05, B_core_T 0.839897, B_gap_T 0.772705, Vm_core_At 277.651, Vm_gap_At 922.349, U_exc_induced_V_rms 98.948, U_meas_induced_signed_V_rms -7.586. */
    doc /* one dataset note writes area unit as m, but resolved interpretation uses m^2 because the requirement and engineering register define area and list A = 0.0006250000000000001 m^2 for the magnetic elements. */
    doc /* quasistatic_ramp_results is reference evidence of one observed 0..1 s run and confirms observed ranges and the 0.92 useful/core ratio at observed times 0.105 s and 1.0 s; it is not a commanded input table. geometry_metrology_export is supporting evidence for nominal and as-built geometry values and metrology provenance; it does not prescribe the simulation input schedule. */
  }
}
