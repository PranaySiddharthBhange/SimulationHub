package Behaviors {
    action def initiate_automatic_operation;
    // START command in initial condition == true  -> initiate automatic operation sequence controller / tankController
    action def close_V1_at_T1_high;
    // Tank 1 level >= 0.78 m -> close V1 (inlet valve to Tank 1)
    action def close_V2_at_T1_low;
    // Tank 1 level <= 0.05 m -> close V2 (transfer valve Tank 1 to Tank 2)
    action def close_V3_at_T2_low;
    // Tank 2 level <= 0.05 m -> close V3 (drain valve for Tank 2)
    action def close_all_valves_and_suspend_automatic_operation;
    // STOP command == true  -> close all and suspend automatic operation V1, V2, V3 / sequence controller
    action def open_V2_V3_and_inhibit_V1_on_SHUT;
    // SHUT command == true  -> open and inhibit V2, V3 open; V1 inhibited
    action def start_automatic_fill_transfer_drain_sequence;
    // controller process state RANGE idle or paused  -> start automatic fill-transfer-drain sequence controller
    action def close_V1_at_T1_high_080m;
    // Tank 1 level >= 0.8 m -> close V1 / XV-101
    action def close_V1_at_T1_high_078m;
    // Tank 1 level >= 0.78 m -> close V1 / XV-101
    action def close_V2_at_T1_low_005m;
    // Tank 1 level <= 0.05 m -> stop transfer / close V2 V2 / XV-102
    action def close_V3_at_T2_low_005m;
    // Tank 2 level <= 0.05 m -> stop drain / close V3 V3 / XV-103
    action def complete_shutdown_when_both_tanks_low;
    // shutdown draining completion condition RANGE Tank 1 and Tank 2 both at or below low-level setpoints  -> close V2 and V3 and enter completed shutdown / idle configuration
    action def open_V2_after_T1_high_delay_12s;
    // time since Tank 1 high-level reached >= 12.0 s -> open V2 / XV-102
    action def open_V3_after_T1_low_delay_12s;
    // time since Tank 1 low-level reached >= 12.0 s -> open V3 / XV-103
    action def restart_cycle_after_T2_low_delay_8s;
    // time since Tank 2 low-level reached >= 8.0 s -> return to Tank 1 filling operation / start next cycle controller
    action def freeze_wait_timer_on_STOP;
    // STOP command received during wait state == true  -> freeze wait timer controller wait timer
    action def ignore_START_while_running;
    // START command received while already running == true  -> ignore command controller
    action def ignore_STOP_during_SHUT_mode;
    // STOP command received during SHUT mode == true  -> ignore command until shutdown complete controller
    action def ignore_START_during_SHUT_mode;
    // START command received during SHUT mode == true  -> ignore command until shutdown complete controller
    action def move_all_process_valves_to_closed_on_power_loss;
    // power loss == true  -> move to closed position all process valves
    action def prioritize_SHUT_over_STOP_over_START;
    // command priority RANGE SHUT > STOP > START  -> prioritize commands controller command arbitration
    action def forbid_V1_open_when_V2_open_in_normal_auto;
    // V2 open and normal automatic operation == true  -> prevent simultaneous opening V1
    action def prevent_V2_V3_simultaneous_open_in_normal_auto;
    // normal automatic operation == true  -> keep V2 and V3 not simultaneously open controller interlock for XV-102 and XV-103
    action def allow_V2_V3_simultaneous_open_in_SHUT_mode;
    // SHUT mode == true  -> allow simultaneous opening V2 and V3
    action def latch_command_edges_for_PLC_inputs;
    // momentary START, STOP, SHUT command edge RANGE rising edge  -> latch/interpret command event PLC-101 controller inputs
    action def control_tank_valves_from_level_logic;
    // level1 and level2 RANGE start/stop/shut control logic not specified  -> control tankController -> valves 1/2/3
    action def enter_SHUTDOWN_on_SHUT_command_edge;
    // command edge == SHUT  -> enter state SHUTDOWN
    action def enter_PAUSED_on_STOP_command;
    // command == STOP  -> enter state PAUSED
    action def enter_FILL_T1_on_START_command;
    // command == START  -> enter state FILL_T1
    action def restore_stored_interrupted_state_on_START;
    // command == START  -> restore state stored interrupted state from PAUSED
    action def enter_TRANSFER_T1_T2_on_timer_expired;
    // timer == expired  -> enter state TRANSFER_T1_T2
    action def enter_DRAIN_T2_on_timer_expired;
    // timer == expired  -> enter state DRAIN_T2
    action def enter_FILL_T1_on_timer_expired;
    // timer == expired  -> enter state FILL_T1
    action def enter_WAIT_AFTER_FILL_on_LT_101_high;
    // LT-101 level >= T1_High m -> enter state WAIT_AFTER_FILL
    action def enter_WAIT_AFTER_TRANSFER_on_LT_101_low;
    // LT-101 level <= T1_Low m -> enter state WAIT_AFTER_TRANSFER
    action def enter_WAIT_AFTER_DRAIN_on_LT_102_low;
    // LT-102 level <= T2_Low m -> enter state WAIT_AFTER_DRAIN
    action def enter_IDLE_on_both_levels_low;
    // LT-101 level AND LT-102 level RANGE <= T1_Low AND <= T2_Low m -> enter state IDLE
    action def set_all_valve_outputs_false_on_controller_power_loss;
    // controller power loss == true  -> set outputs all valve outputs false
    action def forbid_V1_V2_simultaneous_open;
    // V1 and V2 simultaneous open == true  -> forbid V1 and V2 open simultaneously
    action def forbid_V2_V3_simultaneous_open_in_normal_auto;
    // V2 and V3 simultaneous open during normal automatic operation == true  -> forbid V2 and V3 open simultaneously
    action def retain_remaining_delay_on_STOP;
    // STOP in WAIT_AFTER_FILL, WAIT_AFTER_TRANSFER, or WAIT_AFTER_DRAIN == true  -> retain remaining delay
    action def resume_with_retained_delay_on_START;
    // START after STOP in WAIT_AFTER_FILL, WAIT_AFTER_TRANSFER, or WAIT_AFTER_DRAIN == true  -> resume with retained remaining delay
    action def freeze_remaining_delay_on_STOP;
    // STOP received during any delay == true  -> freeze remaining delay
    action def ignore_START_while_sequence_running;
    // START received while automatic sequence is already running == true  -> ignore START command
    action def ignore_START_STOP_during_active_SHUT;
    // START or STOP received during active SHUT == true  -> ignore START and STOP commands
    action def complete_shutdown_when_LT_101_LT_102_low;
    // LT-101 and LT-102 at or below their low-level setpoints RANGE at or below low-level setpoints  -> complete shutdown sequence
    action def close_all_valves_and_reset_to_IDLE_on_shutdown_complete;
    // shutdown completion == true  -> close all valves and reset sequence context to IDLE
    action def prohibit_V1_V2_open_command_combination;
    // V1 and V2 commanded open together == true  -> prohibit open command combination V1+V2
    action def prohibit_V2_V3_open_command_combination_in_normal_auto;
    // V2 and V3 commanded open together in normal auto operation == true  -> prohibit open command combination V2+V3 in normal auto operation
    action def dead_time_after_T1_low_before_resuming_control;
    // time after T1 low >= 12.0 s -> wait/dead-time before resuming control T1 fill/transfer control
    action def resume_fill_after_T2_low_delay_8s;
    // tank 2 low >= 8.0 s -> resume fill after drain T2 fill control
    action def stop_and_close_V1_at_high_target;
    // tank level == high target 0.80 m -> stop/close valve V1 / XV-101
    action def turn_off_all_valve_lamps_on_stop;
    // stop command == active  -> turn off lamps / stop valve actuation all valve lamps
    action def enable_simultaneous_transfer_and_drain_on_shut;
    // shut command == active  -> enable simultaneous transfer and drain transfer + drain lamps
    action def set_T1_high_limit_at_080m;
    // T1 high level >= 0.8 m -> set effective high limit / control threshold T1 high limit
    action def open_drain_valve_after_T1_low_delay_12s;
    // time after T1 reaches low level >= 12.0 s -> open drain valve
    action def start_next_fill_after_T2_low_delay_8s;
    // time after T2 reaches low level >= 8.0 s -> start next fill
    action def maintain_V2_V3_open_in_SHUT;
    // control state == SHUT  -> maintain command open V2 and V3
    action def release_V2_V3_commanded_open_when_low_conditions_met;
    // low-level conditions RANGE both satisfied  -> allow SHUT to end / release commanded-open state V2 and V3
    action def ignore_START_during_SHUT;
    // command/state == START during SHUT  -> ignore START command
    action def set_stopped_false_on_startCmd_edge;
    // startCmd edge == 1.0  -> set boolean false stopped
    action def set_stopped_true_on_stopCmd_edge;
    // stopCmd edge == 1.0  -> set boolean true stopped
    action def set_valve1_true_in_FILL_when_not_stopped;
    // seq == StepState.FILL  -> assign boolean true when not stopped valve1
    action def set_valve2_true_in_TRANSFER_when_not_stopped;
    // seq == StepState.TRANSFER  -> assign boolean true when not stopped valve2
    action def set_valve3_true_in_DRAIN_when_not_stopped;
    // seq == StepState.DRAIN  -> assign boolean true when not stopped valve3
    action def return_valve_to_closed_position_on_power_loss;
    // Electrical power / actuator energy availability < loss of power  -> return_to_closed_position VXS-24 valve actuator/valve
    action def open_VXS_24_valve_on_24VDC_command;
    // Actuator command voltage == 24.0 VDC energized -> open_valve VXS-24 valve
    action def begin_or_resume_automatic_operation_on_START;
    // command == START  -> begin_or_resume_automatic_operation PLC-101 sequence behavior
    action def close_all_valves_and_hold_sequence_context_on_STOP;
    // command == STOP  -> close all three valves and hold sequence context
    action def resume_state_interrupted_at_220s_on_START;
    // command == START  -> resume the state interrupted at 220 s
    action def close_all_valves_and_hold_sequence_context_on_STOP_repeat;
    // command == STOP  -> close all valves and hold sequence context
    action def enter_controlled_shutdown_inhibit_V1_and_open_V2_V3_until_low;
    // command == SHUT  -> enter controlled shutdown; inhibit V1; command V2 and V3 open until both tanks are at low level
}
