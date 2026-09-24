package Two_Tanks_One_Above_The_Other_Gravity_Flow_To_Equilibrium {

part def OpenTank {
  attribute level_m : ScalarValues::Real;
  attribute cross_sectional_area_m2 : ScalarValues::Real;
  attribute height_m : ScalarValues::Real;
}

part def ConnectingValve {
  attribute valve_open_cmd : ScalarValues::Integer;
}

part def ConnectingFlow {
  attribute q_m3s : ScalarValues::Real;
  attribute k_m2s : ScalarValues::Real;
  doc /* Explicit physical relationship from 01_two_tank_equilibrium.txt: q = k * (level_A - level_B) when the Connecting valve is open. Human-confirmed and merged executable interpretation: during 0 to 5 s with valve_open_cmd = 0, q_m3s = 0; after opening, q_m3s = k * (level_A_m - level_B_m) with k = 0.025 m^2/s. */
}

part def Two_Tank_System {
  part Tank_A : OpenTank {
    doc /* Canonical entity: Tank A (upper tank); alias: Tank A (upper). Report variable: level_A_m in m. */
    attribute level_m : ScalarValues::Real = 0.80;
    attribute cross_sectional_area_m2 : ScalarValues::Real = 0.5;
    attribute height_m : ScalarValues::Real = 1.0;
  }

  part Tank_B : OpenTank {
    doc /* Canonical entity: Tank B (lower tank); alias: Tank B (lower). Report variable: level_B_m in m. */
    attribute level_m : ScalarValues::Real = 0.00;
    attribute cross_sectional_area_m2 : ScalarValues::Real = 0.5;
    attribute height_m : ScalarValues::Real = 1.0;
  }

  part Connecting_valve : ConnectingValve {
    doc /* Canonical entity: Connecting valve. Report variable: valve_open_cmd as 0 or 1 for commanded closed/open state of the on/off valve. */
    attribute valve_open_cmd : ScalarValues::Integer = 0;
  }

  part Connecting_flow : ConnectingFlow {
    doc /* Canonical entity: Connecting flow. Report variable: q_m3s in m^3/s through the single connecting pipe and valve. */
    attribute q_m3s : ScalarValues::Real;
    attribute k_m2s : ScalarValues::Real = 0.025;
  }

  attribute level_A_m : ScalarValues::Real = 0.80;
  attribute level_B_m : ScalarValues::Real = 0.00;
  attribute valve_open_cmd : ScalarValues::Integer = 0;
  attribute q_m3s : ScalarValues::Real;
  attribute total_level_sum_m : ScalarValues::Real = 0.80;
  attribute equilibrium_level_each_m : ScalarValues::Real = 0.40;
  attribute closed_interval_start_s : ScalarValues::Real = 0.0;
  attribute closed_interval_end_s : ScalarValues::Real = 5.0;
  attribute valve_open_time_s : ScalarValues::Real = 5.0;
  attribute simulation_duration_s : ScalarValues::Real = 150.0;
  attribute simulation_tolerance : ScalarValues::Real = 0.001;
  attribute sample_time_pre_open_s : ScalarValues::Real = 4.0;
  attribute sample_time_post_open_s : ScalarValues::Real = 6.0;
  attribute sample_time_flow_visible_s : ScalarValues::Real = 15.0;
  attribute sample_time_equilibrium_approach_s : ScalarValues::Real = 45.0;
  attribute sample_time_acceptance_s : ScalarValues::Real = 150.0;
  attribute tau_s : ScalarValues::Real = 10.0;

  connect Tank_A to Connecting_valve;
  connect Connecting_valve to Tank_B;
  connect Connecting_valve to Connecting_flow;

  doc /* Topology from 01_two_tank_equilibrium.txt: Tank A is physically above Tank B. Two open tanks are joined by a single pipe with the Connecting valve. The connections express the single physical route Tank_A -> Connecting_valve -> Tank_B, with Connecting_flow representing the reported volumetric flow through that route. */
  doc /* Conserved quantity explicitly stated: level_A + level_B is constant at 0.80 m from t = 0 onward, before and after the valve opens. Derived reasoning: because Tank_A and Tank_B have equal constant cross-sectional area 0.5 m^2, constant total level sum is consistent with conservation of total liquid volume up to the common area factor. */
  doc /* Stated time constant from 01_two_tank_equilibrium.txt: tau = area / (2*k) = 10 s. Derived check retained from the merged Understanding: with area = 0.5 m^2 and k = 0.025 m^2/s, tau = 0.5 / (2*0.025) = 10 s, with units (m^2)/(m^2/s) = s, so the stated relationship is numerically and dimensionally consistent. */
  doc /* REQ-SIM-001 requires simulation for 150 seconds and reporting of both tank levels and the connecting valve open/closed command for the whole run. Merge also includes q_m3s as a reported variable so that REQ-FUN-002 flow shall begin can be checked mechanically. Acceptance/check times named in the note: 4 s, 6 s, 15 s, 45 s, and 150 s. */

  requirement REQ_FUN_001 {
    doc /* Source: 01_two_tank_equilibrium.txt <REQ-FUN-001>. Rule: the Connecting valve shall stay closed and both levels shall stay exactly at their starting values for the entire closed interval, t = 0 s to t = 5 s. */
  }

  requirement REQ_FUN_003 {
    doc /* Source: 01_two_tank_equilibrium.txt <REQ-FUN-003>. Rule: the system shall relax toward a shared equilibrium level of 0.40 m in each tank and shall stay there for the remainder of the run once reached. */
  }

  requirement REQ_SAF_001 {
    doc /* Source-grounded executable rule from merged assumptions and human-confirmed answer: while Connecting_valve.valve_open_cmd = 0 during 0 s to 5 s, Connecting_flow.q_m3s is inhibited to zero; after opening at absolute simulation time t = 5 s, Connecting_flow.q_m3s follows q = k * (level_A_m - level_B_m). */
  }

  state OperatingCycle {
    entry; then Valve_Closed_Interval;

    state Valve_Closed_Interval;
    state Valve_Open_Transfer;
    state Equilibrium_Reached;
    state Run_Complete;

    transition Valve_Closed_Interval_to_Valve_Open_Transfer
      first Valve_Closed_Interval
      if closed_interval_end_s >= 5.0
      do action { assign Connecting_valve.valve_open_cmd := 1; assign valve_open_cmd := 1; }
      then Valve_Open_Transfer;

    transition Valve_Open_Transfer_to_Equilibrium_Reached
      first Valve_Open_Transfer
      if (Tank_A.level_m <= 0.40) and (Tank_B.level_m >= 0.40)
      then Equilibrium_Reached;

    transition Equilibrium_Reached_to_Run_Complete
      first Equilibrium_Reached
      if simulation_duration_s >= 150.0
      then Run_Complete;

    doc /* Ordered operating flow from the brief: initial condition at t = 0 s is Tank_A level 0.80 m, Tank_B level 0.00 m, Connecting valve commanded closed. The valve closed interval starts at 0 s and ends at 5 s. At absolute simulation time t = 5 s, the Connecting valve opens. After opening, flow begins from Tank_A into Tank_B, so Tank_A level falls and Tank_B level rises. The system relaxes toward zero level difference and a shared equilibrium level of 0.40 m in each tank. The run continues to 150 s. */
    doc /* Human-confirmed Clarify answer is authoritative: interpret the Valve_Closed_Interval to Valve_Open_Transfer transition as occurring at absolute simulation time t = 5 s in downstream execution. Native elapsed-time syntax was not established in the provided parser examples, so this absolute-time execution requirement is recorded here for downstream realization. */
    doc /* Guard interpretation note: the transition conditions written here preserve the named phases and command actions, but the actual triggering time for opening is the authoritative absolute simulation time t = 5 s from the human-confirmed answer, not merely any evaluation of stored parameter values. */
  }
}

part Two_Tanks_One_Above_The_Other_Gravity_Flow_To_Equilibrium : Two_Tank_System;

}