package NaCl_Evaporation_Plant_Batch_Process {

  part def Vessel {
    attribute cross_section_area_m2 : ScalarValues::Real;
    attribute height_m : ScalarValues::Real;
    attribute max_level_m : ScalarValues::Real;
    attribute port_elevation_m : ScalarValues::Real;
    attribute initial_level_m : ScalarValues::Real;
    attribute initial_w_NaCl_kg_per_kg : ScalarValues::Real;
    attribute level_m : ScalarValues::Real;
    attribute temperature_C : ScalarValues::Real;
    attribute w_NaCl_kg_per_kg : ScalarValues::Real;
    attribute z_base_m : ScalarValues::Real;
    doc /* WaterNaCl custom water_NaCl medium is the required final composition_based medium. Tank and medium balance evidence: V = area*level + V0; m = V*medium.d; mXi = m*medium.Xi; U = m*medium.u; der(m) = sum(topPorts.m_flow) + sum(ports.m_flow); der(U) = sum(H_flow) - p_ambient*der(V). Omission of p_ambient*der(V) is permitted for an incompressible formulation but is not established here. */
  }

  part def AutomatedValve {
    attribute open_cmd : ScalarValues::Boolean;
    attribute fail_closed_on_loss_of_power : ScalarValues::Boolean = true;
    attribute nominal_opening_time_s : ScalarValues::Real = 0.7;
    attribute nominal_closing_time_s : ScalarValues::Real = 0.5;
  }

  part def Pump {
    attribute cmd_on : ScalarValues::Boolean;
    attribute nominal_mass_flow_kg_s : ScalarValues::Real;
    attribute nominal_differential_pressure_bar : ScalarValues::Real;
    attribute low_discharge_pressure_alarm_bar_threshold_bar : ScalarValues::Real = 0.8;
    attribute z_base_m : ScalarValues::Real;
  }

  part def Cooler {
    attribute cmd_on : ScalarValues::Boolean;
    attribute nominal_duty_W : ScalarValues::Real;
    doc /* Cooling implementation beyond on_off command and nominal duty is not specified in the notes. */
  }

  part def Heater {
    attribute cmd_on : ScalarValues::Boolean;
    attribute duty_W : ScalarValues::Real;
    doc /* Explicit mapping in notes: HeatB5.Q_flow = if controller.actuators.T5_Heater then 20000 else 0. */
  }

  part def SensorLevel {
    attribute measured_value_m : ScalarValues::Real;
    attribute range_min_m : ScalarValues::Real;
    attribute range_max_m : ScalarValues::Real;
  }

  part def SensorComposition {
    attribute measured_value_kg_per_kg : ScalarValues::Real;
    attribute range_min_kg_per_kg : ScalarValues::Real;
    attribute range_max_kg_per_kg : ScalarValues::Real;
  }

  part def SensorTemperature {
    attribute measured_value_C : ScalarValues::Real;
    attribute range_min_C : ScalarValues::Real;
    attribute range_max_C : ScalarValues::Real;
  }

  part def SensorFlow {
    attribute measured_value_kg_s : ScalarValues::Real;
    attribute range_min_kg_s : ScalarValues::Real;
    attribute range_max_kg_s : ScalarValues::Real;
  }

  part def AlarmSignal {
    attribute measured_value_bar : ScalarValues::Real;
  }

  part def PassiveEquipment {
    attribute z_base_m : ScalarValues::Real;
  }

  requirement def SafetyRequirement;

  part def Plant {
    attribute medium_name : ScalarValues::String = "WaterNaCl";
    attribute ambient_pressure_Pa : ScalarValues::Real = 101325.0;
    attribute ambient_temperature_K : ScalarValues::Real = 293.15;
    attribute simulation_start_time_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_time_s : ScalarValues::Real = 3000.0;
    attribute logging_sample_interval_s_max : ScalarValues::Real = 5.0;
    attribute startEnable : ScalarValues::Boolean;
    attribute B3_available : ScalarValues::Boolean;
    attribute time_s : ScalarValues::Real;
    attribute controller_state : ScalarValues::String;
    attribute region : ScalarValues::String;
    attribute B3_level_m : ScalarValues::Real;
    attribute B4_level_m : ScalarValues::Real;
    attribute B5_level_m : ScalarValues::Real;
    attribute B6_level_m : ScalarValues::Real;
    attribute B7_level_m : ScalarValues::Real;
    attribute B3_w_NaCl : ScalarValues::Real;
    attribute B5_w_NaCl : ScalarValues::Real;
    attribute B5_temp_C : ScalarValues::Real;
    attribute B6_temp_C : ScalarValues::Real;
    attribute B7_temp_C : ScalarValues::Real;
    attribute FIS801_kg_s : ScalarValues::Real;
    attribute P1_cmd : ScalarValues::Real;
    attribute P2_cmd : ScalarValues::Real;
    attribute B5_heater_cmd : ScalarValues::Real;
    attribute B6_cooler_cmd : ScalarValues::Real;
    attribute B7_cooler_cmd : ScalarValues::Real;
    attribute V1_open : ScalarValues::Real;
    attribute V3_open : ScalarValues::Real;
    attribute V5_open : ScalarValues::Real;
    attribute V6_open : ScalarValues::Real;
    attribute V8_open : ScalarValues::Real;
    attribute V9_open : ScalarValues::Real;
    attribute V11_open : ScalarValues::Real;
    attribute V12_open : ScalarValues::Real;
    attribute V15_open : ScalarValues::Real;
    attribute V18_open : ScalarValues::Real;
    attribute V20_open : ScalarValues::Real;
    attribute V22_open : ScalarValues::Real;
    attribute V23_open : ScalarValues::Real;
    attribute V24_open : ScalarValues::Real;
    attribute V25_open : ScalarValues::Real;

    part B1 : Vessel {
      attribute cross_section_area_m2 = 0.07;
      attribute height_m = 0.6;
      attribute max_level_m = 0.5;
      attribute port_elevation_m = 0.12;
      attribute initial_level_m = 0.5;
      attribute initial_w_NaCl_kg_per_kg = 0.0;
      attribute z_base_m = 4.8;
      doc /* B1 Charging tank. */
    }

    part B2 : Vessel {
      attribute cross_section_area_m2 = 0.07;
      attribute height_m = 0.6;
      attribute max_level_m = 0.5;
      attribute port_elevation_m = 0.12;
      attribute initial_level_m = 0.35;
      attribute initial_w_NaCl_kg_per_kg = 0.25;
      attribute z_base_m = 4.8;
      doc /* B2 Charging tank. */
    }

    part B3 : Vessel {
      attribute cross_section_area_m2 = 0.05;
      attribute height_m = 0.45;
      attribute max_level_m = 0.38;
      attribute port_elevation_m = 0.1;
      attribute initial_level_m = 0.01;
      attribute initial_w_NaCl_kg_per_kg = 0.0;
      attribute z_base_m = 3.5;
      doc /* B3 Mixing tank; water prefill level target 0.13 m; NaCl target after mixing 0.08 kg/kg; nearly_empty threshold 0.01 m. M_301 agitator exists in equipment register, but no required command behavior is established here. */
    }

    part B4 : Vessel {
      attribute cross_section_area_m2 = 0.055;
      attribute height_m = 0.45;
      attribute max_level_m = 0.4;
      attribute port_elevation_m = 0.1;
      attribute initial_level_m = 0.01;
      attribute initial_w_NaCl_kg_per_kg = 0.0;
      attribute z_base_m = 2.6;
      doc /* B4 Buffer tank. */
    }

    part B5 : Vessel {
      attribute cross_section_area_m2 = 0.06;
      attribute height_m = 0.45;
      attribute max_level_m = 0.4;
      attribute port_elevation_m = 0.12;
      attribute initial_level_m = 0.01;
      attribute initial_w_NaCl_kg_per_kg = 0.0;
      attribute z_base_m = 1.5;
      doc /* B5 Evaporator vessel; idle threshold 0.01 m; batch fill level 0.18 m; NaCl target after evaporation 0.18 kg/kg. */
    }

    part K1 : PassiveEquipment {
      attribute z_base_m = 2.8;
      doc /* K1 condenser remains physically identifiable in the architecture even if a later simulation combines evaporator and condenser equations in one component. Minimum cooling_water flow for heater permissive is 0.1 kg/s current. */
    }

    part B6 : Vessel {
      attribute cross_section_area_m2 = 0.05;
      attribute height_m = 0.4;
      attribute max_level_m = 0.35;
      attribute port_elevation_m = 0.1;
      attribute initial_level_m = 0.01;
      attribute initial_w_NaCl_kg_per_kg = 0.0;
      attribute z_base_m = 1.5;
      doc /* B6 Condensate cooling tank; cooling complete temperature 20 degC; nominal cooling duty _6500 W. */
    }

    part B7 : Vessel {
      attribute cross_section_area_m2 = 0.05;
      attribute height_m = 0.4;
      attribute max_level_m = 0.35;
      attribute port_elevation_m = 0.1;
      attribute initial_level_m = 0.01;
      attribute initial_w_NaCl_kg_per_kg = 0.0;
      attribute z_base_m = 0.7;
      doc /* B7 Concentrate cooling tank; cooling complete temperature 25 degC current approved value; earlier 20 degC value superseded; nominal cooling duty _4500 W. */
    }

    part V1 : AutomatedValve;
    part V3 : AutomatedValve;
    part V5 : AutomatedValve;
    part V6 : AutomatedValve;
    part V8 : AutomatedValve;
    part V9 : AutomatedValve;
    part V11 : AutomatedValve;
    part V12 : AutomatedValve;
    part V15 : AutomatedValve;
    part V18 : AutomatedValve;
    part V20 : AutomatedValve;
    part V22 : AutomatedValve;
    part V23 : AutomatedValve;
    part V24 : AutomatedValve;
    part V25 : AutomatedValve;

    part P1 : Pump {
      attribute nominal_mass_flow_kg_s = 0.30;
      attribute nominal_differential_pressure_bar = 1.8;
      attribute z_base_m = 0.0;
      doc /* P1 Return pump; low discharge pressure alarm if PIS_901 < 0.8 bar while running; source permissive requires LIS_701 > 0.02 m and inhibit when LIS_701 <= 0.02 m. */
    }

    part P2 : Pump {
      attribute nominal_mass_flow_kg_s = 0.30;
      attribute nominal_differential_pressure_bar = 1.8;
      attribute z_base_m = 0.0;
      doc /* P2 Return pump; low discharge pressure alarm if PIS_1001 < 0.8 bar while running; source permissive requires LIS_601 > 0.02 m and inhibit when LIS_601 <= 0.02 m. */
    }

    part HeatB5 : Heater {
      attribute duty_W = 20000.0;
    }

    part B6_Cooler : Cooler {
      attribute nominal_duty_W = -6500.0;
    }

    part B7_Cooler : Cooler {
      attribute nominal_duty_W = -4500.0;
    }

    part LIS_301 : SensorLevel {
      attribute range_min_m = 0.0;
      attribute range_max_m = 0.45;
    }

    part QI_302 : SensorComposition {
      attribute range_min_kg_per_kg = 0.0;
      attribute range_max_kg_per_kg = 0.30;
    }

    part LIS_501 : SensorLevel {
      attribute range_min_m = 0.0;
      attribute range_max_m = 0.45;
    }

    part QIS_502 : SensorComposition {
      attribute range_min_kg_per_kg = 0.0;
      attribute range_max_kg_per_kg = 0.30;
    }

    part TIS_602 : SensorTemperature {
      attribute range_min_C = 0.0;
      attribute range_max_C = 120.0;
    }

    part TIS_702 : SensorTemperature {
      attribute range_min_C = 0.0;
      attribute range_max_C = 120.0;
    }

    part FIS_801 : SensorFlow {
      attribute range_min_kg_s = 0.0;
      attribute range_max_kg_s = 0.50;
      doc /* Condenser cooling_water flow proof signal. BAT_09 initial condition: initially >= 0.10 kg/s. */
    }

    part LIS_701 : SensorLevel {
      attribute range_min_m = 0.0;
      attribute range_max_m = 0.45;
    }

    part LIS_601 : SensorLevel {
      attribute range_min_m = 0.0;
      attribute range_max_m = 0.45;
    }

    part PIS_901 : AlarmSignal;
    part PIS_1001 : AlarmSignal;

    part Controller : PassiveEquipment {
      attribute z_base_m = 0.0;
      attribute scan_is_discrete : ScalarValues::Boolean = true;
      doc /* Central controller, also named central controller or Controller. Implemented as a sequential StateGraph with a parallel split after evaporation and a join before cycle reset per 06_06_design_review_minutes.txt and 05_04_control_sequence_design.txt. Manual valves including V17 and V29 are excluded from the StateGraph actuator bundle unless specifically stated in the ICD; no such ICD note is provided here. The executable sequence here follows the requirement specification and BAT_09 interpretation confirmed by human clarification: actuate each device during its stage and use the stated threshold as the stage exit condition. */

      state OperatingCycle {
        entry; then Initial;

        state Initial;
        state Step1_Charge_Water;
        state Step2_Charge_Brine_Mix;
        state Step3_Buffer_Transfer;
        state Step4_B5_Idle_Check;
        state Step5_Evaporator_Charge;
        state Step6_Evaporation;
        state Parallel_A_B;
        state Branch_A_Cool_B6;
        state Branch_A_Return_B6_to_B1;
        state Branch_B_B7_Availability_Check;
        state Step8_Transfer_B5_to_B7;
        state Step9_Cool_B7;
        state Step10_11_Return_B7_to_B2;
        state JoinWait;

        transition Initial_to_Step1_Charge_Water
          first Initial
          if NaCl_Evaporation_Plant.startEnable and NaCl_Evaporation_Plant.B3_available
          do action {
            assign NaCl_Evaporation_Plant.V1.open_cmd := false;
            assign NaCl_Evaporation_Plant.V3.open_cmd := false;
            assign NaCl_Evaporation_Plant.V5.open_cmd := false;
            assign NaCl_Evaporation_Plant.V6.open_cmd := false;
            assign NaCl_Evaporation_Plant.V8.open_cmd := false;
            assign NaCl_Evaporation_Plant.V9.open_cmd := false;
            assign NaCl_Evaporation_Plant.V11.open_cmd := false;
            assign NaCl_Evaporation_Plant.V12.open_cmd := false;
            assign NaCl_Evaporation_Plant.V15.open_cmd := false;
            assign NaCl_Evaporation_Plant.V18.open_cmd := false;
            assign NaCl_Evaporation_Plant.V20.open_cmd := false;
            assign NaCl_Evaporation_Plant.V22.open_cmd := false;
            assign NaCl_Evaporation_Plant.V23.open_cmd := false;
            assign NaCl_Evaporation_Plant.V24.open_cmd := false;
            assign NaCl_Evaporation_Plant.V25.open_cmd := false;
            assign NaCl_Evaporation_Plant.P1.cmd_on := false;
            assign NaCl_Evaporation_Plant.P2.cmd_on := false;
            assign NaCl_Evaporation_Plant.HeatB5.cmd_on := false;
            assign NaCl_Evaporation_Plant.B6_Cooler.cmd_on := false;
            assign NaCl_Evaporation_Plant.B7_Cooler.cmd_on := false;
            assign NaCl_Evaporation_Plant.V8.open_cmd := true;
          }
          then Step1_Charge_Water;

        transition Step1_Charge_Water_to_Step2_Charge_Brine_Mix
          first Step1_Charge_Water
          if NaCl_Evaporation_Plant.LIS_301.measured_value_m >= 0.13
          do action {
            assign NaCl_Evaporation_Plant.V8.open_cmd := false;
            assign NaCl_Evaporation_Plant.V9.open_cmd := true;
          }
          then Step2_Charge_Brine_Mix;

        transition Step2_Charge_Brine_Mix_to_Step3_Buffer_Transfer
          first Step2_Charge_Brine_Mix
          if NaCl_Evaporation_Plant.QI_302.measured_value_kg_per_kg >= 0.08
          do action {
            assign NaCl_Evaporation_Plant.V9.open_cmd := false;
            assign NaCl_Evaporation_Plant.V11.open_cmd := true;
          }
          then Step3_Buffer_Transfer;

        transition Step3_Buffer_Transfer_to_Step4_B5_Idle_Check
          first Step3_Buffer_Transfer
          if NaCl_Evaporation_Plant.LIS_301.measured_value_m < 0.01
          do assign NaCl_Evaporation_Plant.V11.open_cmd := false
          then Step4_B5_Idle_Check;

        transition Step4_B5_Idle_Check_to_Step5_Evaporator_Charge
          first Step4_B5_Idle_Check
          if (NaCl_Evaporation_Plant.LIS_501.measured_value_m < 0.01) and (NaCl_Evaporation_Plant.V15.open_cmd == false)
          do assign NaCl_Evaporation_Plant.V12.open_cmd := true
          then Step5_Evaporator_Charge;

        transition Step5_Evaporator_Charge_to_Step6_Evaporation
          first Step5_Evaporator_Charge
          if NaCl_Evaporation_Plant.LIS_501.measured_value_m >= 0.18
          do action {
            assign NaCl_Evaporation_Plant.V12.open_cmd := false;
            assign NaCl_Evaporation_Plant.HeatB5.cmd_on := true;
          }
          then Step6_Evaporation;

        transition Step6_Evaporation_to_Parallel_A_B
          first Step6_Evaporation
          if NaCl_Evaporation_Plant.QIS_502.measured_value_kg_per_kg >= 0.18
          do assign NaCl_Evaporation_Plant.HeatB5.cmd_on := false
          then Parallel_A_B;

        transition Parallel_A_B_to_Branch_A_Cool_B6
          first Parallel_A_B
          do assign NaCl_Evaporation_Plant.B6_Cooler.cmd_on := true
          then Branch_A_Cool_B6;

        transition Branch_A_Cool_B6_to_Branch_A_Return_B6_to_B1
          first Branch_A_Cool_B6
          if NaCl_Evaporation_Plant.TIS_602.measured_value_C <= 20.0
          do action {
            assign NaCl_Evaporation_Plant.B6_Cooler.cmd_on := false;
            assign NaCl_Evaporation_Plant.P2.cmd_on := true;
            assign NaCl_Evaporation_Plant.V5.open_cmd := true;
            assign NaCl_Evaporation_Plant.V6.open_cmd := true;
            assign NaCl_Evaporation_Plant.V20.open_cmd := true;
            assign NaCl_Evaporation_Plant.V24.open_cmd := true;
            assign NaCl_Evaporation_Plant.V25.open_cmd := true;
          }
          then Branch_A_Return_B6_to_B1;

        transition Branch_A_Return_B6_to_B1_to_JoinWait
          first Branch_A_Return_B6_to_B1
          if NaCl_Evaporation_Plant.LIS_601.measured_value_m <= 0.02
          do action {
            assign NaCl_Evaporation_Plant.P2.cmd_on := false;
            assign NaCl_Evaporation_Plant.V5.open_cmd := false;
            assign NaCl_Evaporation_Plant.V6.open_cmd := false;
            assign NaCl_Evaporation_Plant.V20.open_cmd := false;
            assign NaCl_Evaporation_Plant.V24.open_cmd := false;
            assign NaCl_Evaporation_Plant.V25.open_cmd := false;
          }
          then JoinWait;

        transition Parallel_A_B_to_Branch_B_B7_Availability_Check
          first Parallel_A_B
          then Branch_B_B7_Availability_Check;

        transition Branch_B_B7_Availability_Check_to_Step8_Transfer_B5_to_B7
          first Branch_B_B7_Availability_Check
          if NaCl_Evaporation_Plant.LIS_701.measured_value_m < 0.01
          do assign NaCl_Evaporation_Plant.V15.open_cmd := true
          then Step8_Transfer_B5_to_B7;

        transition Step8_Transfer_B5_to_B7_to_Step9_Cool_B7
          first Step8_Transfer_B5_to_B7
          if NaCl_Evaporation_Plant.LIS_501.measured_value_m < 0.01
          do assign NaCl_Evaporation_Plant.B7_Cooler.cmd_on := true
          then Step9_Cool_B7;

        transition Step9_Cool_B7_to_Step10_11_Return_B7_to_B2
          first Step9_Cool_B7
          if NaCl_Evaporation_Plant.TIS_702.measured_value_C <= 25.0
          do action {
            assign NaCl_Evaporation_Plant.B7_Cooler.cmd_on := false;
            assign NaCl_Evaporation_Plant.P1.cmd_on := true;
            assign NaCl_Evaporation_Plant.V1.open_cmd := true;
            assign NaCl_Evaporation_Plant.V3.open_cmd := true;
            assign NaCl_Evaporation_Plant.V18.open_cmd := true;
            assign NaCl_Evaporation_Plant.V22.open_cmd := true;
            assign NaCl_Evaporation_Plant.V23.open_cmd := true;
          }
          then Step10_11_Return_B7_to_B2;

        transition Step10_11_Return_B7_to_B2_to_JoinWait
          first Step10_11_Return_B7_to_B2
          if NaCl_Evaporation_Plant.LIS_701.measured_value_m <= 0.02
          do action {
            assign NaCl_Evaporation_Plant.P1.cmd_on := false;
            assign NaCl_Evaporation_Plant.V1.open_cmd := false;
            assign NaCl_Evaporation_Plant.V3.open_cmd := false;
            assign NaCl_Evaporation_Plant.V18.open_cmd := false;
            assign NaCl_Evaporation_Plant.V22.open_cmd := false;
            assign NaCl_Evaporation_Plant.V23.open_cmd := false;
            assign NaCl_Evaporation_Plant.V15.open_cmd := false;
          }
          then JoinWait;

        transition JoinWait_to_Initial
          first JoinWait
          if NaCl_Evaporation_Plant.time_s > 2500.0
          then Initial;
      }
    }

    connect B1 to V8;
    connect V8 to B3;
    connect B2 to V9;
    connect V9 to B3;
    connect B3 to V11;
    connect V11 to B4;
    connect B4 to V12;
    connect V12 to B5;
    connect B5 to K1;
    connect K1 to B6;
    connect B5 to V15;
    connect V15 to B7;
    connect B6 to P2;
    connect P2 to V5;
    connect V5 to V6;
    connect V6 to V20;
    connect V20 to V24;
    connect V24 to V25;
    connect V25 to B1;
    connect B7 to P1;
    connect P1 to V1;
    connect V1 to V3;
    connect V3 to V18;
    connect V18 to V22;
    connect V22 to V23;
    connect V23 to B2;

    doc /* Authoritative process interfaces: IF_PROC_01 through IF_PROC_12 and IF_RET_01 through IF_RET_04 cover the resolved process and return routing connections. Exact one_to_one mapping of each identifier to each individual connect statement is not restated in the provided understanding, so identifiers are preserved here at route_set level rather than assigned one_by_one. */
    doc /* Return routing human_confirmed and authoritative: B6 -> P2 -> B1 and B7 -> P1 -> B2. The exact corrected automated_valve memberships and mandatory simultaneous openings inside the B1 return valve group and B2 return valve group remain only partially established. Per confirmed clarification, the listed five_valve sets are preserved as candidate members pending confirmation of which set belongs to which destination. This draft uses the grouped candidate set with B6_P2_to_B1 on V5 V6 V20 V24 V25 and B7_P1_to_B2 on V1 V3 V18 V22 V23 because those sets satisfy the grouped acceptance routing evidence, but the underlying notes do not establish whether all five are mandatory simultaneously. */
    doc /* Port crossing design evidence: for ports that can cross the liquid level, default implementation uses asymmetric loss factors with regularized quadratic flow law and hysteresis around level crossing; default very large outflow loss factor above liquid level 1e5 and small inflow factor 0.01. Multiple pressure_drop_only valve or pipe elements that can be isolated simultaneously require small junction volumes. Non_horizontal pipes require gravity pressure drop based on relative elevation. */
    doc /* WaterNaCl property evidence explicitly available: rho(T,p,w), h(T,p,w), cp(T,w), p_sat(T,w), eta(T,w). Viscosity correlation evidence: eta(T,w) = exp(c1*T^3 + c2*T^2 + c3*T + c4 + c5*w + c6*w^2 + c7*w^3) with c1=_6.83241E_07, c2=0.000765676, c3=_0.297018665, c4=_0.299730079, c5=2.065267182, c6=1.546491257, c7=31.57571595. */
    doc /* Explicit signal equalities from notes: controller.sensors.LIS_301 = B3.level; controller.sensors.QI_302 = B3.medium.Xi[1]; controller.sensors.LIS_501 = B5.level; controller.sensors.QIS_502 = B5.medium.Xi[NaCl] or Xi[1] depending on notation; controller.sensors.TIS_602 = B6.medium.T; controller.sensors.TIS_702 = B7.medium.T; V9.open = controller.actuators.V9; HeatB5.Q_flow = if controller.actuators.T5_Heater then 20000 else 0. */
    doc /* Required reports: time_s, controller_state, region, B3_level_m, B4_level_m, B5_level_m, B6_level_m, B7_level_m, B3_w_NaCl, B5_w_NaCl, B5_temp_C, B6_temp_C, B7_temp_C, FIS801_kg_s, P1_cmd, P2_cmd, B5_heater_cmd, B6_cooler_cmd, B7_cooler_cmd, and all automated valve command outputs V1_open through V25_open as listed in the brief. */

    requirement Heater_Fail_Closed_Valves_Fail_Closed : SafetyRequirement {
      doc /* Automated valves V1, V3, V5, V6, V8, V9, V11, V12, V15, V18, V20, V22, V23, V24, and V25 fail closed on loss of power. */
    }

    requirement Heater_Permissive_Requires_Level_And_Condenser_Flow : SafetyRequirement {
      doc /* Heater permissive is LIS_501 >= 0.05 m and FIS_801 >= 0.10 kg/s. Heater is inhibited when LIS_501 < 0.05 m or condenser cooling_water flow proof is below 0.10 kg/s. Source: REQ_SAF_001 and REQ_SAF_005. */
    }

    requirement P1_Dry_Run_Permissive_And_Alarm : SafetyRequirement {
      doc /* P1 permissive requires LIS_701 > 0.02 m and P1 is inhibited when LIS_701 <= 0.02 m. P1 has low discharge pressure alarm if PIS_901 < 0.8 bar while running. */
    }

    requirement P2_Dry_Run_Permissive_And_Alarm : SafetyRequirement {
      doc /* P2 permissive requires LIS_601 > 0.02 m and P2 is inhibited when LIS_601 <= 0.02 m. P2 has low discharge pressure alarm if PIS_1001 < 0.8 bar while running. */
    }

    requirement Join_Before_Reset : SafetyRequirement {
      doc /* Join is satisfied only when both parallel branches report completion. Cycle reset or restart cannot occur until both parallel return branches are complete and time exceeds 2500 s. Requirement specification states completion is both complete and time > 2500 s; acceptance test states Initial becomes active only after process time >2500 s. */
    }
  }

  part NaCl_Evaporation_Plant : Plant {
    attribute startEnable = true;
    attribute B3_available = true;
  }
}
