package Behaviors {
    action def Close_V1_On_T1_High;
    // Tank 1 level >= 0.78 m -> close V1
    action def Wait_10s_Before_Open_V2_On_T1_High;
    // Tank 1 level >= 0.78 m -> wait 10 s before opening V2
    action def Close_V2_On_T1_Low;
    // Tank 1 level <= 0.05 m -> close V2
    action def Wait_10s_Before_Open_V3_On_T1_Low;
    // Tank 1 level <= 0.05 m -> wait 10 s before opening V3
    action def Close_V3_On_T2_Low;
    // Tank 2 level <= 0.05 m -> close V3
    action def Stop_All_Valves_On_STOP_Command;
    // STOP command == received  -> close all three valves and suspend automatic operation
    action def Enter_SHUT_Open_V2_V3_Inhibit_V1;
    // SHUT command == received  -> open V2 and V3; inhibit V1
    action def Complete_Shutdown_Close_V2_V3_Return_Idle;
    // shutdown emptying achieved == true  -> close V2 and V3; return controller to start configuration
    action def Start_Automatic_Sequence_On_VALID_START;
    // START command received while process is idle or paused == valid START command  -> start sequence automatic fill-transfer-drain sequence
    action def Close_V1_On_T1_High_Demo;
    // Tank 1 level >= 0.8 m -> close V1 / XV-101
    action def Wait_12s_Before_Open_V2_On_T1_High_Demo;
    // Tank 1 level >= 0.8 m -> wait controller for 12 s before opening V2 / XV-102
    action def Open_V3_After_12s_On_T1_Low_Demo;
    // Tank 1 level <= 0.05 m -> open V3 / XV-103 after 12 s wait
    action def Return_To_Fill_T1_After_8s_On_T2_Low_Demo;
    // Tank 2 level <= 0.05 m -> return to Tank 1 filling operation after 8 s
    action def Pause_All_Valves_On_STOP_Command_Demo;
    // STOP command received == STOP command  -> close V1, V2, and V3 and pause controller
    action def Resume_Sequence_After_STOP_Command_Demo;
    // START command received following STOP == START after STOP  -> continue sequence from point STOP was accepted
    action def Open_V2_V3_On_SHUT_Command_Demo;
    // SHUT command received == SHUT command  -> open V2 and V3 for shutdown drain
    action def Finish_Shutdown_Close_All_Valves_Demo;
    // shutdown draining complete == complete  -> close all three valves and set initial idle configuration
    action def Close_All_Valves_On_Power_Loss;
    // controller power lost == loss of controller power  -> move/keep closed all process valves
    action def Freeze_Wait_Timer_On_STOP_During_Wait;
    // STOP command received during wait state == STOP command during wait state  -> freeze wait timer rather than restart it
    action def Ignore_START_While_Running;
    // START command received while already running == START while already running  -> ignore START command
    action def Ignore_STOP_During_SHUT;
    // STOP command received during SHUT mode == STOP during SHUT mode  -> ignore STOP command until shutdown is complete
    action def Ignore_START_During_SHUT;
    // START command received during SHUT mode == START during SHUT mode  -> ignore START command until shutdown is complete
    action def Close_V2_V3_On_Both_Lows_Shutdown_Complete;
    // Tank 1 and Tank 2 levels <= their low-level setpoints m -> allow shutdown completion / close V2 and V3
    action def Start_Controller_Sequence_On_DI101_Rise;
    // DI-101 rising edge == rising edge  -> start/resume controller sequence
    action def Pause_All_Valves_On_DI102_Rise;
    // DI-102 rising edge == rising edge  -> pause and close all valves
    action def Latch_Shutdown_On_DI103_Rise;
    // DI-103 rising edge == rising edge  -> latch shutdown
    action def Set_Controller_Run_On_Start;
    // start == true  -> control tankController
    action def Set_Controller_Stop_On_Stop;
    // stop == true  -> control tankController
    action def Set_Controller_Shut_On_Shut;
    // shut == true  -> control tankController
    action def Transition_IDLE_To_FILL_T1_On_START_Edge;
    // START edge == START edge  -> transition FILL_T1 from IDLE
    action def Transition_To_PAUSED_On_STOP_Edge;
    // STOP edge == STOP edge  -> transition PAUSED with all valves false
    action def Transition_To_SHUTDOWN_On_SHUT_Edge;
    // SHUT edge == SHUT edge  -> transition SHUTDOWN; clear resume context; V1=0,V2=1,V3=1
    action def Enter_WAIT_AFTER_FILL_On_LT101_High;
    // LT-101 >= T1_High m -> transition WAIT_AFTER_FILL; close V1; start timer
    action def Enter_WAIT_AFTER_TRANSFER_On_LT101_Low;
    // LT-101 <= T1_Low m -> transition WAIT_AFTER_TRANSFER; close V2; start timer
    action def Enter_WAIT_AFTER_DRAIN_On_LT102_Low;
    // LT-102 <= T2_Low m -> transition WAIT_AFTER_DRAIN; close V3; start timer
    action def Start_TRANSFER_T1_T2_On_Timer_Expired;
    // timer == expired  -> transition TRANSFER_T1_T2 with V2=1
    action def Start_DRAIN_T2_On_Timer_Expired;
    // timer == expired  -> transition DRAIN_T2 with V3=1
    action def Restart_FILL_T1_On_Timer_Expired;
    // timer == expired  -> transition FILL_T1 with V1=1
    action def Preserve_Remaining_Delay_On_STOP_During_Waits;
    // STOP in WAIT_AFTER_FILL, WAIT_AFTER_TRANSFER, or WAIT_AFTER_DRAIN RANGE configured remaining delay retained s -> preserve timer and state resume with remaining delay on START
    action def Set_All_Valves_False_On_Power_Loss;
    // controller power loss == power loss  -> set outputs false all valves
    action def Transition_To_IDLE_On_Both_Lows;
    // LT-101 <= T1_Low AND LT-102 <= T2_Low RANGE both low-level limits m -> transition IDLE; close V2 and V3
    action def Freeze_Delay_Timer_On_STOP_During_Delay;
    // STOP received during any delay RANGE delay  -> freeze remaining delay delay timer
    action def Ignore_START_While_Sequence_Running;
    // START received while automatic sequence is already running == running  -> ignore command START
    action def Ignore_START_STOP_During_Active_SHUT;
    // START or STOP received during active SHUT == active SHUT  -> ignore command START and STOP
    action def Complete_SHUT_On_Low_Level_Conditions;
    // SHUT completion condition RANGE LT-101 and LT-102 at or below their low-level setpoints  -> complete shutdown SHUT sequence
    action def Reset_To_IDLE_On_Shutdown_Complete;
    // shutdown completion == complete  -> close all valves and reset sequence context to IDLE controller sequence context
    action def Prohibit_V1_V2_Open_Together;
    // V1 and V2 commanded open together == open together  -> prohibit V1 and V2
    action def Prohibit_V2_V3_Open_Together_Normal_Mode;
    // V2 and V3 commanded open together in normal auto operation == open together  -> prohibit V2 and V3
    action def Drop_Out_V1_On_Tank_High;
    // tank level >= 0.8 m -> drop out / stop fill V1 (valve1 / XV-101)
    action def Wait_12s_After_T1_Low_Before_Resuming;
    // tank level after T1 low == 12 s dead time -> wait before resuming controls control logic for second wait period
    action def Resume_Fill_After_8s_On_T2_Low;
    // tank2 low == 8 s dead time -> resume fill new fill sequence
    action def Use_T1_High_As_Effective_Limit;
    // T1 level >= 0.8 m -> use as effective high limit for T1 T1 high limit threshold
    action def Open_Drain_Valve_After_12s_From_T1_Low;
    // time since T1 reaches low level >= 12.0 s -> open drain valve
    action def Start_Next_Fill_After_8s_From_T2_Low;
    // time since T2 reaches low >= 8.0 s -> start next fill
    action def Hold_V2_V3_Open_During_SHUT;
    // state command == SHUT  -> keep commanded open V2 and V3
    action def Release_V2_V3_On_Low_Conditions;
    // low-level conditions == both satisfied  -> allow transition out of SHUT / stop holding open V2 and V3
    action def Ignore_START_During_SHUT_State;
    // state command == START during SHUT  -> ignore START command
    action def Set_Stopped_False_On_StartCmd_Rise;
    // startCmd edge == 1.0  -> set stopped := false
    action def Set_Stopped_True_On_StopCmd_Rise;
    // stopCmd edge == 1.0  -> set stopped := true
    action def Set_Valve1_On_Fill_State_Unless_Stopped;
    // seq == StepState.FILL  -> set valve1 := true unless stopped
    action def Set_Valve2_On_Transfer_State_Unless_Stopped;
    // seq == StepState.TRANSFER  -> set valve2 := true unless stopped
    action def Set_Valve3_On_Drain_State_Unless_Stopped;
    // seq == StepState.DRAIN  -> set valve3 := true unless stopped
    action def Close_VXS24_On_Power_Loss;
    // actuator power < energized threshold / loss of electrical power 24 VDC supply present -> return to closed position VXS-24 valve actuator
    action def Open_VXS24_On_24VDC_Command;
    // actuator command voltage == 24.0 VDC energized -> open valve VXS-24 valve
    action def Close_All_Valves_On_STOP_Command_Alt;
    // command == STOP  -> close all three valves
    action def Begin_Or_Resume_Automatic_Operation_On_START;
    // command == START  -> begin or resume automatic operation
    action def Begin_T1_Fill_On_START;
    // command == START  -> begin T1 fill
    action def Enter_Controlled_Shutdown_On_SHUT;
    // command == SHUT  -> enter controlled shutdown
    action def Inhibit_V1_On_SHUT;
    // command == SHUT  -> inhibit V1
    action def Command_V2_V3_Open_Together_On_SHUT;
    // command == SHUT  -> command open V2 and V3 together
    action def Set_Controller_State_On_cmd_start;
    // cmd_start == 1.0  -> state_change controller_state
    action def Set_Controller_State_On_cmd_stop;
    // cmd_stop == 1.0  -> state_change controller_state
    action def Set_Controller_State_On_cmd_shut;
    // cmd_shut == 1.0  -> state_change controller_state
}
