package Gapped_Core_Magnetic_Circuit_Ramped_Excitation {
  part def ExcitationCoil {
    attribute turns_nominal : ScalarValues::Integer = 500;
    attribute current_A : ScalarValues::Real = 0.0;
    attribute mmf_At : ScalarValues::Real = 0.0;
    doc /* Excitation coil with 500 turns nominal. Prescribed current input: linear ramp from 0 A at 0 s to 2 A at 0.1 s, then hold at 2 A through 1 s, per merged assumption and confirmed scenario. Report mmf_At for the whole run. */
  }

  part def Core {
    attribute mean_path_length_m : ScalarValues::Real = 0.4;
    attribute cross_section_m2 : ScalarValues::Real = 0.0004;
    attribute relative_permeability_nominal : ScalarValues::Real = 2000.0;
    attribute Phi_core_Wb : ScalarValues::Real = 0.0;
    attribute B_core_T : ScalarValues::Real = 0.0;
    attribute Vm_core_At : ScalarValues::Real = 0.0;
    doc /* Core, alias iron core. Mean path length 0.4 m, cross-section 0.0004 m^2, relative permeability 2000 nominal. Carries the same flux in series with the air gap. Report Phi_core_Wb, B_core_T, and Vm_core_At for the whole run. */
  }

  part def AirGap {
    attribute length_m : ScalarValues::Real = 0.002;
    attribute cross_section_m2 : ScalarValues::Real = 0.0004;
    attribute B_gap_T : ScalarValues::Real = 0.0;
    attribute Vm_gap_At : ScalarValues::Real = 0.0;
    doc /* Air gap with length 0.002 m and cross-section 0.0004 m^2 nominal. In series with the core and carries the same flux. Report B_gap_T and Vm_gap_At for the whole run. */
  }

  part def MagneticReference {
    doc /* One magnetic reference nominal. Human-confirmed answer retained the current draft topology connection Air_gap to Magnetic_reference and Magnetic_reference to magnetic_ground unless clarified reference placement is provided. */
  }

  part def MagneticGround {
    doc /* Exactly one magnetic ground. */
  }

  part Gapped_Core_Magnetic_Circuit {
    attribute simulation_duration_s : ScalarValues::Real = 1.0;
    attribute output_intervals : ScalarValues::Integer = 1000;
    attribute initial_time_s : ScalarValues::Real = 0.0;
    attribute ramp_end_time_s : ScalarValues::Real = 0.1;
    attribute final_time_s : ScalarValues::Real = 1.0;
    doc /* Gapped Core Magnetic Circuit — Ramped Excitation. Magnetic-circuit requirement case with prescribed excitation current ramp and reported magnetic quantities over time. The brief states no other equations, nonlinear magnetic properties, inductance values, or dynamic electrical circuit elements. */

    part Excitation_coil : ExcitationCoil {
      attribute turns_nominal : ScalarValues::Integer = 500;
      attribute current_A : ScalarValues::Real = 0.0;
      attribute mmf_At : ScalarValues::Real = 0.0;
      doc /* Canonical entity: Excitation coil. Coil current is prescribed model input: 0 A at 0 s, linearly ramped to 2 A at 0.1 s, then held at 2 A thereafter through 1 s. Explicit relationship note: mmf_At = N * I, with approved full-current reference value 500 * 2 = 1000 A-turn from AC-02 note. */
    }

    part Core_iron_path : Core {
      attribute mean_path_length_m : ScalarValues::Real = 0.4;
      attribute cross_section_m2 : ScalarValues::Real = 0.0004;
      attribute relative_permeability_nominal : ScalarValues::Real = 2000.0;
      attribute Phi_core_Wb : ScalarValues::Real = 0.0;
      attribute B_core_T : ScalarValues::Real = 0.0;
      attribute Vm_core_At : ScalarValues::Real = 0.0;
      doc /* Canonical entity: Core (iron path), alias iron core. Same flux as air gap in series. */
    }

    part Air_gap : AirGap {
      attribute length_m : ScalarValues::Real = 0.002;
      attribute cross_section_m2 : ScalarValues::Real = 0.0004;
      attribute B_gap_T : ScalarValues::Real = 0.0;
      attribute Vm_gap_At : ScalarValues::Real = 0.0;
      doc /* Canonical entity: Air gap. Same flux as core in series. Because core and air gap are stated to have the same flux and the same cross-section, the requirement note explicitly states that B_gap_T equals B_core_T. */
    }

    part Magnetic_reference : MagneticReference;
    part magnetic_ground : MagneticGround;

    connect Excitation_coil to Core_iron_path;
    connect Core_iron_path to Air_gap;
    connect Air_gap to Magnetic_reference;
    connect Magnetic_reference to magnetic_ground;

    state OperatingFlow {
      entry; then Initialization;

      state Initialization;
      state CurrentRamp_0_to_0_1_s;
      state Hold_At_2_A;
      state RunComplete;

      transition Initialization_to_CurrentRamp_0_to_0_1_s
        first Initialization
        if initial_time_s == 0.0
        do action { assign Excitation_coil.current_A := 0.0; assign Excitation_coil.mmf_At := 0.0; assign Core_iron_path.Phi_core_Wb := 0.0; assign Core_iron_path.B_core_T := 0.0; assign Air_gap.B_gap_T := 0.0; assign Core_iron_path.Vm_core_At := 0.0; assign Air_gap.Vm_gap_At := 0.0; }
        then CurrentRamp_0_to_0_1_s;

      transition CurrentRamp_0_to_0_1_s_to_Hold_At_2_A
        first CurrentRamp_0_to_0_1_s
        if ramp_end_time_s >= 0.1
        do action { assign Excitation_coil.current_A := 2.0; assign Excitation_coil.mmf_At := 1000.0; }
        then Hold_At_2_A;

      transition Hold_At_2_A_to_RunComplete
        first Hold_At_2_A
        if final_time_s >= simulation_duration_s
        then RunComplete;

      doc /* Ordered operating flow from the brief: initial condition at 0 s with 0 A and zero reported magnetic quantities; prescribed current rises linearly from 0 A at 0 s to 2 A at 0.1 s; every reported quantity shall rise with coil current during the 0–0.1 s ramp and then hold steady at its final value for the rest of the 1 s run; simulation duration is 1 s. No STOP, resume, shutdown, reset, or interlocks were stated in the evidence. */
    }

    requirement ReportingContract {
      doc /* Source: approved reported variables contract for later stages. Report these quantities for the whole run, not only at the end: mmf_At, Phi_core_Wb, B_core_T, B_gap_T, Vm_core_At, Vm_gap_At. */
    }
  }
}
