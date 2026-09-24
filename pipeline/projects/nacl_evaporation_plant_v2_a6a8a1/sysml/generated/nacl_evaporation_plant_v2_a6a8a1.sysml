package NaCl_Evaporation_Batch_Plant {
  part def Vessel {
    attribute area_m2 : ScalarValues::Real;
    attribute height_m : ScalarValues::Real;
    attribute max_level_m : ScalarValues::Real;
    attribute port_level_note_m : ScalarValues::Real;
    attribute base_elevation_m : ScalarValues::Real;
  }

  part def Valve {
    attribute fail_closed : ScalarValues::Boolean = true;
    attribute open_cmd : ScalarValues::Boolean = false;
    attribute nominal_opening_time_s : ScalarValues::Real = 0.7;
    attribute nominal_closing_time_s : ScalarValues::Real = 0.5;
    doc /* Automated process valve family datasheet: closed leakage <0.02% Kv; permitted medium temperature range 0-120 degC. */
  }

  part def Pump {
    attribute cmd_on : ScalarValues::Boolean = false;
    attribute nominal_mass_flow_kg_per_s : ScalarValues::Real;
    attribute nominal_differential_pressure_bar : ScalarValues::Real;
    attribute minimum_source_level_permissive_m : ScalarValues::Real = 0.02;
    attribute low_discharge_pressure_alarm_threshold_bar : ScalarValues::Real = 0.8;
  }

  part def SensorBundle {
    attribute LIS_301_m : ScalarValues::Real;
    attribute QI_302_kg_per_kg : ScalarValues::Real;
    attribute LIS_501_m : ScalarValues::Real;
    attribute QIS_502_kg_per_kg : ScalarValues::Real;
    attribute TIS_602_degC : ScalarValues::Real;
    attribute TIS_702_degC : ScalarValues::Real;
    attribute FIS_801_kg_per_s : ScalarValues::Real;
    attribute LIS_601_m : ScalarValues::Real;
    attribute LIS_701_m : ScalarValues::Real;
    attribute PIS_901_bar : ScalarValues::Real;
    attribute PIS_1001_bar : ScalarValues::Real;
    attribute TI_503_degC : ScalarValues::Real;
  }

  part def ActuatorBundle {
    attribute V1_open : ScalarValues::Boolean = false;
    attribute V3_open : ScalarValues::Boolean = false;
    attribute V5_open : ScalarValues::Boolean = false;
    attribute V6_open : ScalarValues::Boolean = false;
    attribute V8_open : ScalarValues::Boolean = false;
    attribute V9_open : ScalarValues::Boolean = false;
    attribute V11_open : ScalarValues::Boolean = false;
    attribute V12_open : ScalarValues::Boolean = false;
    attribute V15_open : ScalarValues::Boolean = false;
    attribute V18_open : ScalarValues::Boolean = false;
    attribute V20_open : ScalarValues::Boolean = false;
    attribute V22_open : ScalarValues::Boolean = false;
    attribute V23_open : ScalarValues::Boolean = false;
    attribute V24_open : ScalarValues::Boolean = false;
    attribute V25_open : ScalarValues::Boolean = false;
    attribute P1_on : ScalarValues::Boolean = false;
    attribute P2_on : ScalarValues::Boolean = false;
    attribute T5_Heater : ScalarValues::Boolean = false;
    attribute B6_cooler_on : ScalarValues::Boolean = false;
    attribute B7_cooler_on : ScalarValues::Boolean = false;
  }

  part def CentralController {
    attribute startEnable : ScalarValues::Boolean = false;
    attribute B3_available : ScalarValues::Boolean = true;
    attribute elapsed_time_s : ScalarValues::Real;
    attribute branch_A_complete : ScalarValues::Boolean = false;
    attribute branch_B_complete : ScalarValues::Boolean = false;
    attribute controller_state : ScalarValues::Integer;
    attribute region : ScalarValues::Integer;
    part sensors : SensorBundle;
    part actuators : ActuatorBundle;

    state MainSequence {
      entry; then Initial;
      state Initial;
      state Step1_Charge_B1_to_B3;
      state Step2_Charge_B2_to_B3;
      state Step3_Transfer_B3_to_B4;
      state Step4_Wait_B5_Idle;
      state Step5_Transfer_B4_to_B5;
      state Step6_Evaporate_B5;
      state JoinWait;

      transition Initial_to_Step1
        first Initial
        if startEnable and B3_available
        then Step1_Charge_B1_to_B3;

      transition Step1_to_Step2
        first Step1_Charge_B1_to_B3
        if sensors.LIS_301_m >= 0.13
        do action { assign actuators.V8_open := false; assign actuators.V9_open := true; }
        then Step2_Charge_B2_to_B3;

      transition Step2_to_Step3
        first Step2_Charge_B2_to_B3
        if sensors.QI_302_kg_per_kg >= 0.080
        do action { assign actuators.V9_open := false; assign actuators.V11_open := true; }
        then Step3_Transfer_B3_to_B4;

      transition Step3_to_Step4
        first Step3_Transfer_B3_to_B4
        if sensors.LIS_301_m < 0.01
        do assign actuators.V11_open := false
        then Step4_Wait_B5_Idle;

      transition Step4_to_Step5
        first Step4_Wait_B5_Idle
        if sensors.LIS_501_m < 0.01 and not actuators.V15_open
        do assign actuators.V12_open := true
        then Step5_Transfer_B4_to_B5;

      transition Step5_to_Step6
        first Step5_Transfer_B4_to_B5
        if sensors.LIS_501_m >= 0.18
        do action { assign actuators.V12_open := false; assign actuators.T5_Heater := true; }
        then Step6_Evaporate_B5;

      transition Step6_to_JoinWait
        first Step6_Evaporate_B5
        if sensors.QIS_502_kg_per_kg >= 0.180
        do assign actuators.T5_Heater := false
        then JoinWait;

      transition JoinWait_to_Initial
        first JoinWait
        if branch_A_complete and branch_B_complete and elapsed_time_s > 2500
        then Initial;

      doc /* Initial condition: all automated valves closed; P1, P2, B5 heater, B6 cooler, and B7 cooler off. Step6 heater permissives are modeled in BranchInterlocks. Human-confirmed: elapsed_time_s is controller-readable and mapped to time_s for the JoinWait restart guard. */
    }

    state BranchA_Condensate {
      entry; then A_Idle;
      state A_Idle;
      state Step12_Cool_B6;
      state Step13_Return_B6_to_B1;
      state A_Complete;

      transition A_Idle_to_Step12
        first A_Idle
        if sensors.QIS_502_kg_per_kg >= 0.180
        do assign actuators.B6_cooler_on := true
        then Step12_Cool_B6;

      transition Step12_to_Step13
        first Step12_Cool_B6
        if sensors.TIS_602_degC <= 20
        do action { assign actuators.B6_cooler_on := false; assign actuators.V20_open := true; assign actuators.V24_open := true; assign actuators.V25_open := true; assign actuators.V1_open := true; assign actuators.V3_open := true; assign actuators.P2_on := true; }
        then Step13_Return_B6_to_B1;

      transition Step13_to_A_Complete
        first Step13_Return_B6_to_B1
        if sensors.LIS_601_m <= 0.02
        do action { assign actuators.P2_on := false; assign actuators.V20_open := false; assign actuators.V24_open := false; assign actuators.V25_open := false; assign actuators.V1_open := false; assign actuators.V3_open := false; assign branch_A_complete := true; }
        then A_Complete;

      doc /* Branch A uses approved CR-017 destination B6 to B1 via P2. The exact manifold path beyond the approved valve group is not fully readable in the notes. Executable implementation uses observed commands V20, V24, V25, V1, and V3 when P2 runs, per human-confirmed clarification. Step13 completion criterion is modeled from the stated B6 return branch completion using the pump source-level permissive threshold because no separate branch-complete sensor is defined in the notes. */
    }

    state BranchB_Concentrate {
      entry; then B_Idle;
      state B_Idle;
      state Step7_Wait_Branch_B_Ready;
      state Step8_Transfer_B5_to_B7;
      state Step9_Cool_B7;
      state Step10_11_Return_B7_to_B2;
      state B_Complete;

      transition B_Idle_to_Step7
        first B_Idle
        if sensors.QIS_502_kg_per_kg >= 0.180
        then Step7_Wait_Branch_B_Ready;

      transition Step7_to_Step8
        first Step7_Wait_Branch_B_Ready
        if sensors.LIS_701_m < 0.01
        do assign actuators.V15_open := true
        then Step8_Transfer_B5_to_B7;

      transition Step8_to_Step9
        first Step8_Transfer_B5_to_B7
        if sensors.LIS_501_m < 0.01
        do action { assign actuators.V15_open := false; assign actuators.B7_cooler_on := true; }
        then Step9_Cool_B7;

      transition Step9_to_Step10_11
        first Step9_Cool_B7
        if sensors.TIS_702_degC <= 25
        do action { assign actuators.B7_cooler_on := false; assign actuators.V18_open := true; assign actuators.V23_open := true; assign actuators.V22_open := true; assign actuators.V5_open := true; assign actuators.V6_open := true; assign actuators.P1_on := true; }
        then Step10_11_Return_B7_to_B2;

      transition Step10_11_to_B_Complete
        first Step10_11_Return_B7_to_B2
        if sensors.LIS_701_m <= 0.02
        do action { assign actuators.P1_on := false; assign actuators.V18_open := false; assign actuators.V23_open := false; assign actuators.V22_open := false; assign actuators.V5_open := false; assign actuators.V6_open := false; assign branch_B_complete := true; }
        then B_Complete;

      doc /* Human-confirmed Step7 role: explicit no-actuator wait state preceding Step8 with completion condition LIS-701 <0.01 m. Branch B uses approved CR-017 destination B7 to B2 via P1. Executable implementation uses observed commands V18, V23, V22, V5, and V6 when P1 runs, per human-confirmed clarification. */
    }

    state BranchInterlocks {
      entry; then InterlocksActive;
      state InterlocksActive;
      state Stopped;

      transition HeaterInhibitLowLevel
        first InterlocksActive
        if actuators.T5_Heater and sensors.LIS_501_m < 0.05
        do assign actuators.T5_Heater := false
        then InterlocksActive;

      transition HeaterInhibitLowFlow
        first InterlocksActive
        if actuators.T5_Heater and sensors.FIS_801_kg_per_s < 0.10
        do assign actuators.T5_Heater := false
        then InterlocksActive;

      transition Pump1InhibitLowSource
        first InterlocksActive
        if actuators.P1_on and not (sensors.LIS_701_m > 0.02)
        do assign actuators.P1_on := false
        then InterlocksActive;

      transition Pump2InhibitLowSource
        first InterlocksActive
        if actuators.P2_on and not (sensors.LIS_601_m > 0.02)
        do assign actuators.P2_on := false
        then InterlocksActive;

      doc /* This machine carries continuously enforced permissive behavior from the notes: heater only above LIS-501 >= 0.05 m and with FIS-801 >= 0.10 kg/s; P1 only with LIS-701 > 0.02 m; P2 only with LIS-601 > 0.02 m. Low discharge pressure alarm thresholds PIS-901 <0.8 bar and PIS-1001 <0.8 bar are evidenced alarm relations, but no controller trip action is stated in the notes. STOP, resume, shutdown, and reset commands are not defined beyond the cycle reset to Initial after both branches complete and elapsed_time_s >2500. */
    }
  }

  part BatchPlant {
    attribute simulation_start_time_s : ScalarValues::Real = 0;
    attribute simulation_stop_time_s : ScalarValues::Real = 3000;
    attribute reporting_interval_count : ScalarValues::Integer = 600;
    attribute required_logging_interval_s : ScalarValues::Real = 5;
    attribute time_s : ScalarValues::Real;
    attribute baseline_integration_medium : ScalarValues::String = "Modelica.Media.Water.StandardWater";
    attribute intended_physical_medium : ScalarValues::String = "WaterNaCl";
    doc /* Baseline integration-test medium only: StandardWater. Intended physical plant medium: WaterNaCl with composition-dependent rho(T,p,w), h(T,p,w), cp(T,w), p_sat(T,w), eta(T,w). WaterNaCl hierarchy intended in notes: PartialMedium -> PartialMixtureMedium -> PartialMixtureTwoPhaseMedium -> WaterNaCl. B5 and K1 remain distinct physical components even if a combined simulation abstraction is used later. */

    part B1 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.07;
      attribute height_m : ScalarValues::Real = 0.6;
      attribute max_level_m : ScalarValues::Real = 0.5;
      attribute port_level_note_m : ScalarValues::Real = 0.12;
      attribute base_elevation_m : ScalarValues::Real = 4.8;
      doc /* B1 Charging tank; initial NaCl mass fraction 0.000. */
    }

    part B2 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.07;
      attribute height_m : ScalarValues::Real = 0.6;
      attribute max_level_m : ScalarValues::Real = 0.5;
      attribute port_level_note_m : ScalarValues::Real = 0.12;
      attribute base_elevation_m : ScalarValues::Real = 4.8;
      doc /* B2 Charging tank; initial NaCl mass fraction 0.250. */
    }

    part B3 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.05;
      attribute height_m : ScalarValues::Real = 0.45;
      attribute max_level_m : ScalarValues::Real = 0.38;
      attribute port_level_note_m : ScalarValues::Real = 0.1;
      attribute base_elevation_m : ScalarValues::Real = 3.5;
      doc /* B3 Mixing tank; water prefill level 0.13 m current; target NaCl mass fraction after mixing 0.080 kg/kg current; nearly-empty threshold 0.01 m current. */
    }

    part B4 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.055;
      attribute height_m : ScalarValues::Real = 0.45;
      attribute max_level_m : ScalarValues::Real = 0.4;
      attribute port_level_note_m : ScalarValues::Real = 0.1;
      attribute base_elevation_m : ScalarValues::Real = 2.6;
    }

    part B5 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.06;
      attribute height_m : ScalarValues::Real = 0.45;
      attribute max_level_m : ScalarValues::Real = 0.4;
      attribute port_level_note_m : ScalarValues::Real = 0.12;
      attribute base_elevation_m : ScalarValues::Real = 1.5;
      doc /* B5 Evaporator vessel; idle threshold 0.01 m current; batch fill level 0.18 m current; target NaCl mass fraction after evaporation 0.180 kg/kg current; heater duty 20000 W current/approved; heater inhibit level 0.05 m approved. */
    }

    part K1 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.0;
      attribute height_m : ScalarValues::Real = 0.0;
      attribute max_level_m : ScalarValues::Real = 0.0;
      attribute port_level_note_m : ScalarValues::Real = 0.0;
      attribute base_elevation_m : ScalarValues::Real = 2.8;
      doc /* K1 Condenser. Geometry values other than base elevation are not supplied in the notes; zero placeholders are used only because Vessel requires these attributes. K1 remains a distinct physical component. */
    }

    part B6 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.05;
      attribute height_m : ScalarValues::Real = 0.4;
      attribute max_level_m : ScalarValues::Real = 0.35;
      attribute port_level_note_m : ScalarValues::Real = 0.1;
      attribute base_elevation_m : ScalarValues::Real = 1.5;
      doc /* B6 Cooling tank; cooling complete temperature 20 degC current; nominal cooling duty -6500 W current. */
    }

    part B7 : Vessel {
      attribute area_m2 : ScalarValues::Real = 0.05;
      attribute height_m : ScalarValues::Real = 0.4;
      attribute max_level_m : ScalarValues::Real = 0.35;
      attribute port_level_note_m : ScalarValues::Real = 0.1;
      attribute base_elevation_m : ScalarValues::Real = 0.7;
      doc /* B7 Cooling tank; cooling complete temperature 25 degC current/approved. Archived 20 degC value is superseded. Nominal cooling duty -4500 W current. */
    }

    part V1 : Valve;
    part V3 : Valve;
    part V5 : Valve;
    part V6 : Valve;
    part V8 : Valve;
    part V9 : Valve;
    part V11 : Valve;
    part V12 : Valve;
    part V15 : Valve;
    part V18 : Valve;
    part V20 : Valve;
    part V22 : Valve;
    part V23 : Valve;
    part V24 : Valve;
    part V25 : Valve;

    part P1 : Pump {
      attribute nominal_mass_flow_kg_per_s : ScalarValues::Real = 0.30;
      attribute nominal_differential_pressure_bar : ScalarValues::Real = 1.8;
    }

    part P2 : Pump {
      attribute nominal_mass_flow_kg_per_s : ScalarValues::Real = 0.30;
      attribute nominal_differential_pressure_bar : ScalarValues::Real = 1.8;
    }

    part M_301_agitator {
      doc /* M-301 agitator. Present in canonical equipment list. No explicit automated command, topology connection, or sequence logic is provided in the notes. */
    }

    part central_controller : CentralController {
      attribute elapsed_time_s : ScalarValues::Real = 0;
    }

    part Junction_B1_to_V8 {
      doc /* Small junction volume insertion is required wherever multiple pressure-drop-only valve/pipe elements can be isolated simultaneously. This junction represents the B1 branch segment. */
    }
    part Junction_V8_to_B3;
    part Junction_B2_to_V9;
    part Junction_V9_to_B3;
    part Junction_B3_to_V11;
    part Junction_V11_to_B4;
    part Junction_B4_to_V12;
    part Junction_V12_to_B5;
    part Junction_B5_to_K1;
    part Junction_K1_to_B6;
    part Junction_B5_to_V15;
    part Junction_V15_to_B7;
    part Junction_B6_to_P2;
    part Junction_P2_to_B1_Return_Group {
      doc /* Cross-connected bottom return headers/manifolds exist, but exact full manifold path is not completely readable in the notes. This junction represents only the approved B1 return destination side. */
    }
    part Junction_B7_to_P1;
    part Junction_P1_to_B2_Return_Group {
      doc /* Cross-connected bottom return headers/manifolds exist, but exact full manifold path is not completely readable in the notes. This junction represents only the approved B2 return destination side. */
    }

    connect B1 to Junction_B1_to_V8;
    connect Junction_B1_to_V8 to V8;
    connect V8 to Junction_V8_to_B3;
    connect Junction_V8_to_B3 to B3;

    connect B2 to Junction_B2_to_V9;
    connect Junction_B2_to_V9 to V9;
    connect V9 to Junction_V9_to_B3;
    connect Junction_V9_to_B3 to B3;

    connect B3 to Junction_B3_to_V11;
    connect Junction_B3_to_V11 to V11;
    connect V11 to Junction_V11_to_B4;
    connect Junction_V11_to_B4 to B4;

    connect B4 to Junction_B4_to_V12;
    connect Junction_B4_to_V12 to V12;
    connect V12 to Junction_V12_to_B5;
    connect Junction_V12_to_B5 to B5;

    connect B5 to Junction_B5_to_K1;
    connect Junction_B5_to_K1 to K1;
    connect K1 to Junction_K1_to_B6;
    connect Junction_K1_to_B6 to B6;

    connect B5 to Junction_B5_to_V15;
    connect Junction_B5_to_V15 to V15;
    connect V15 to Junction_V15_to_B7;
    connect Junction_V15_to_B7 to B7;

    connect B6 to Junction_B6_to_P2;
    connect Junction_B6_to_P2 to P2;
    connect P2 to Junction_P2_to_B1_Return_Group;
    connect Junction_P2_to_B1_Return_Group to V20;
    connect V20 to V24;
    connect V24 to V25;
    connect V25 to V1;
    connect V1 to V3;
    connect V3 to B1;

    connect B7 to Junction_B7_to_P1;
    connect Junction_B7_to_P1 to P1;
    connect P1 to Junction_P1_to_B2_Return_Group;
    connect Junction_P1_to_B2_Return_Group to V18;
    connect V18 to V23;
    connect V23 to V22;
    connect V22 to V5;
    connect V5 to V6;
    connect V6 to B2;

    attribute B3_level_m : ScalarValues::Real;
    attribute B4_level_m : ScalarValues::Real;
    attribute B5_level_m : ScalarValues::Real;
    attribute B6_level_m : ScalarValues::Real;
    attribute B7_level_m : ScalarValues::Real;
    attribute B3_X_NaCl_kg_per_kg : ScalarValues::Real;
    attribute B5_X_NaCl_kg_per_kg : ScalarValues::Real;
    attribute B5_T_degC : ScalarValues::Real;
    attribute B6_T_degC : ScalarValues::Real;
    attribute B7_T_degC : ScalarValues::Real;
    attribute FIS801_flow_kg_per_s : ScalarValues::Real;
    attribute P1_cmd : ScalarValues::Boolean;
    attribute P2_cmd : ScalarValues::Boolean;
    attribute B5_heater_cmd : ScalarValues::Boolean;
    attribute B6_cooler_cmd : ScalarValues::Boolean;
    attribute B7_cooler_cmd : ScalarValues::Boolean;

    requirement Automated_Valves_Fail_Closed {
      doc /* All automated process valves V1, V3, V5, V6, V8, V9, V11, V12, V15, V18, V20, V22, V23, V24, and V25 fail closed on loss of actuator power. Source: valve and pump actuation data. */
    }

    requirement Join_Waits_For_Both_Branches_And_Time {
      doc /* The controller shall not reset the cycle from JoinWait to Initial until branch_A_complete and branch_B_complete are both true and elapsed_time_s > 2500. Source: plant purpose, resolved sequence, and human-confirmed elapsed time guard. */
    }

    requirement Heater_Permissive_Rule {
      doc /* The B5 heater shall be inhibited unless LIS-501 >= 0.05 m and FIS-801 >= 0.10 kg/s. Source: Step6 heater permissives and REQ-SAF-001/005 narrative behavior. */
    }

    requirement Pump_Source_Level_Permissive_Rule {
      doc /* P1 shall be inhibited unless LIS-701 > 0.02 m, and P2 shall be inhibited unless LIS-601 > 0.02 m. Source: pump actuation relationships. */
    }

    requirement Baseline_Logging_Contract {
      doc /* BAT-09 requires logging state/region, all tank levels, QI-302, QIS-502, TI-503, TIS-602, TIS-702, FIS-801, P1/P2, heater/cooler commands, and all 15 automated valve commands at 5 s or faster over the resolved 3000 s run. */
    }

    doc /* Physical relationships evidenced in the notes for later stages: medium pressure equals p_ambient; vessel volume V = area*level + V0; mass m = V*medium.d; species mass vector mXi = m*medium.Xi; internal energy U = m*medium.u; total mass balance der(m) = sum(topPorts.m_flow) + sum(ports.m_flow); internal-energy balance der(U) = sum(H_flow) - p_ambient*der(V). Heater command relation: HeatB5.Q_flow = if controller.actuators.T5_Heater then 20000 else 0. Condenser-side note: if Q_up > heatPort.Q_flow then m_con = 0; else m_con = -(heatPort.Q_flow - Q_up)/(hv - hl + Xi[1]*(cp*dT_dX + dhl_dX)). Units for the latter relation are not fully established in the notes and must be verified later before implementation. Static head/gravity pressure drop shall be included in non-horizontal pipes based on relative elevation. Tank ports that can cross liquid level should use regularized asymmetric loss-factor approach with hysteresis. */
  }
}