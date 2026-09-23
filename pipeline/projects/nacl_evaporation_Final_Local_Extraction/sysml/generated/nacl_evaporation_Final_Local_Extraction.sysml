package NaCl_Evaporation_System {
  part def Tank {
    attribute description : ScalarValues::String;
    attribute level_max_m : ScalarValues::Real;
    attribute base_elevation_m : ScalarValues::Real;
  }

  part def Actuator {
    attribute description : ScalarValues::String;
    attribute commanded_on : ScalarValues::Boolean;
  }

  part def Valve {
    attribute description : ScalarValues::String;
    attribute fail_closed : ScalarValues::Boolean = true;
    attribute actuation_voltage_VDC : ScalarValues::Real = 24.0;
    attribute opening_time_s : ScalarValues::Real = 0.7;
    attribute closing_time_s : ScalarValues::Real = 0.5;
    attribute commanded_open : ScalarValues::Boolean;
  }

  part def Sensor {
    attribute description : ScalarValues::String;
  }

  requirement REQ_DAT_001 {
    doc /* 02_02_process_data_register_chunk01: controller inputs required: LIS_301, QI_302, LIS_501, QIS_502, TIS_602, TIS_702, FIS_801 */
  }

  requirement REQ_DAT_002 {
    doc /* 02_02_process_data_register_chunk01: controller outputs required: V1 V3 V5 V6 V8 V9 V11 V12 V15 V18 V20 V22 V23 V24 V25, P1, P2, B5_Heater, B6_Cooler, B7_Cooler */
  }

  requirement REQ_VV_001 {
    doc /* 02_02_process_data_register_chunk01: at least one parallel branch split and rejoin and continuation beyond 2500 s */
  }

  part System {
    attribute medium : ScalarValues::String = "WaterNaCl";
    attribute stop_time_s : ScalarValues::Real = 3000.0;
    attribute restart_time_s : ScalarValues::Real = 2500.0;
    attribute report_experiment_s : ScalarValues::Real = 900.0;
    attribute B6_cooling_duty_benchmark_W : ScalarValues::Real = -6500.0;
    attribute B7_cooling_duty_benchmark_W : ScalarValues::Real = -4500.0;
    attribute heater_Q_flow_when_on : ScalarValues::Real = 20000.0;
    attribute note_heater_units : ScalarValues::String = "Q_flow quantity stated; units not explicitly stated in heater notes";
    attribute static_head_required_non_horizontal_pipes : ScalarValues::Boolean = true;
    attribute small_junction_volumes_required : ScalarValues::Boolean = true;
    attribute above_level_outflow_loss_factor_default : ScalarValues::Real = 100000.0;
    attribute above_level_inflow_factor_default : ScalarValues::Real = 0.01;

    part B1 : Tank {
      attribute description : ScalarValues::String = "charging tank B1 initial water rich charge and recovered water destination";
      attribute level_max_m : ScalarValues::Real = 0.60;
      attribute base_elevation_m : ScalarValues::Real = 4.8;
    }
    part B2 : Tank {
      attribute description : ScalarValues::String = "charging tank B2 initial concentrated NaCl charge and recovered concentrate destination";
      attribute level_max_m : ScalarValues::Real = 0.60;
      attribute base_elevation_m : ScalarValues::Real = 4.8;
    }
    part B3 : Tank {
      attribute description : ScalarValues::String = "mixing tank B3";
      attribute level_max_m : ScalarValues::Real = 0.45;
      attribute base_elevation_m : ScalarValues::Real = 3.5;
    }
    part B4 : Tank {
      attribute description : ScalarValues::String = "intermediate output tank B4";
      attribute level_max_m : ScalarValues::Real = 0.45;
      attribute base_elevation_m : ScalarValues::Real = 2.6;
    }
    part B5 : Tank {
      attribute description : ScalarValues::String = "evaporator vessel B5 alias D8 by LIS_501 QIS_502 TI_503 pairing";
      attribute level_max_m : ScalarValues::Real = 0.45;
      attribute base_elevation_m : ScalarValues::Real = 1.5;
    }
    part K1 : Tank {
      attribute description : ScalarValues::String = "condenser K1 alias B9 by cooling water function";
      attribute level_max_m : ScalarValues::Real = 0.0;
      attribute base_elevation_m : ScalarValues::Real = 2.8;
    }
    part B6 : Tank {
      attribute description : ScalarValues::String = "condensate cooling return tank B6 alias B10";
      attribute level_max_m : ScalarValues::Real = 0.40;
      attribute base_elevation_m : ScalarValues::Real = 1.5;
    }
    part B7 : Tank {
      attribute description : ScalarValues::String = "concentrate cooling return tank B7 alias B11 buffer return tank";
      attribute level_max_m : ScalarValues::Real = 0.40;
      attribute base_elevation_m : ScalarValues::Real = 0.7;
    }

    part P1 : Actuator { attribute description : ScalarValues::String = "return pump P1 on B7 branch"; }
    part P2 : Actuator { attribute description : ScalarValues::String = "return pump P2 on B6 branch"; }
    part B5_Heater : Actuator { attribute description : ScalarValues::String = "heater actuator for B5"; }
    part B6_Cooler : Actuator { attribute description : ScalarValues::String = "cooler actuator for B6"; }
    part B7_Cooler : Actuator { attribute description : ScalarValues::String = "cooler actuator for B7"; }

    part V1 : Valve { attribute description : ScalarValues::String = "return path valve"; }
    part V3 : Valve { attribute description : ScalarValues::String = "return path valve"; }
    part V5 : Valve { attribute description : ScalarValues::String = "return path valve"; }
    part V6 : Valve { attribute description : ScalarValues::String = "return path valve"; }
    part V8 : Valve { attribute description : ScalarValues::String = "B1 to B3 valve"; }
    part V9 : Valve { attribute description : ScalarValues::String = "B2 to B3 valve"; }
    part V11 : Valve { attribute description : ScalarValues::String = "B3 to B4 valve"; }
    part V12 : Valve { attribute description : ScalarValues::String = "B4 to B5 valve"; }
    part V15 : Valve { attribute description : ScalarValues::String = "B5 to B7 concentrate valve"; }
    part V18 : Valve { attribute description : ScalarValues::String = "B7 P1 branch return valve"; }
    part V20 : Valve { attribute description : ScalarValues::String = "B6 P2 branch return valve"; }
    part V22 : Valve { attribute description : ScalarValues::String = "B7 P1 branch return valve"; }
    part V23 : Valve { attribute description : ScalarValues::String = "B7 P1 branch return valve"; }
    part V24 : Valve { attribute description : ScalarValues::String = "B6 P2 branch return valve"; }
    part V25 : Valve { attribute description : ScalarValues::String = "B6 P2 branch return valve"; }

    part LIS_301 : Sensor { attribute description : ScalarValues::String = "B3 level"; }
    part QI_302 : Sensor { attribute description : ScalarValues::String = "B3 NaCl mass fraction"; }
    part LIS_501 : Sensor { attribute description : ScalarValues::String = "B5 level"; }
    part QIS_502 : Sensor { attribute description : ScalarValues::String = "B5 NaCl mass fraction"; }
    part TI_503 : Sensor { attribute description : ScalarValues::String = "B5 temperature"; }
    part TIS_602 : Sensor { attribute description : ScalarValues::String = "B6 temperature"; }
    part TIS_702 : Sensor { attribute description : ScalarValues::String = "B7 temperature"; }
    part FIS_801 : Sensor { attribute description : ScalarValues::String = "cooling water flow"; }
    part PIS_901 : Sensor { attribute description : ScalarValues::String = "pressure indicator switch"; }
    part PIS_1001 : Sensor { attribute description : ScalarValues::String = "pressure indicator switch"; }
    part Central_Controller;

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
    connect B7 to P1;
    connect B6 to P2;
    connect B7 to V18;
    connect V18 to V23;
    connect V23 to V22;
    connect V22 to V1;
    connect V1 to V3;
    connect V3 to B1;
    connect B6 to V20;
    connect V20 to V24;
    connect V24 to V25;
    connect V25 to V5;
    connect V5 to V6;
    connect V6 to B2;
    connect LIS_301 to B3;
    connect QI_302 to B3;
    connect LIS_501 to B5;
    connect QIS_502 to B5;
    connect TI_503 to B5;
    connect TIS_602 to B6;
    connect TIS_702 to B7;
    connect FIS_801 to K1;
    connect PIS_901 to P1;
    connect PIS_1001 to P2;
    connect Central_Controller to LIS_301;
    connect Central_Controller to QI_302;
    connect Central_Controller to LIS_501;
    connect Central_Controller to QIS_502;
    connect Central_Controller to TIS_602;
    connect Central_Controller to TIS_702;
    connect Central_Controller to FIS_801;
    connect Central_Controller to V1;
    connect Central_Controller to V3;
    connect Central_Controller to V5;
    connect Central_Controller to V6;
    connect Central_Controller to V8;
    connect Central_Controller to V9;
    connect Central_Controller to V11;
    connect Central_Controller to V12;
    connect Central_Controller to V15;
    connect Central_Controller to V18;
    connect Central_Controller to V20;
    connect Central_Controller to V22;
    connect Central_Controller to V23;
    connect Central_Controller to V24;
    connect Central_Controller to V25;
    connect Central_Controller to P1;
    connect Central_Controller to P2;
    connect Central_Controller to B5_Heater;
    connect Central_Controller to B6_Cooler;
    connect Central_Controller to B7_Cooler;
  }

  action def Initial_Idle_Reset {
    doc /* Initial -> Step1_Water_Charge_B3; guard: startEnable and B3 available; command: all valves closed, P1 off, P2 off, B5_Heater off, B6_Cooler off, B7_Cooler off; priority: initial */
  }
  action def Step1_Water_Charge_B3 {
    doc /* Step1_Water_Charge_B3 -> Step2_Brine_Charge_Mix_B3; guard: LIS_301 >= 0.13 m; command: V8 open; other automated valves closed unless required by another active branch */
  }
  action def Step2_Brine_Charge_Mix_B3 {
    doc /* Step2_Brine_Charge_Mix_B3 -> Step3_Transfer_B3_to_B4; guard: QI_302 >= 0.080 kg_per_kg; command: V9 open */
  }
  action def Step3_Transfer_B3_to_B4 {
    doc /* Step3_Transfer_B3_to_B4 -> Step4_Wait_B5_Idle; guard: LIS_301 < 0.01 m; command: V11 open; note: 12_09_batch_acceptance_test has one <=0.01 m line but repeated guard is below 0.01 m */
  }
  action def Step4_Wait_B5_Idle {
    doc /* Step4_Wait_B5_Idle -> Step5_Transfer_B4_to_B5; guard: LIS_501 < 0.01 m and NOT V15; command: no transfer actuator */
  }
  action def Step5_Transfer_B4_to_B5 {
    doc /* Step5_Transfer_B4_to_B5 -> Step6_Heat_Evaporate_B5; guard: LIS_501 >= 0.18 m; command: V12 open */
  }
  action def Step6_Heat_Evaporate_B5 {
    doc /* Step6_Heat_Evaporate_B5 -> Parallel_Split; guard: QIS_502 >= 0.180 kg_per_kg; command: B5_Heater on; permissive: LIS_501 >= 0.05 m and FIS_801 >= 0.10 kg_per_s; TI_503 constraint <= 130 degC; interpretation per confirmed clarification: heater on until QIS_502 reaches 0.180 kg/kg */
  }
  action def Branch_A_B6_Cool_And_Return {
    doc /* Parallel_Split -> Join_Wait; condensate branch facts retained from notes: B5 vapor/process stream goes to K1, K1 condensate to B6, B6_Cooler on until TIS_602 <= 20 degC, then P2 return on through V20 V24 V25 V5 V6 to B2 per approved current routing; exact intermediate approved state list not fully provided in Stage 1 notes */
  }
  action def Branch_B_Step7_Wait_B7_Idle {
    doc /* Parallel_Split -> Branch_B_Step8_Transfer_B5_to_B7; guard: LIS_701 < 0.01 m stated in notes; command: no transfer actuator; source note names LIS_701 though canonical sensor list only explicitly included TIS_702 for controller input */
  }
  action def Branch_B_Step8_Transfer_B5_to_B7 {
    doc /* Branch_B_Step8_Transfer_B5_to_B7 -> Branch_B_Step9_Cool_B7; guard: LIS_501 < 0.01 m; command: V15 open */
  }
  action def Branch_B_Step9_Cool_B7 {
    doc /* Branch_B_Step9_Cool_B7 -> Branch_B_Return_B7_to_B1; guard: TIS_702 <= 25 degC; command: B7_Cooler on */
  }
  action def Branch_B_Return_B7_to_B1 {
    doc /* Branch_B_Return_B7_to_B1 -> Join_Wait; command: P1 on and V18 V23 V22 V1 V3 open to return B7 concentrate to B1 per approved current routing; interlock: dry run inhibit start or trip from source tank level, explicit minimum source level provided only for pump branch with LIS_701 > 0.02 m and low discharge pressure alarm PIS_901 < 0.8 bar */
  }
  action def Join_Wait_And_Cycle_Reset {
    doc /* Join_Wait -> Initial_Idle_Reset; guard: both branches complete and time > 2500 s; command: cycle reset; repeat behavior: sequential StateGraph with parallel split after evaporation and join before cycle reset; simulation to continue beyond 2500 s, stop_time 3000 s */
  }
  action def STOP_Shutdown_Reset {
    doc /* Any active state -> Initial_Idle_Reset; command: all automated valves closed because fail closed, P1 off, P2 off, B5_Heater off, B6_Cooler off, B7_Cooler off; shutdown and reset behavior explicit, resume path not further specified in provided notes */
  }

  requirement Safety_And_Interlocks {
    doc /* 06_06_design_review_minutes and 11_08_valve_pump_datasheet: all automated process valves discrete fail closed; heater permissive requires LIS_501 >= 0.05 m and FIS_801 >= 0.10 kg/s; P1 and P2 dry run policy inhibit start and trip from source tank level; explicit source level minimum only stated as LIS_701 > 0.02 m; pressure bounds PIS_901 <= 4.00 bar_g and PIS_1001 <= 4.00 bar_g; low discharge pressure alarm stated for PIS_901 < 0.8 bar */
  }

  requirement Acceptance_Thresholds {
    doc /* exact resolved checks: LIS_301 == 0.13 at value; QI_302 == 0.08 at value; LIS_501 == 0.18 at value; QIS_502 == 0.18 at value; TIS_602 == 20.0 at value before return; TIS_702 == 25.0 at value before return; FIS_801 == 0.1 always value; time == 2500.0 final value; relative tolerance 0.000 percent for each listed check */
  }
}