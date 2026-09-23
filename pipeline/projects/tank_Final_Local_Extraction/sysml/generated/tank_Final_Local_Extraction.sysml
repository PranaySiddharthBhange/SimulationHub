package Two_Tank_Fill_Transfer_Drain_System {

part def Valve;
part def Tank;
part def Sensor;
part def Command_Input;
part def Controller;
part def Boundary;

requirement URS_M_001 {
    doc /* STOP closes V1, V2, and V3 and suspends automatic operation / places the controller in a paused condition. Source: 01_01_customer_URS.txt; 02_02_engineering_data_register_chunk00.txt URS_MOD_001 */
}

requirement URS_M_003 {
    doc /* SHUT opens V2 and V3, inhibits V1, empties both tanks; when LT_101 and LT_102 are both at or below low setpoints, V2 and V3 close and controller returns to start configuration. Source: 01_01_customer_URS.txt URS_M_003 URS_M_004; 02_02_engineering_data_register_chunk00.txt URS_MOD_003; 06_06_design_review_minutes.txt */
}

requirement AC_01 {
    doc /* T1 reaches 0.80 m before the first transfer begins == 1.0 (relative tolerance 0.000%), always value -- source: 11_09_test_procedure_TP17.txt AC_01 */
}
requirement AC_02 {
    doc /* During STOP intervals, V1=0 and V2=0 and V3=0 == 1.0 (relative tolerance 0.000%), always value -- source: 11_09_test_procedure_TP17.txt AC_02; AC_05 */
}
requirement AC_03 {
    doc /* The START at 280 s resumes the interrupted transfer == 1.0 (relative tolerance 0.000%), at t=280.0 -- source: 11_09_test_procedure_TP17.txt AC_03 */
}
requirement AC_04 {
    doc /* Following completion of the first T2 drain, another fill cycle begins automatically after an 8 s inter_cycle delay == 1.0 (relative tolerance 0.000%), always value -- source: 11_09_test_procedure_TP17.txt AC_04 */
}
requirement AC_05 {
    doc /* From 650 s until SHUT at 700 s, V1=0 and V2=0 and V3=0 == 1.0 (relative tolerance 0.000%), always value -- source: 11_09_test_procedure_TP17.txt AC_05 */
}
requirement AC_06 {
    doc /* At 700 s, V1=0 and V2=1 and V3=1 == 1.0 (relative tolerance 0.000%), at t=700.0 -- source: 11_09_test_procedure_TP17.txt AC_06 */
}
requirement AC_07 {
    doc /* At 900 s, controller_state=IDLE and V1=0 and V2=0 and V3=0 == 1.0 (relative tolerance 0.000%), at t=900.0 -- source: 11_09_test_procedure_TP17.txt AC_07 */
}
requirement AC_08 {
    doc /* During normal automatic operation, not(V1 and V2) and not(V2 and V3) == 1.0 (relative tolerance 0.000%), always value -- source: 11_09_test_procedure_TP17.txt AC_08; 06_06_design_review_minutes.txt D_08 D_09 */
}

action def Start_From_Idle_Or_Paused {
    doc /* source -> IDLE or PAUSED; target -> FILL_T1 or resume retained context; guard -> START edge and not active SHUTDOWN; command -> if IDLE begin automatic sequence, if PAUSED continue from point STOP was accepted; wait/duration -> retained wait timer is resumed, not restarted; priority -> lower than SHUT, START while already running is ignored. Source: 01_01_customer_URS.txt; 02_02_engineering_data_register_chunk00.txt; 05_04_control_logic_design_notes.txt; 06_06_design_review_minutes.txt */
}

action def Stop_To_Paused {
    doc /* source -> any normal automatic state FILL_T1 WAIT_AFTER_FILL TRANSFER_T1_T2 WAIT_AFTER_TRANSFER DRAIN_T2 WAIT_AFTER_DRAIN; target -> PAUSED; guard -> STOP edge; command -> close V1 V2 V3, suspend automatic operation; wait/duration -> if STOP occurs during a wait state, remaining wait time is frozen; priority -> lower than SHUT. Source: URS_M_001; URS_MOD_001; URS_MOD_002; 05_04_control_logic_design_notes.txt */
}

action def Shut_To_Shutdown {
    doc /* source -> any state except active SHUTDOWN remains in SHUTDOWN if already there; target -> SHUTDOWN; guard -> SHUT edge; command -> inhibit V1, open V2 and V3 together, waive normal V2 V3 simultaneous_open restriction in SHUTDOWN; wait/duration -> continue until LT_101 <= T1 low and LT_102 <= T2 low; priority -> highest, START or STOP during active SHUTDOWN is ignored. Source: URS_M_003 URS_M_004; 02_02_engineering_data_register_chunk00.txt URS_MOD_003; 05_04_control_logic_design_notes.txt; 06_06_design_review_minutes.txt; 11_09_test_procedure_TP17.txt AC_06 */
}

action def Fill_To_Wait_After_Fill {
    doc /* source -> FILL_T1; target -> WAIT_AFTER_FILL; guard -> LT_101 >= 0.80 m, equality included; command -> close V1; wait/duration -> immediate state change then 10 s wait in WAIT_AFTER_FILL; priority -> normal automatic transition. Source: 05_04_control_logic_design_notes.txt; 11_09_test_procedure_TP17.txt AC_01; clarified setpoint */
}

action def Wait_After_Fill_To_Transfer {
    doc /* source -> WAIT_AFTER_FILL; target -> TRANSFER_T1_T2; guard -> 10 s elapsed; command -> open V2, keep V1 and V3 closed; wait/duration -> 10 s fixed delay; priority -> normal automatic transition. Source: notes consistent on 10 s */
}

action def Transfer_To_Wait_After_Transfer {
    doc /* source -> TRANSFER_T1_T2; target -> WAIT_AFTER_TRANSFER; guard -> LT_101 <= 0.05 m, equality included; command -> close V2; wait/duration -> immediate state change then 10 s wait in WAIT_AFTER_TRANSFER; priority -> normal automatic transition. Source: 05_04_control_logic_design_notes.txt; clarified wait after T1 low uses 10 s */
}

action def Wait_After_Transfer_To_Drain {
    doc /* source -> WAIT_AFTER_TRANSFER; target -> DRAIN_T2; guard -> 10 s elapsed; command -> open V3, keep V1 and V2 closed; wait/duration -> 10 s fixed delay; priority -> normal automatic transition. Source: clarified wait after T1 low = 10 s */
}

action def Drain_To_Wait_After_Drain {
    doc /* source -> DRAIN_T2; target -> WAIT_AFTER_DRAIN; guard -> LT_102 <= 0.05 m, equality included; command -> close V3; wait/duration -> immediate state change then 8 s wait in WAIT_AFTER_DRAIN; priority -> normal automatic transition. Source: 05_04_control_logic_design_notes.txt; clarified TP17 inter_cycle wait = 8 s */
}

action def Wait_After_Drain_To_Fill {
    doc /* source -> WAIT_AFTER_DRAIN; target -> FILL_T1; guard -> 8 s elapsed; command -> open V1, keep V2 and V3 closed; wait/duration -> 8 s fixed inter_cycle delay; priority -> normal automatic transition and cycle repeat. Source: 11_09_test_procedure_TP17.txt AC_04; clarified TP17 configuration */
}

action def Shutdown_Completion_To_Idle {
    doc /* source -> SHUTDOWN; target -> IDLE; guard -> LT_101 <= 0.05 m and LT_102 <= 0.05 m, equality included for both; command -> close V2 and V3, V1 remains inhibited/closed, reset sequence context to IDLE/start configuration; wait/duration -> immediate upon both tanks emptying to low thresholds; priority -> shutdown completion. Source: 01_01_customer_URS.txt URS_M_004; 02_02_engineering_data_register_chunk01.txt; 06_06_design_review_minutes.txt */
}

part Two_Tank_System {
    part PLC_101 : Controller;
    part Tank_1 : Tank {
        doc /* aliases: tank1 / T1 / TK_101 */
        attribute initial_level_m : ScalarValues::Real = 0.05;
        attribute low_level_limit_m : ScalarValues::Real = 0.05;
        attribute high_level_limit_m : ScalarValues::Real = 0.80;
        attribute cross_section_area_m2 : ScalarValues::Real = 1.20;
    }
    part Tank_2 : Tank {
        doc /* aliases: tank2 / T2 / TK_102 */
        attribute initial_level_m : ScalarValues::Real = 0.05;
        attribute low_level_limit_m : ScalarValues::Real = 0.05;
        attribute cross_section_area_m2 : ScalarValues::Real = 1.40;
    }
    part XV_101 : Valve {
        doc /* aliases: valve1 / V1 / inlet valve to Tank 1; actuator 24 VDC spring_return closed */
        attribute discrete_output_id : ScalarValues::String = "DO_101";
        attribute fail_safe_closed : ScalarValues::Boolean = true;
        attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0060;
    }
    part XV_102 : Valve {
        doc /* aliases: valve2 / V2 / transfer valve from Tank 1 to Tank 2; actuator 24 VDC spring_return closed */
        attribute discrete_output_id : ScalarValues::String = "DO_102";
        attribute fail_safe_closed : ScalarValues::Boolean = true;
        attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0045;
    }
    part XV_103 : Valve {
        doc /* aliases: valve3 / V3 / drain valve from Tank 2 to drain; actuator 24 VDC spring_return closed */
        attribute discrete_output_id : ScalarValues::String = "DO_103";
        attribute fail_safe_closed : ScalarValues::Boolean = true;
        attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0050;
    }
    part LT_101 : Sensor {
        doc /* Tank 1 level measurement to AI_101 */
        attribute analog_input_id : ScalarValues::String = "AI_101";
        attribute measured_unit : ScalarValues::String = "m";
    }
    part LT_102 : Sensor {
        doc /* Tank 2 level measurement to AI_102 */
        attribute analog_input_id : ScalarValues::String = "AI_102";
        attribute measured_unit : ScalarValues::String = "m";
    }
    part START : Command_Input {
        doc /* aliases: PB_START / DI_101; momentary digital command */
        attribute digital_input_id : ScalarValues::String = "DI_101";
    }
    part STOP : Command_Input {
        doc /* aliases: PB_STOP / DI_102; momentary digital command */
        attribute digital_input_id : ScalarValues::String = "DI_102";
    }
    part SHUT : Command_Input {
        doc /* aliases: PB_SHUT / DI_103; momentary digital command */
        attribute digital_input_id : ScalarValues::String = "DI_103";
    }
    part SRC_101 : Boundary;
    part DRN_101 : Boundary;

    connect SRC_101 to XV_101;
    connect XV_101 to Tank_1;
    connect Tank_1 to XV_102;
    connect XV_102 to Tank_2;
    connect Tank_2 to XV_103;
    connect XV_103 to DRN_101;
    connect LT_101 to Tank_1;
    connect LT_102 to Tank_2;
    connect PLC_101 to XV_101;
    connect PLC_101 to XV_102;
    connect PLC_101 to XV_103;
    connect LT_101 to PLC_101;
    connect LT_102 to PLC_101;
    connect START to PLC_101;
    connect STOP to PLC_101;
    connect SHUT to PLC_101;

    attribute experiment_start_s : ScalarValues::Real = 0.0;
    attribute experiment_stop_s : ScalarValues::Real = 900.0;
    attribute scheduled_start_1_s : ScalarValues::Real = 20.0;
    attribute scheduled_stop_1_s : ScalarValues::Real = 220.0;
    attribute scheduled_start_2_s : ScalarValues::Real = 280.0;
    attribute scheduled_stop_2_s : ScalarValues::Real = 650.0;
    attribute scheduled_shut_s : ScalarValues::Real = 700.0;
    attribute wait_after_fill_s : ScalarValues::Real = 10.0;
    attribute wait_after_transfer_s : ScalarValues::Real = 10.0;
    attribute wait_after_drain_s : ScalarValues::Real = 8.0;
    attribute report_tank1_level_name : ScalarValues::String = "tank1_level_m";
    attribute report_tank2_level_name : ScalarValues::String = "tank2_level_m";
    attribute report_valve1_name : ScalarValues::String = "valve1_open";
    attribute report_valve2_name : ScalarValues::String = "valve2_open";
    attribute report_valve3_name : ScalarValues::String = "valve3_open";
    attribute report_controller_state_name : ScalarValues::String = "controller_state";
    attribute report_valve_open_unit : ScalarValues::String = "%";
    attribute report_state_type : ScalarValues::String = "string";

    state IDLE;
    state FILL_T1;
    state WAIT_AFTER_FILL;
    state TRANSFER_T1_T2;
    state WAIT_AFTER_TRANSFER;
    state DRAIN_T2;
    state WAIT_AFTER_DRAIN;
    state PAUSED;
    state SHUTDOWN;

    doc /* Initial condition: controller starts in IDLE; Tank_1 level = 0.05 m; Tank_2 level = 0.05 m; all three valves closed. Normal state valve commands: FILL_T1 -> XV_101 open, XV_102/XV_103 closed. TRANSFER_T1_T2 -> XV_102 open, XV_101/XV_103 closed. DRAIN_T2 -> XV_103 open, XV_101/XV_102 closed. IDLE, WAIT_AFTER_FILL, WAIT_AFTER_TRANSFER, WAIT_AFTER_DRAIN, PAUSED -> all valves closed. SHUTDOWN -> XV_101 inhibited/closed and XV_102/XV_103 commanded open until both tanks are at or below 0.05 m, then all valves closed and return to IDLE. START at 20 s from IDLE initiates sequence. STOP at 220 s pauses and closes all valves. START at 280 s resumes from retained context, including frozen remaining wait time if paused during a wait. STOP at 650 s closes all valves and pauses until SHUT at 700 s. SHUT has highest priority over normal operation and pause, START/STOP while active SHUTDOWN are ignored. Normal automatic operation is cyclic after WAIT_AFTER_DRAIN returns to FILL_T1. Interlocks: XV_101 and XV_102 shall never be commanded open simultaneously. XV_102 and XV_103 shall not be open simultaneously during normal automatic operation; this restriction is waived only in SHUTDOWN. Legacy demo physics evidence only: der(Tank_1 level) = (if XV_101 open then 0.0060 else 0)/1.20 - (if XV_102 open then 0.0045 else 0)/1.20; der(Tank_2 level) = (if XV_102 open then 0.0045 else 0)/1.40 - (if XV_103 open then 0.0050 else 0)/1.40 from 09_07_legacy_tank_demo.txt, noted as simplified demonstration logic lacking SHUT handling. */
}

}