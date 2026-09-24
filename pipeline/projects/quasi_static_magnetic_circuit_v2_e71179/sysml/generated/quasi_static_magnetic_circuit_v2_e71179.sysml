package Quasi_Static_Magnetic_Circuit_Benchmark {

  part def MagneticSegment {
    attribute length_m : ScalarValues::Real;
    attribute area_m2 : ScalarValues::Real;
  }

  part def Coil {
    attribute turns : ScalarValues::Integer;
  }

  part def GroundReference {
  }

  part def FluxSensorDef {
    attribute Phi_gap_Wb : ScalarValues::Real;
  }

  part Benchmark_Magnetic_Circuit {
    doc /* benchmark magnetic circuit; released nominal analytic benchmark; linear and quasi-static baseline using complex-phasor represented quantities. Nonlinear B_H behavior, saturation, hysteresis, eddy_current loss, frequency_dependent permeability, and force interaction are excluded by the released baseline notes. */

    attribute time_s : ScalarValues::Real = 0.0;
    attribute simulation_start_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_s : ScalarValues::Real = 1.0;
    attribute simulation_tolerance : ScalarValues::Real = 1e-6;

    attribute a_m : ScalarValues::Real = 0.025;
    attribute l_m : ScalarValues::Real = 0.150;
    attribute delta_m : ScalarValues::Real = 0.00150;
    attribute prototype_gap_m : ScalarValues::Real = 0.00158;
    attribute prototype_gap_uncertainty_m : ScalarValues::Real = 2e-05;
    attribute mu_r : ScalarValues::Real = 1200.0;
    attribute sigma : ScalarValues::Real = 0.08;
    attribute f_Hz : ScalarValues::Real = 50.0;
    attribute mu0_H_per_m : ScalarValues::Real = 1.2566370614359173e-6;
    attribute A_m2 : ScalarValues::Real = 0.0006250000000000001;
    attribute l_core_m : ScalarValues::Real = 0.4985;

    attribute I_rms_A : ScalarValues::Real = 0.0;
    attribute mmf_At : ScalarValues::Real = 0.0;
    attribute Phi_core_Wb : ScalarValues::Real = 0.0;
    attribute Phi_gap_Wb : ScalarValues::Real = 0.0;
    attribute Phi_leak_Wb : ScalarValues::Real = 0.0;
    attribute Phi_gap_over_Phi_core : ScalarValues::Real = 0.92;
    attribute B_core_T : ScalarValues::Real = 0.0;
    attribute B_gap_T : ScalarValues::Real = 0.0;
    attribute H_core_A_m : ScalarValues::Real = 0.0;
    attribute H_gap_A_m : ScalarValues::Real = 0.0;
    attribute Vm_core_At : ScalarValues::Real = 0.0;
    attribute Vm_gap_At : ScalarValues::Real = 0.0;
    attribute U_exc_induced_V_rms : ScalarValues::Real = 0.0;
    attribute U_meas_induced_signed_V_rms : ScalarValues::Real = 0.0;

    attribute R_core_A_per_Wb : ScalarValues::Real = 0.0;
    attribute R_gap_A_per_Wb : ScalarValues::Real = 0.0;
    attribute R_leak_A_per_Wb : ScalarValues::Real = 0.0;
    attribute R_par_A_per_Wb : ScalarValues::Real = 0.0;
    attribute R_total_A_per_Wb : ScalarValues::Real = 0.0;

    part ExcitingCoil : Coil {
      attribute turns : ScalarValues::Integer = 600;
      doc /* exciting coil / ExcitingCoil; referenced to ElectricGround. Positive exciting_coil RMS current magnitude produces positive magnetomotive force. Exciting coil induced voltage is oriented positive with respect to the defined positive electric direction. */
    }

    part MeasuringCoil : Coil {
      attribute turns : ScalarValues::Integer = 50;
      doc /* measuring coil / MeasuringCoil; magnetically coupled to GAP_1 in the air_gap region. Measuring_coil induced voltage is oriented negative with respect to the positive useful_flux or air_gap flux direction in the released configuration. */
    }

    part FluxSensor : FluxSensorDef {
      doc /* useful_flux sensor / FluxSensor; reports useful air_gap flux through GAP_1 with positive sign in the documented arrow direction. */
    }

    part ElectricGround : GroundReference {
      doc /* electric ground / ElectricGround */
    }

    part MagneticGround : GroundReference {
      doc /* magnetic ground / MagneticGround */
    }

    part CORE_L : MagneticSegment {
      attribute length_m : ScalarValues::Real = 0.125;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      doc /* left leg / CORE_L */
    }

    part CORE_U : MagneticSegment {
      attribute length_m : ScalarValues::Real = 0.125;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      doc /* upper yoke / CORE_U */
    }

    part CORE_R : MagneticSegment {
      attribute length_m : ScalarValues::Real = 0.1235;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      doc /* right leg iron / CORE_R */
    }

    part CORE_D : MagneticSegment {
      attribute length_m : ScalarValues::Real = 0.125;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      doc /* lower yoke / CORE_D */
    }

    part GAP_1 : MagneticSegment {
      attribute length_m : ScalarValues::Real = 0.00150;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      doc /* air gap / GAP_1; released nominal benchmark gap. The distinct 0.00158 m as_built prototype gap is retained as separate evidence only and is not used in the released nominal acceptance case. */
    }

    part LEAK_1 : MagneticSegment {
      attribute length_m : ScalarValues::Real = 0.00150;
      attribute area_m2 : ScalarValues::Real = 0.0006250000000000001;
      doc /* leakage path / LEAK_1; parallel leakage_flux branch after CORE_R and before CORE_D. Released notes define this branch by leakage coefficient sigma and equivalent reluctance relation R_leak = R_gap*(1-sigma)/sigma, not by separate geometric metrology. length_m is carried only as a placeholder equal to the nominal air_gap length for topology readability; executable reluctance for this branch is determined from sigma and R_gap per the released benchmark relation. */
    }

    part CurrentRamp {
      doc /* Commanded RMS current_phasor magnitude source schedule applied to ExcitingCoil. Human_confirmed answer requires representing the ramp as a documented source schedule in this handoff, with the 0.10 s and 0.50 s operating transitions present and the continuous linear ramp behavior stated here for Stage 3 realization: 0 A until t = 0.10 s, linear ramp to 2.0 A by t = 0.50 s, then hold at 2.0 A through t = 1.0 s. Values are RMS phasor magnitudes and are not converted to peak values in this released benchmark handoff. */
      attribute initial_current_A : ScalarValues::Real = 0.0;
      attribute ramp_start_time_s : ScalarValues::Real = 0.10;
      attribute final_current_A : ScalarValues::Real = 2.0;
      attribute ramp_end_time_s : ScalarValues::Real = 0.50;
      attribute hold_end_time_s : ScalarValues::Real = 1.0;
    }

    connect ExcitingCoil to ElectricGround;
    connect CORE_L to CORE_U;
    connect CORE_U to CORE_R;
    connect CORE_R to GAP_1;
    connect CORE_R to LEAK_1;
    connect GAP_1 to CORE_D;
    connect LEAK_1 to CORE_D;
    connect CORE_D to MagneticGround;
    connect GAP_1 to FluxSensor;
    connect GAP_1 to MeasuringCoil;
    connect CurrentRamp to ExcitingCoil;

    state OperatingCycle {
      entry; then PreRampHold;

      state PreRampHold;
      state RampToFinalCurrent;
      state FinalHold;
      state Complete;

      transition PreRampHold_to_RampToFinalCurrent
        first PreRampHold
        if time_s >= 0.10
        then RampToFinalCurrent;

      transition RampToFinalCurrent_to_FinalHold
        first RampToFinalCurrent
        if time_s >= 0.50
        do action { assign I_rms_A := 2.0; }
        then FinalHold;

      transition FinalHold_to_Complete
        first FinalHold
        if time_s >= 1.0
        then Complete;
    }

    requirement REQ_BASELINE_LINEARITY {
      doc /* Released baseline rule from 05_04_model_definition_notes.txt and human_confirmed answers: the executable released benchmark remains linear and quasi_static, with constant effective relative permeability mu_r = 1200 and leakage coefficient sigma = 0.08, and excludes saturation, hysteresis, eddy_current loss, frequency_dependent permeability, and force interaction. */
    }

    requirement REQ_GROUNDS_PRESENT {
      doc /* Higher_authority notes require both ElectricGround and MagneticGround to be instantiated in the released benchmark topology. */
    }

    requirement REQ_MEASURING_POLARITY_RULE {
      doc /* Source REQ_IND_002 polarity rule: MeasuringCoil orientation is such that U_meas_induced_signed_V_rms is negative for positive useful_flux direction in the released configuration. */
    }

    requirement REQ_PARALLEL_BRANCH_RULE {
      doc /* Released branch rule: after CORE_R the magnetic circuit splits into parallel branches GAP_1 and LEAK_1, both rejoining before CORE_D; Vm_gap equals Vm_leak across the parallel branches, and flux continuity at the split is Phi_core = Phi_gap + Phi_leak. */
    }

    requirement REQ_NOMINAL_GAP_SELECTION {
      doc /* Released benchmark configuration rule from 09_05_magnetics_email_thread.txt and 13_14_lab_validation_runbook.txt: use nominal delta = 0.00150 m for the released analytic benchmark and AV_11; retain 0.00158 m as_built prototype gap only for separate prototype comparison evidence. */
    }
  }
}
