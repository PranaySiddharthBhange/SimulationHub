package Requirements {
    requirement def Tank1_initial_level_req {
        doc /* Tank 1 initial level.level == 0.05 m */
        attribute level : ScalarValues::Real;
    }
    requirement def Tank2_initial_level_req {
        doc /* Tank 2 initial level.level == 0.05 m */
        attribute level : ScalarValues::Real;
    }
    requirement def Tank1_high_limit_req {
        doc /* Tank 1 high limit.level high limit == 0.78 m */
        attribute level_high_limit : ScalarValues::Real;
    }
    requirement def Tank1_low_limit_req {
        doc /* Tank 1 low limit.level low limit == 0.05 m */
        attribute level_low_limit : ScalarValues::Real;
    }
    requirement def Tank2_low_limit_req {
        doc /* Tank 2 low limit.level low limit == 0.05 m */
        attribute level_low_limit : ScalarValues::Real;
    }
    requirement def WaitAfterT1High_delay_req {
        doc /* Wait after T1 high.delay == 10.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def WaitAfterT1Low_delay_req {
        doc /* Wait after T1 low.delay == 10.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def WaitAfterT2Low_delay_req {
        doc /* Wait after T2 low.delay == 10.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def Controller_start_condition_req {
        doc /* controller.automatic fill-transfer-drain sequence start condition == valid START command when process is idle or paused */
        attribute automatic_fill_transfer_drain_sequence_start_condition : ScalarValues::Real;
    }
    requirement def V1_fill_open_cmd_req {
        doc /* inlet valve V1.commanded state during automatic fill == open */
        attribute commanded_state_during_automatic_fill : ScalarValues::Real;
    }
    requirement def T1_high_setpoint_req {
        doc /* Tank 1 high-level setpoint.value == 0.8 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T1_low_setpoint_req {
        doc /* Tank 1 low-level setpoint.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T2_low_setpoint_req {
        doc /* Tank 2 low-level setpoint.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def WaitAfterT1High_beforeV2_req {
        doc /* controller.wait time after Tank 1 reaches high level before opening V2 == 10.0 s */
        attribute wait_time_after_Tank_1_reaches_high_level_before_opening_V2 : ScalarValues::Real;
    }
    requirement def WaitAfterT1Low_beforeV3_req {
        doc /* controller.wait time after Tank 1 reaches low level before opening V3 == 12.0 s */
        attribute wait_time_after_Tank_1_reaches_low_level_before_opening_V3 : ScalarValues::Real;
    }
    requirement def WaitAfterT2Low_returnFill_req {
        doc /* controller.wait time after Tank 2 reaches low level before returning to Tank 1 filling == 8.0 s */
        attribute wait_time_after_Tank_2_reaches_low_level_before_returning_to_Tank_1_filling : ScalarValues::Real;
    }
    requirement def Controller_state_after_stop_req {
        doc /* controller.state after STOP == paused */
        attribute state_after_STOP : ScalarValues::Real;
    }
    requirement def Controller_resume_after_stop_req {
        doc /* controller.state after START following STOP == continue sequence from point STOP was accepted */
        attribute state_after_START_following_STOP : ScalarValues::Real;
    }
    requirement def Controller_shutdown_latch_req {
        doc /* controller.shutdown mode == latched */
        attribute shutdown_mode : ScalarValues::Real;
    }
    requirement def Shut_over_Stop_priority_req {
        doc /* command priority.SHUT over STOP == higher */
        attribute SHUT_over_STOP : ScalarValues::Real;
    }
    requirement def Stop_over_Start_priority_req {
        doc /* command priority.STOP over START == higher */
        attribute STOP_over_START : ScalarValues::Real;
    }
    requirement def V1_not_open_with_V2_req {
        doc /* valve V1.open while V2 open == never permitted */
        attribute open_while_V2_open : ScalarValues::Real;
    }
    requirement def V2_V3_no_simul_open_normal_req {
        doc /* valves V2 and V3.simultaneous open state during normal automatic operation == not permitted */
        attribute simultaneous_open_state_during_normal_automatic_operation : ScalarValues::Real;
    }
    requirement def V2_V3_simul_open_allowed_req {
        doc /* valves V2 and V3.simultaneous open state == permitted */
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    requirement def Simulation_duration_req {
        doc /* 0.0 RANGE controller.simulation run duration RANGE 900.0 s */
        attribute simulation_run_duration : ScalarValues::Real;
    }
    requirement def Start_event_time_20s_req {
        doc /* controller.event time START == 20.0 s */
        attribute event_time_START : ScalarValues::Real;
    }
    requirement def Stop_event_time_220s_req {
        doc /* controller.event time STOP == 220.0 s */
        attribute event_time_STOP : ScalarValues::Real;
    }
    requirement def Start_event_time_280s_req {
        doc /* controller.event time START == 280.0 s */
        attribute event_time_START : ScalarValues::Real;
    }
    requirement def Stop_event_time_650s_req {
        doc /* controller.event time STOP == 650.0 s */
        attribute event_time_STOP : ScalarValues::Real;
    }
    requirement def Shut_event_time_700s_req {
        doc /* controller.event time SHUT == 700.0 s */
        attribute event_time_SHUT : ScalarValues::Real;
    }
    requirement def Level_units_metres_req {
        doc /* level values.internal representation units == metres */
        attribute internal_representation_units : ScalarValues::Real;
    }
    requirement def Level_nominal_range_req {
        doc /* 0.0 RANGE level values.nominal valid range RANGE 1.0 m */
        attribute nominal_valid_range : ScalarValues::Real;
    }
    requirement def ValveCommands_boolean_open_closed_req {
        doc /* valve commands.representation == Boolean open/closed commands */
        attribute representation : ScalarValues::Real;
    }
    requirement def Tank1_initial_level_req2 {
        doc /* Tank 1.initial level == 0.05 m */
        attribute initial_level : ScalarValues::Real;
    }
    requirement def Tank2_initial_level_req2 {
        doc /* Tank 2.initial level == 0.05 m */
        attribute initial_level : ScalarValues::Real;
    }
    requirement def Controller_scan_time_req {
        doc /* controller.scan time == 0.1 s */
        attribute scan_time : ScalarValues::Real;
    }
    requirement def XV101_nominal_flow_req {
        doc /* XV-101.nominal flow == 0.006 m^3/s */
        attribute nominal_flow : ScalarValues::Real;
    }
    requirement def XV102_nominal_flow_req {
        doc /* XV-102.nominal flow == 0.0045 m^3/s */
        attribute nominal_flow : ScalarValues::Real;
    }
    requirement def XV103_nominal_flow_req {
        doc /* XV-103.nominal flow == 0.005 m^3/s */
        attribute nominal_flow : ScalarValues::Real;
    }
    requirement def LT101_engineering_range_req {
        doc /* 0.0 RANGE LT-101.engineering range RANGE 1.0 m */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def LT102_engineering_range_req {
        doc /* 0.0 RANGE LT-102.engineering range RANGE 1.0 m */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def PB_START_signal_type_req {
        doc /* PB-START.signal type == Boolean / edge */
        attribute signal_type : ScalarValues::Real;
    }
    requirement def PB_STOP_signal_type_req {
        doc /* PB-STOP.signal type == Boolean / edge */
        attribute signal_type : ScalarValues::Real;
    }
    requirement def PB_SHUT_signal_type_req {
        doc /* PB-SHUT.signal type == Boolean / edge */
        attribute signal_type : ScalarValues::Real;
    }
    requirement def DO101_signal_type_req {
        doc /* DO-101.signal type == Boolean */
        attribute signal_type : ScalarValues::Real;
    }
    requirement def DO102_signal_type_req {
        doc /* DO-102.signal type == Boolean */
        attribute signal_type : ScalarValues::Real;
    }
    requirement def DO103_signal_type_req {
        doc /* DO-103.signal type == Boolean */
        attribute signal_type : ScalarValues::Real;
    }
    requirement def tank1_level_default_req {
        doc /* tank1.level.default value == 0.05 */
        attribute default_value : ScalarValues::Real;
    }
    requirement def tank2_level_default_req {
        doc /* tank2.level.default value == 0.05 */
        attribute default_value : ScalarValues::Real;
    }
    requirement def Shut_command_priority_highest_req {
        doc /* controller command priority.SHUT command priority rank == highest */
        attribute SHUT_command_priority_rank : ScalarValues::Real;
    }
    requirement def Stop_command_priority_next_req {
        doc /* controller command priority.STOP command priority rank == next highest after SHUT */
        attribute STOP_command_priority_rank : ScalarValues::Real;
    }
    requirement def Start_command_priority_lowest_req {
        doc /* controller command priority.START command priority rank == lowest */
        attribute START_command_priority_rank : ScalarValues::Real;
    }
    requirement def Start_accepted_after_shutdown_req {
        doc /* controller.command accepted after shutdown completion == START */
        attribute command_accepted_after_shutdown_completion : ScalarValues::Real;
    }
    requirement def Timer_remaining_retained_on_stop_req {
        doc /* controller timer.remaining delay retained on STOP in wait states == retained */
        attribute remaining_delay_retained_on_STOP_in_wait_states : ScalarValues::Real;
    }
    requirement def Timer_resume_remaining_delay_req {
        doc /* controller timer.resume delay behavior after START == resume with remaining delay */
        attribute resume_delay_behavior_after_START : ScalarValues::Real;
    }
    requirement def V1_V2_no_simul_open_req {
        doc /* V1 and V2 valves.simultaneous open state == not allowed */
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    requirement def V2_V3_no_simul_open_normal_req2 {
        doc /* V2 and V3 valves.simultaneous open state during normal automatic operation == not allowed */
        attribute simultaneous_open_state_during_normal_automatic_operation : ScalarValues::Real;
    }
    requirement def V2_V3_simul_open_allowed_req2 {
        doc /* V2 and V3 valves.simultaneous open state == allowed */
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    requirement def Controller_outputs_false_on_power_loss_req {
        doc /* controller output commands.state on controller power loss == false */
        attribute state_on_controller_power_loss : ScalarValues::Real;
    }
    requirement def Level_threshold_equality_inclusive_req {
        doc /* level threshold comparisons.comparison includes equality == >= high and <= low */
        attribute comparison_includes_equality : ScalarValues::Real;
    }
    requirement def FILL_T1_valve_pattern_req {
        doc /* FILL_T1.valve command pattern (V1,V2,V3) == 1,0,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_FILL_valve_pattern_req {
        doc /* WAIT_AFTER_FILL.valve command pattern (V1,V2,V3) == 0,0,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def TRANSFER_T1_T2_valve_pattern_req {
        doc /* TRANSFER_T1_T2.valve command pattern (V1,V2,V3) == 0,1,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_TRANSFER_valve_pattern_req {
        doc /* WAIT_AFTER_TRANSFER.valve command pattern (V1,V2,V3) == 0,0,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def DRAIN_T2_valve_pattern_req2 {
        doc /* DRAIN_T2.valve command pattern (V1,V2,V3) == 0,0,1 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_DRAIN_valve_pattern_req {
        doc /* WAIT_AFTER_DRAIN.valve command pattern (V1,V2,V3) == 0,0,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def PAUSED_valve_pattern_req {
        doc /* PAUSED.valve command pattern (V1,V2,V3) == 0,0,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def SHUTDOWN_valve_pattern_req {
        doc /* SHUTDOWN.valve command pattern (V1,V2,V3) == 0,1,1 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def IDLE_valve_pattern_req {
        doc /* IDLE.valve command pattern (V1,V2,V3) == 0,0,0 */
        attribute valve_command_pattern_V1_V2_V3 : ScalarValues::Real;
    }
    requirement def FILL_T1_transition_guard_req {
        doc /* FILL_T1.transition guard == LT-101 >= T1_High */
        attribute transition_guard : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_FILL_transition_guard_req {
        doc /* WAIT_AFTER_FILL.transition guard == timer expired */
        attribute transition_guard : ScalarValues::Real;
    }
    requirement def TRANSFER_T1_T2_transition_guard_req {
        doc /* TRANSFER_T1_T2.transition guard == LT-101 <= T1_Low */
        attribute transition_guard : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_TRANSFER_transition_guard_req {
        doc /* WAIT_AFTER_TRANSFER.transition guard == timer expired */
        attribute transition_guard : ScalarValues::Real;
    }
    requirement def DRAIN_T2_transition_guard_req {
        doc /* DRAIN_T2.transition guard == LT-102 <= T2_Low */
        attribute transition_guard : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_DRAIN_transition_guard_req {
        doc /* WAIT_AFTER_DRAIN.transition guard == timer expired */
        attribute transition_guard : ScalarValues::Real;
    }
    requirement def Paused_restart_source_req {
        doc /* PAUSED.restart transition source == stored state */
        attribute restart_transition_source : ScalarValues::Real;
    }
    requirement def Shutdown_exit_condition_req {
        doc /* SHUTDOWN.exit condition == LT-101 <= T1_Low AND LT-102 <= T2_Low */
        attribute exit_condition : ScalarValues::Real;
    }
    requirement def Command_precedence_order_req {
        doc /* command precedence.priority order == SHUT > STOP > START */
        attribute priority_order : ScalarValues::Real;
    }
    requirement def Stop_command_valves_closed_req {
        doc /* STOP command.valve state after STOP == closed */
        attribute valve_state_after_STOP : ScalarValues::Real;
    }
    requirement def Stop_interrupted_state_stored_req {
        doc /* STOP command.interrupted state handling == stored */
        attribute interrupted_state_handling : ScalarValues::Real;
    }
    requirement def Wait_timer_frozen_on_stop_req {
        doc /* automatic sequence delay timer.remaining delay handling after STOP == frozen */
        attribute remaining_delay_handling_after_STOP : ScalarValues::Real;
    }
    requirement def Start_timer_resume_remaining_req {
        doc /* START command.delay timer resumption behavior == resume remaining delay */
        attribute delay_timer_resumption_behavior : ScalarValues::Real;
    }
    requirement def Start_ignored_while_running_req {
        doc /* START command.behavior while automatic sequence is running == ignored */
        attribute behavior_while_automatic_sequence_is_running : ScalarValues::Real;
    }
    requirement def Start_ignored_during_shut_req {
        doc /* START command.behavior during active SHUT == ignored */
        attribute behavior_during_active_SHUT : ScalarValues::Real;
    }
    requirement def Stop_ignored_during_shut_req {
        doc /* STOP command.behavior during active SHUT == ignored */
        attribute behavior_during_active_SHUT : ScalarValues::Real;
    }
    requirement def Shut_lt101_completion_req {
        doc /* SHUT sequence.completion criterion for LT-101 <= None */
        attribute completion_criterion_for_LT_101 : ScalarValues::Real;
    }
    requirement def Shut_lt102_completion_req {
        doc /* SHUT sequence.completion criterion for LT-102 <= None */
        attribute completion_criterion_for_LT_102 : ScalarValues::Real;
    }
    requirement def Shutdown_completion_valves_closed_req {
        doc /* shutdown completion.valve state == closed */
        attribute valve_state : ScalarValues::Real;
    }
    requirement def Sequence_state_after_shutdown_req {
        doc /* sequence context.state after shutdown completion == IDLE */
        attribute state_after_shutdown_completion : ScalarValues::Real;
    }
    requirement def V1_V2_commanded_open_prohibited_req {
        doc /* V1 and V2.commanded open together == prohibited */
        attribute commanded_open_together : ScalarValues::Real;
    }
    requirement def V2_V3_commanded_open_prohibited_req {
        doc /* V2 and V3.commanded open together == prohibited */
        attribute commanded_open_together : ScalarValues::Real;
    }
    requirement def V2_V3_commanded_open_allowed_req {
        doc /* V2 and V3.commanded open together == allowed */
        attribute commanded_open_together : ScalarValues::Real;
    }
    requirement def T1_high_threshold_req {
        doc /* T1 high.threshold == 0.8 m */
        attribute threshold : ScalarValues::Real;
    }
    requirement def Post_transfer_delay_req {
        doc /* post-transfer delay.duration == 12.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def Inter_cycle_delay_after_T2_low_req {
        doc /* inter-cycle delay after Tank 2 low.duration == 8.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def V1_drop_out_target_req {
        doc /* Observed target for V1 drop-out.value at high target == 0.8 m */
        attribute value_at_high_target : ScalarValues::Real;
    }
    requirement def Stop_event_kills_valve_lamps_req {
        doc /* Stop event.time that kills all valve lamps == 220.0 s */
        attribute time_that_kills_all_valve_lamps : ScalarValues::Real;
    }
    requirement def Start_event_resume_transfer_req {
        doc /* Start event.time that picks transfer back up == 280.0 s */
        attribute time_that_picks_transfer_back_up : ScalarValues::Real;
    }
    requirement def Control_dead_time_after_T1_low_req {
        doc /* Control dead time after T1 low.duration == 12.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def Dead_time_after_T2_low_req {
        doc /* Dead time after T2 low.duration == 8.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def Stop_event_interrupts_second_fill_req {
        doc /* Stop event.time that interrupts second fill == 650.0 s */
        attribute time_that_interrupts_second_fill : ScalarValues::Real;
    }
    requirement def Shut_event_controlled_drain_req {
        doc /* Shut event.time of controlled drain shutdown == 700.0 s */
        attribute time_of_controlled_drain_shutdown : ScalarValues::Real;
    }
    requirement def Shutdown_idle_period_end_req {
        doc /* System idle period after shutdown.end time of idle period == 900.0 s */
        attribute end_time_of_idle_period : ScalarValues::Real;
    }
    requirement def Initial_both_tank_displays_req {
        doc /* Initial both tank displays.level == 0.05 m */
        attribute level : ScalarValues::Real;
    }
    requirement def T1_high_limit_effective_req {
        doc /* T1 high limit.effective value == 0.8 m */
        attribute effective_value : ScalarValues::Real;
    }
    requirement def Delay_after_T1_low_before_drain_req {
        doc /* Delay after T1 reaches low level before opening the drain valve.delay == 12.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def Delay_after_T2_low_before_next_fill_req {
        doc /* Delay after T2 reaches low level before the next fill starts.delay == 8.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def Shut_over_Stop_priority_relation_req {
        doc /* Control priority of SHUT relative to STOP.priority relation == SHUT higher than STOP */
        attribute priority_relation : ScalarValues::Real;
    }
    requirement def V2_open_during_shut_req {
        doc /* V2 commanded state during SHUT until both low-level conditions are satisfied.commanded state == open */
        attribute commanded_state : ScalarValues::Real;
    }
    requirement def V3_open_during_shut_req {
        doc /* V3 commanded state during SHUT until both low-level conditions are satisfied.commanded state == open */
        attribute commanded_state : ScalarValues::Real;
    }
    requirement def Start_ignored_during_shut_behavior_req {
        doc /* START behavior during SHUT.effect == ignored */
        attribute effect : ScalarValues::Real;
    }
    requirement def Stopped_state_after_start_edge_req {
        doc /* stopped.state after startCmd edge == 0.0 */
        attribute state_after_startCmd_edge : ScalarValues::Real;
    }
    requirement def Stopped_state_after_stop_edge_req {
        doc /* stopped.state after stopCmd edge == 1.0 */
        attribute state_after_stopCmd_edge : ScalarValues::Real;
    }
    requirement def Valve1_boolean_state_expr_req {
        doc /* valve1.boolean state == (seq == StepState.FILL) and not stopped */
        attribute boolean_state : ScalarValues::Real;
    }
    requirement def Valve2_boolean_state_expr_req {
        doc /* valve2.boolean state == (seq == StepState.TRANSFER) and not stopped */
        attribute boolean_state : ScalarValues::Real;
    }
    requirement def Valve3_boolean_state_expr_req {
        doc /* valve3.boolean state == (seq == StepState.DRAIN) and not stopped */
        attribute boolean_state : ScalarValues::Real;
    }
    requirement def XV101_feed_to_tank1_service_req {
        doc /* VXS-24 valve for project tag XV-101.project service == Feed to Tank 1 */
        attribute project_service : ScalarValues::Real;
    }
    requirement def XV102_tank1_transfer_service_req {
        doc /* VXS-24 valve for project tag XV-102.project service == Tank 1 transfer */
        attribute project_service : ScalarValues::Real;
    }
    requirement def XV103_tank2_drain_service_req {
        doc /* VXS-24 valve for project tag XV-103.project service == Tank 2 drain */
        attribute project_service : ScalarValues::Real;
    }
    requirement def XV101_deenergized_closed_req {
        doc /* VXS-24 valve for project tag XV-101.de-energized position == Closed */
        attribute de_energized_position : ScalarValues::Real;
    }
    requirement def XV102_deenergized_closed_req {
        doc /* VXS-24 valve for project tag XV-102.de-energized position == Closed */
        attribute de_energized_position : ScalarValues::Real;
    }
    requirement def XV103_deenergized_closed_req {
        doc /* VXS-24 valve for project tag XV-103.de-energized position == Closed */
        attribute de_energized_position : ScalarValues::Real;
    }
    requirement def XV101_nominal_demo_flow_req {
        doc /* VXS-24 valve for project tag XV-101.nominal demo flow coefficient equivalent == 0.006 m^3/s */
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    requirement def XV102_nominal_demo_flow_req {
        doc /* VXS-24 valve for project tag XV-102.nominal demo flow coefficient equivalent == 0.0045 m^3/s */
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    requirement def XV103_nominal_demo_flow_req {
        doc /* VXS-24 valve for project tag XV-103.nominal demo flow coefficient equivalent == 0.005 m^3/s */
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    requirement def XV101_full_open_stroke_req {
        doc /* VXS-24 valve for project tag XV-101.full open stroke time == 0.8 s */
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    requirement def XV102_full_open_stroke_req {
        doc /* VXS-24 valve for project tag XV-102.full open stroke time == 0.8 s */
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    requirement def XV103_full_open_stroke_req {
        doc /* VXS-24 valve for project tag XV-103.full open stroke time == 0.8 s */
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    requirement def XV101_full_close_stroke_req {
        doc /* VXS-24 valve for project tag XV-101.full close stroke time == 0.6 s */
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    requirement def XV102_full_close_stroke_req {
        doc /* VXS-24 valve for project tag XV-102.full close stroke time == 0.6 s */
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    requirement def XV103_full_close_stroke_req {
        doc /* VXS-24 valve for project tag XV-103.full close stroke time == 0.6 s */
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    requirement def XV101_energized_open_relation_req {
        doc /* VXS-24 valve for project tag XV-101.command relationship == 24 VDC energized=open */
        attribute command_relationship : ScalarValues::Real;
    }
    requirement def XV102_energized_open_relation_req {
        doc /* VXS-24 valve for project tag XV-102.command relationship == 24 VDC energized=open */
        attribute command_relationship : ScalarValues::Real;
    }
    requirement def XV103_energized_open_relation_req {
        doc /* VXS-24 valve for project tag XV-103.command relationship == 24 VDC energized=open */
        attribute command_relationship : ScalarValues::Real;
    }
    requirement def T1_level_initial_value_req {
        doc /* T1 level.initial value == 0.05 m */
        attribute initial_value : ScalarValues::Real;
    }
    requirement def T2_level_initial_value_req {
        doc /* T2 level.initial value == 0.05 m */
        attribute initial_value : ScalarValues::Real;
    }
    requirement def Simulation_duration_900s_req {
        doc /* simulation.duration == 900.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def Logging_interval_1s_req {
        doc /* logging.interval == 1.0 s */
        attribute interval : ScalarValues::Real;
    }
    requirement def T1_effective_high_setpoint_req {
        doc /* effective high-level setpoint for T1.value == 0.8 m */
        attribute value : ScalarValues::Real;
    }
    requirement def Stop_interval_valves_closed_req {
        doc /* STOP interval from 220 s to 280 s.all valves closed == closed */
        attribute all_valves_closed : ScalarValues::Real;
    }
    requirement def Start_resume_interrupted_transfer_req {
        doc /* START at 280 s.controller behavior == resume the interrupted transfer */
        attribute controller_behavior : ScalarValues::Real;
    }
    requirement def Inter_cycle_delay_value_req {
        doc /* inter-cycle delay.value == 8.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def Stop_interval_650_700_closed_req {
        doc /* STOP interval from 650 s to 700 s.all valves closed == closed */
        attribute all_valves_closed : ScalarValues::Real;
    }
    requirement def V1_state_at_700s_req {
        doc /* V1.state at 700 s == closed */
        attribute state_at_700_s : ScalarValues::Real;
    }
    requirement def V2_V3_state_at_700s_req {
        doc /* V2 and V3.state at 700 s == open */
        attribute state_at_700_s : ScalarValues::Real;
    }
    requirement def Controller_state_after_shutdown_drain_req {
        doc /* controller.state after shutdown drain completion == IDLE */
        attribute state_after_shutdown_drain_completion : ScalarValues::Real;
    }
    requirement def Valves_state_after_shutdown_drain_req {
        doc /* valves.state after shutdown drain completion == closed */
        attribute state_after_shutdown_drain_completion : ScalarValues::Real;
    }
    requirement def State_boundary_tolerance_req {
        doc /* controller.tolerance for state-boundary comparisons == 2.0 s */
        attribute tolerance_for_state_boundary_comparisons : ScalarValues::Real;
    }
    requirement def time_s_sampling_period_req {
        doc /* time_s.sampling_period == 1.0 s */
        attribute sampling_period : ScalarValues::Real;
    }
    requirement def time_s_range_req {
        doc /* 0.0 RANGE time_s.range RANGE 900.0 s */
        attribute range : ScalarValues::Real;
    }
    requirement def cmd_start_value_range_req {
        doc /* 0.0 RANGE cmd_start.value range RANGE 1.0 */
        attribute value_range : ScalarValues::Real;
    }
    requirement def cmd_stop_value_range_req {
        doc /* 0.0 RANGE cmd_stop.value range RANGE 1.0 */
        attribute value_range : ScalarValues::Real;
    }
    requirement def cmd_shut_value_range_req {
        doc /* 0.0 RANGE cmd_shut.value range RANGE 1.0 */
        attribute value_range : ScalarValues::Real;
    }
    requirement def tank1_level_m_range_req {
        doc /* 0.05 RANGE tank1_level_m.range RANGE 0.8 m */
        attribute range : ScalarValues::Real;
    }
    requirement def tank2_level_m_range_req {
        doc /* 0.05 RANGE tank2_level_m.range RANGE 0.69286 m */
        attribute range : ScalarValues::Real;
    }
    requirement def valve1_open_value_range_req {
        doc /* 0.0 RANGE valve1_open.value range RANGE 1.0 */
        attribute value_range : ScalarValues::Real;
    }
    requirement def valve2_open_value_range_req {
        doc /* 0.0 RANGE valve2_open.value range RANGE 1.0 */
        attribute value_range : ScalarValues::Real;
    }
    requirement def valve3_open_value_range_req {
        doc /* 0.0 RANGE valve3_open.value range RANGE 1.0 */
        attribute value_range : ScalarValues::Real;
    }
    requirement def wait_remaining_s_range_req {
        doc /* 0.0 RANGE wait_remaining_s.range RANGE 12.0 s */
        attribute range : ScalarValues::Real;
    }
}
