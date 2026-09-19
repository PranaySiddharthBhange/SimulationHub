package Constraints {
    constraint def Tank1_initial_level_005m_constraint {
        attribute initial_level : ScalarValues::Real;
    }
    constraint def Tank2_initial_level_005m_constraint {
        attribute initial_level : ScalarValues::Real;
    }
    constraint def Tank1_high_limit_078m_constraint {
        attribute high_limit : ScalarValues::Real;
    }
    constraint def Tank1_low_limit_005m_constraint {
        attribute low_limit : ScalarValues::Real;
    }
    constraint def Tank2_low_limit_005m_constraint {
        attribute low_limit : ScalarValues::Real;
    }
    constraint def Wait_after_T1_high_duration_10s_constraint {
        attribute duration : ScalarValues::Real;
    }
    constraint def Wait_after_T1_low_duration_10s_constraint {
        attribute duration : ScalarValues::Real;
    }
    constraint def Wait_after_T2_low_duration_10s_constraint {
        attribute duration : ScalarValues::Real;
    }
    constraint def T1_high_level_setpoint_080m_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def T1_low_level_setpoint_005m_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def T2_low_level_setpoint_005m_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def Post_transfer_waiting_time_12s_constraint {
        attribute time : ScalarValues::Real;
    }
    constraint def Inter_cycle_wait_after_T2_low_8s_constraint {
        attribute time : ScalarValues::Real;
    }
    constraint def Controller_scan_time_01s_constraint {
        attribute time : ScalarValues::Real;
    }
    constraint def Simulation_stop_time_900s_constraint {
        attribute time : ScalarValues::Real;
    }
    constraint def Tank1_level_measurement_range_0_to_1m_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def Tank1_initial_level_005m_repeat_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def Tank2_initial_level_005m_repeat_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def Tank1_maximum_working_level_09m_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def Tank1_cross_section_area_12m2_constraint {
        attribute area : ScalarValues::Real;
    }
    constraint def Tank2_cross_section_area_14m2_constraint {
        attribute area : ScalarValues::Real;
    }
    constraint def Tank1_height_1m_constraint {
        attribute height : ScalarValues::Real;
    }
    constraint def Tank2_height_1m_constraint {
        attribute height : ScalarValues::Real;
    }
    constraint def V1_nominal_flow_0006_constraint {
        attribute flow_value : ScalarValues::Real;
    }
    constraint def V2_nominal_flow_00045_constraint {
        attribute flow_value : ScalarValues::Real;
    }
    constraint def V3_nominal_flow_0005_constraint {
        attribute flow_value : ScalarValues::Real;
    }
    constraint def tank1_level_default_005m_constraint {
        attribute default_level : ScalarValues::Real;
    }
    constraint def tank2_level_default_005m_constraint {
        attribute default_level : ScalarValues::Real;
    }
    constraint def V1_V2_simultaneous_open_status_0_constraint {
        attribute simultaneous_open_status : ScalarValues::Real;
    }
    constraint def V2_V3_simultaneous_open_status_normal_auto_0_constraint {
        attribute simultaneous_open_status_during_normal_automatic_operation : ScalarValues::Real;
    }
    constraint def V2_V3_simultaneous_open_status_SHUTDOWN_1_constraint {
        attribute simultaneous_open_status_in_SHUTDOWN : ScalarValues::Real;
    }
    constraint def LT_101_level_comparison_high_threshold_inclusive_constraint {
        attribute high_threshold_comparison_inclusion : ScalarValues::Real;
    }
    constraint def LT_101_level_comparison_low_threshold_inclusive_constraint {
        attribute low_threshold_comparison_inclusion : ScalarValues::Real;
    }
    constraint def T1_high_limit_URS_baseline_078m_constraint {
        attribute value_relative_to_URS_baseline : ScalarValues::Real;
    }
    constraint def T1_high_threshold_upper_bound_080m_constraint {
        attribute upper_bound : ScalarValues::Real;
    }
    constraint def post_transfer_delay_12s_constraint {
        attribute duration : ScalarValues::Real;
    }
    constraint def inter_cycle_delay_after_T2_low_8s_constraint {
        attribute duration : ScalarValues::Real;
    }
    constraint def T1_fill_target_080m_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def T1_low_wait_time_12s_constraint {
        attribute dead_time : ScalarValues::Real;
    }
    constraint def T2_low_to_fill_delay_8s_constraint {
        attribute dead_time : ScalarValues::Real;
    }
    constraint def T1_high_limit_effective_080m_constraint {
        attribute effective_high_limit : ScalarValues::Real;
    }
    constraint def T1_low_to_drain_valve_wait_12s_constraint {
        attribute waiting_time : ScalarValues::Real;
    }
    constraint def T2_low_to_next_fill_wait_8s_constraint {
        attribute waiting_time : ScalarValues::Real;
    }
    constraint def tank1Level_level_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def tank2Level_level_constraint {
        attribute level : ScalarValues::Real;
    }
    constraint def VXS_24_XV_101_nominal_demo_flow_0006_constraint {
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    constraint def VXS_24_XV_102_nominal_demo_flow_00045_constraint {
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    constraint def VXS_24_XV_103_nominal_demo_flow_0005_constraint {
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    constraint def VXS_24_XV_101_full_open_stroke_time_08s_constraint {
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    constraint def VXS_24_XV_102_full_open_stroke_time_08s_constraint {
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    constraint def VXS_24_XV_103_full_open_stroke_time_08s_constraint {
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    constraint def VXS_24_XV_101_full_close_stroke_time_06s_constraint {
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    constraint def VXS_24_XV_102_full_close_stroke_time_06s_constraint {
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    constraint def VXS_24_XV_103_full_close_stroke_time_06s_constraint {
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    constraint def T1_level_at_start_005m_constraint {
        attribute level_at_start : ScalarValues::Real;
    }
    constraint def T2_level_at_start_005m_constraint {
        attribute level_at_start : ScalarValues::Real;
    }
    constraint def simulation_duration_900s_constraint {
        attribute duration : ScalarValues::Real;
    }
    constraint def logging_interval_1s_constraint {
        attribute interval : ScalarValues::Real;
    }
    constraint def time_s_range_0_to_900s_constraint {
        attribute time : ScalarValues::Real;
    }
    constraint def cmd_start_boolean_range_constraint {
        attribute command_value : ScalarValues::Real;
    }
    constraint def cmd_stop_boolean_range_constraint {
        attribute command_value : ScalarValues::Real;
    }
    constraint def cmd_shut_boolean_range_constraint {
        attribute command_value : ScalarValues::Real;
    }
    constraint def tank1_level_m_range_005_to_08m_constraint {
        attribute tank_level : ScalarValues::Real;
    }
    constraint def tank2_level_m_range_005_to_069286m_constraint {
        attribute tank_level : ScalarValues::Real;
    }
    constraint def valve1_open_boolean_range_constraint {
        attribute valve_open_value : ScalarValues::Real;
    }
    constraint def valve2_open_boolean_range_constraint {
        attribute valve_open_value : ScalarValues::Real;
    }
    constraint def valve3_open_boolean_range_constraint {
        attribute valve_open_value : ScalarValues::Real;
    }
    constraint def wait_remaining_s_range_0_to_12s_constraint {
        attribute wait_remaining_time : ScalarValues::Real;
    }
    constraint def delay_timer_remaining_time_constraint {
        attribute delay_timer_remaining_time : ScalarValues::Real;
        attribute STOP_START_state : ScalarValues::Real;
        doc /* LINEAR:  */
    }
    constraint def t1_fill_rate_time_constraint {
        attribute T1_fill_rate : ScalarValues::Real;
        attribute time_after_start_event : ScalarValues::Real;
        doc /* LINEAR:  */
    }
    constraint def transfer_back_to_fill_timing_constraint {
        attribute transfer_back_to_fill : ScalarValues::Real;
        attribute tank1_low_event_timing : ScalarValues::Real;
        doc /* LINEAR:  */
    }
    constraint def tank1_level_valve_interaction_constraint {
        attribute tank1Level : ScalarValues::Real;
        attribute valve1_valve2 : ScalarValues::Real;
        doc /* LINEAR:  */
    }
    constraint def tank2_level_valve_interaction_constraint {
        attribute tank2Level : ScalarValues::Real;
        attribute valve2_valve3 : ScalarValues::Real;
        doc /* LINEAR:  */
    }
    constraint def valve_position_actuator_command_constraint {
        attribute valve_position_open_closed_state : ScalarValues::Real;
        attribute _24_VDC_actuator_command_energized_de_energized : ScalarValues::Real;
        doc /* LINEAR:  */
    }
    constraint def t1_fill_level_proportional_constraint {
        attribute T1_fill_level_control : ScalarValues::Real;
        attribute T1_level_error_relative_to_effective_high_level_setpoint : ScalarValues::Real;
        doc /* PROPORTIONAL: , setpoint=0.8m */
    }
}
