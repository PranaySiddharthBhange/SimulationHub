package Held_Mass_Released_Onto_A_Spring_Damper_Underdamped_Oscillation_To_Rest {
  part def MassDef {
    attribute mass_kg : ScalarValues::Real = 1.0;
    attribute position_m : ScalarValues::Real = 0.10;
    attribute velocity_m_s : ScalarValues::Real = 0.0;
    doc /* Reported variables: position_m [m], velocity_m_s [m/s]. position_m is the Mass position relative to the spring natural-length position. Extra entity-list position entries 0 m [current] and -0.0729 m [current] are preserved as non-executable contextual values with no stated timing or role per human-confirmed clarification. */
  }

  part def SpringDef {
    attribute stiffness_N_per_m : ScalarValues::Real = 1.0;
    attribute natural_length_position_m : ScalarValues::Real = 0.0;
  }

  part def DamperDef {
    attribute damping_coefficient_N_s_per_m : ScalarValues::Real = 0.2;
  }

  part def ClampDef {
    attribute held_position_m : ScalarValues::Real = 0.10;
    attribute start_time_s : ScalarValues::Real = 0.0;
    attribute release_time_s : ScalarValues::Real = 5.0;
    attribute clamp_engaged : ScalarValues::Integer = 1;
    doc /* clamp_engaged encoding is the confirmed execution assumption: 1 while engaged and 0 after release. */
  }

  part def FixedWallDef {
  }

  part def Held_Mass_Released_Onto_A_Spring_Damper_System {
    part Mass : MassDef;
    part Spring : SpringDef;
    part Damper : DamperDef;
    part Clamp : ClampDef;
    part fixed_wall : FixedWallDef;

    attribute simulation_start_time_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_time_s : ScalarValues::Real = 150.0;
    attribute report_position_m : ScalarValues::Boolean = true;
    attribute report_velocity_m_s : ScalarValues::Boolean = true;
    attribute report_clamp_engaged : ScalarValues::Boolean = true;

    attribute governing_equation_applies_post_release_only : ScalarValues::Boolean = true;
    attribute damping_ratio_zeta : ScalarValues::Real = 0.1;
    attribute natural_frequency_rad_per_s : ScalarValues::Real = 1.0;
    attribute damped_natural_frequency_rad_per_s : ScalarValues::Real = 0.995;
    doc /* Explicit physical relationship after release: m*x'' + c*x' + k*x = 0. Units balance as force: kg*m/s^2 = N, N*s/m * m/s = N, N/m * m = N. Explicit evidence gives zeta = 0.1, omega_n = 1 rad/s, omega_d ~= 0.995 rad/s. Explicit execution assumption retained: the free-motion governing equation applies only for t >= 5 s after clamp release; before release, clamp holding overrides free motion. Explicit execution assumption retained for the stated closed-form expression: dt = t - 5 s for t >= 5 s. */

    connect Mass to Spring;
    connect Spring to fixed_wall;
    connect Mass to Damper;
    connect Damper to fixed_wall;
    connect Mass to Clamp;

    requirement REQ_FUN_001 {
      doc /* Source: 01_spring_mass_release.txt <REQ-FUN-001>. While the Clamp is engaged from t = 0 s until t = 5 s, the Clamp holds the Mass fixed at x = 0.10 m with velocity 0 m/s. */
    }

    requirement REQ_FUN_002 {
      doc /* Source: 01_spring_mass_release.txt <REQ-FUN-002>. At t = 5 s, the Clamp releases once; after release clamp_engaged becomes 0 and the Clamp no longer holds the Mass fixed. */
    }

    requirement REQ_FUN_003 {
      doc /* Source: 01_spring_mass_release.txt <REQ-FUN-003>. After release, the motion is underdamped and overshoots past the spring natural-length position so that position_m becomes negative before settling; the approach to 0 m is not monotonic. */
    }

    state OperatingCycle {
      entry; then Clamp_Engaged_Holding;

      state Clamp_Engaged_Holding;
      state Released_Free_Oscillation;
      state Completed_Run;

      transition Clamp_Engaged_Holding_to_Released_Free_Oscillation
        first Clamp_Engaged_Holding
        if Clamp.release_time_s >= 5.0
        do action { assign Clamp.clamp_engaged := 0; assign Mass.position_m := 0.10; assign Mass.velocity_m_s := 0.0; }
        then Released_Free_Oscillation;

      transition Released_Free_Oscillation_to_Completed_Run
        first Released_Free_Oscillation
        if simulation_stop_time_s >= 150.0
        then Completed_Run;

      doc /* Ordered operating flow from the evidence: initial condition at t = 0 s is Clamp engaged and holding the Mass at position_m = 0.10 m and velocity_m_s = 0 m/s. The single discrete event is a one-time clamp release at t = 5 s. After release, Mass motion follows the stated underdamped free response rather than remaining clamped. No STOP, pause, resume, reset, shutdown, travel limit, gravity term, additional actuator, external force, or nonlinear spring law is stated in the brief. */
    }

    doc /* Topology: Spring connects Mass to fixed wall. Damper also connects Mass to fixed wall in parallel with the Spring. Clamp holds the Mass fixed while engaged. Simulation requirement: simulate for 150 s and report position_m, velocity_m_s, and clamp_engaged for the whole run. */
  }
}