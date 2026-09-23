package Single_Tank_Transfer_Sequence {

part def Atmospheric_Tank {
    attribute level : ScalarValues::Real;
    doc /* Atmospheric liquid tank; no geometry, capacity, or initial level provided in the brief. */
}

part def Valve {
    attribute commanded_open : ScalarValues::Boolean;
}

part def Level_Switch {
    attribute senses_level : ScalarValues::String;
}

part def Human_Interface {
    attribute START : ScalarValues::Boolean;
    attribute STOP : ScalarValues::Boolean;
    attribute SHUT : ScalarValues::Boolean;
}

part def Sequence_Controller {
    attribute experiment_duration_s : ScalarValues::Real = 900.0;
    attribute wait_duration_s : ScalarValues::Real = 10.0;
    attribute paused : ScalarValues::Boolean = false;
    attribute inlet_inhibited : ScalarValues::Boolean = false;
    attribute report_tank_levels : ScalarValues::Boolean = true;
    attribute report_valve_commands : ScalarValues::Boolean = true;
    attribute active_state : ScalarValues::String = "Idle";
    doc /* Controls Inlet_valve, Transfer_valve, and Drain_valve. STOP closes every valve and pauses; later START resumes interrupted state. SHUT has priority over STOP, inhibits inlet, opens transfer and drain until both tanks are empty, then returns to Idle automatically. */
}

action def Start_Fill_Tank_1 {
    doc /* Idle or paused Fill_Tank_1 -> Fill_Tank_1; command Inlet_valve open, Transfer_valve closed, Drain_valve closed; initiated by START; on resume after STOP, continue interrupted Fill_Tank_1 state rather than restart sequence. */
}

action def Wait_After_High_Level {
    doc /* Fill_Tank_1 -> Wait_1; guard Tank_1_High_level_switch reached; command every valve closed during wait; wait duration 10 s; next state Transfer_To_Tank_2. */
}

action def Start_Transfer_To_Tank_2 {
    doc /* Wait_1 -> Transfer_To_Tank_2; after 10 s; command Transfer_valve open, Inlet_valve closed, Drain_valve closed; continue until Tank_1_Low_level_switch reached. */
}

action def Wait_After_Tank_1_Low_Level {
    doc /* Transfer_To_Tank_2 -> Wait_2; guard Tank_1_Low_level_switch reached; command every valve closed during wait; wait duration 10 s; next state Drain_Tank_2. */
}

action def Start_Drain_Tank_2 {
    doc /* Wait_2 -> Drain_Tank_2; after 10 s; command Drain_valve open, Inlet_valve closed, Transfer_valve closed; continue until Tank_2_Low_level_switch reached. */
}

action def Complete_Normal_Sequence {
    doc /* Drain_Tank_2 -> Idle; guard Tank_2_Low_level_switch reached; command every valve closed; normal completion of one sequence cycle; no repeat behavior stated in the brief. */
}

action def Stop_Sequence {
    doc /* Any active normal-sequence state or paused state -> Paused; guard STOP issued and SHUT not competing with higher priority; command every valve closed; pause sequence and retain interrupted state for later START resume. */
}

action def Resume_After_Stop {
    doc /* Paused -> interrupted prior state; guard later START issued; resume interrupted Fill_Tank_1, Wait_1, Transfer_To_Tank_2, Wait_2, or Drain_Tank_2 rather than restart from beginning. */
}

action def Execute_Shutdown {
    doc /* Any state including Paused -> Shutdown_Emptying; guard SHUT issued; priority higher than STOP; command inlet inhibited, Transfer_valve open, Drain_valve open; continue until both Tank_1_Low_level_switch and Tank_2_Low_level_switch reached. */
}

action def Complete_Shutdown {
    doc /* Shutdown_Emptying -> Idle; guard both Tank_1_Low_level_switch and Tank_2_Low_level_switch reached; command every valve closed; SHUT empties both tanks and then returns to Idle automatically. */
}

requirement STOP_behavior {
    doc /* Source: clarified engineering brief. When STOP is issued, every valve closes and the sequence pauses. A later START resumes the interrupted state rather than restarting from the beginning. */
}

requirement SHUT_behavior {
    doc /* Source: clarified engineering brief. SHUT has priority over STOP. SHUT inhibits inlet and opens transfer and drain until both tanks are empty, then returns to Idle automatically. */
}

part Single_Tank_Transfer_System {
    part Operator : Human_Interface;
    part Controller : Sequence_Controller;
    part Tank_1 : Atmospheric_Tank;
    part Tank_2 : Atmospheric_Tank;
    part Inlet_valve : Valve;
    part Transfer_valve : Valve;
    part Drain_valve : Valve;
    part High_level_switch : Level_Switch;
    part Tank_1_Low_level_switch : Level_Switch;
    part Tank_2_Low_level_switch : Level_Switch;

    attribute experiment_duration_s : ScalarValues::Real = 900.0;
    attribute report_tank_levels : ScalarValues::Boolean = true;
    attribute report_valve_commands : ScalarValues::Boolean = true;

    connect Operator to Controller;
    connect Controller to Inlet_valve;
    connect Controller to Transfer_valve;
    connect Controller to Drain_valve;
    connect High_level_switch to Tank_1;
    connect Tank_1_Low_level_switch to Tank_1;
    connect Tank_2_Low_level_switch to Tank_2;
    connect Tank_1 to Inlet_valve;
    connect Tank_1 to Transfer_valve;
    connect Tank_1 to Drain_valve;
    connect Tank_2 to Inlet_valve;
    connect Tank_2 to Transfer_valve;
    connect Tank_2 to Drain_valve;

    state Idle;
    state Fill_Tank_1;
    state Wait_1;
    state Transfer_To_Tank_2;
    state Wait_2;
    state Drain_Tank_2;
    state Paused;
    state Shutdown_Emptying;

    doc /* Topology reflects only the stated generic connection: Tank 1 and Tank 2 are connected by the Inlet valve, Transfer valve, and Drain valve, with no further endpoint detail confirmed. High-level switch senses Tank 1. Distinct low-level switches sense Tank 1 and Tank 2 respectively. No equations, valve flow laws, tank geometry, switch thresholds, initial tank levels, sample interval, simulation start time, reset command, or shutdown resumability beyond automatic return to Idle are provided in the brief. */
}

}