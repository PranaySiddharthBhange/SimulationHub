package Constraints {
    constraint def Tank1_initial_level_range {
        attribute initial_level : ScalarValues::Real;
    }
    constraint def Tank2_initial_level_range {
        attribute initial_level : ScalarValues::Real;
    }
    constraint def Tank1_high_level_limit_range {
        attribute high_level_limit : ScalarValues::Real;
    }
    constraint def Tank1_low_level_limit_range {
        attribute low_level_limit : ScalarValues::Real;
    }
    constraint def Tank2_low_level_limit_range {
        attribute low_level_limit : ScalarValues::Real;
    }
    constraint def WaitAfterTank1High_duration_range {
        attribute waiting_period : ScalarValues::Real;
    }
    constraint def WaitAfterTank1Low_duration_range {
        attribute waiting_period : ScalarValues::Real;
    }
    constraint def WaitAfterTank2Low_duration_range {
        attribute waiting_period : ScalarValues::Real;
    }
    constraint def TK101_initial_level_range {
        attribute initial_level : ScalarValues::Real;
    }
    constraint def TK102_initial_level_range {
        attribute initial_level : ScalarValues::Real;
    }
    constraint def TK101_high_level_limit_range {
        attribute high_level_limit : ScalarValues::Real;
    }
    constraint def TK101_low_level_limit_range {
        attribute low_level_limit : ScalarValues::Real;
    }
    constraint def TK102_low_level_limit_range {
        attribute low_level_limit : ScalarValues::Real;
    }
    constraint def Controller_waitAfterTank1High_range {
        attribute wait_after_Tank_1_high : ScalarValues::Real;
    }
    constraint def Controller_waitAfterTank1Low_range {
        attribute wait_after_Tank_1_low : ScalarValues::Real;
    }
    constraint def Controller_waitAfterTank2Low_range {
        attribute wait_after_Tank_2_low : ScalarValues::Real;
    }
    constraint def XV101_nominal_inlet_flow_range {
        attribute nominal_inlet_flow : ScalarValues::Real;
    }
    constraint def XV102_nominal_transfer_flow_range {
        attribute nominal_transfer_flow : ScalarValues::Real;
    }
    constraint def XV103_nominal_drain_flow_range {
        attribute nominal_drain_flow : ScalarValues::Real;
    }
    constraint def PLC101_scan_time_range {
        attribute controller_scan_time : ScalarValues::Real;
    }
    constraint def Demo_simulation_stop_time_range {
        attribute simulation_stop_time : ScalarValues::Real;
    }
    constraint def LT101_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def LT102_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def PBSTART_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def PBSTOP_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def PBSHUT_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def DO101_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def DO102_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def DO103_engineering_range {
        attribute engineering_range : ScalarValues::Real;
    }
    constraint def V1_V2_simultaneous_open_state_limit {
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    constraint def V2_V3_simultaneous_open_normal_limit {
        attribute simultaneous_open_state_during_normal_automatic_operation : ScalarValues::Real;
    }
    constraint def V2_V3_simultaneous_open_shutdown_requirement {
        attribute simultaneous_open_state_in_SHUTDOWN : ScalarValues::Real;
    }
    constraint def Controller_outputs_false_on_power_loss_range {
        attribute command_state : ScalarValues::Real;
    }
    constraint def Level_threshold_comparison_inclusive_rule {
        attribute comparison_inclusion : ScalarValues::Real;
    }
    constraint def T1_high_limit_lower_bound {
        attribute level_threshold : ScalarValues::Real;
    }
    constraint def T1_high_threshold_height_range {
        attribute height : ScalarValues::Real;
    }
    constraint def Post_transfer_delay_range {
        attribute delay : ScalarValues::Real;
    }
    constraint def Inter_cycle_delay_after_T2_low_range {
        attribute delay : ScalarValues::Real;
    }
    constraint def T1_fill_target_level_range {
        attribute target_level : ScalarValues::Real;
    }
    constraint def T1_low_dead_time_range {
        attribute dead_time : ScalarValues::Real;
    }
    constraint def T2_refill_after_low_delay_range {
        attribute delay : ScalarValues::Real;
    }
    constraint def T1_high_limit_upper_bound {
        attribute level_limit : ScalarValues::Real;
    }
    constraint def Drain_valve_opening_delay_after_T1_low_range {
        attribute delay : ScalarValues::Real;
    }
    constraint def Next_fill_after_T2_low_delay_range {
        attribute delay : ScalarValues::Real;
    }
    constraint def tank1Level_value_range {
        attribute level : ScalarValues::Real;
    }
    constraint def tank2Level_value_range {
        attribute level : ScalarValues::Real;
    }
    constraint def XV101_demo_flow_coefficient_range {
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    constraint def XV102_demo_flow_coefficient_range {
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    constraint def XV103_demo_flow_coefficient_range {
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    constraint def XV101_full_open_stroke_time_range {
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    constraint def XV102_full_open_stroke_time_range {
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    constraint def XV103_full_open_stroke_time_range {
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    constraint def XV101_full_close_stroke_time_range {
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    constraint def XV102_full_close_stroke_time_range {
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    constraint def XV103_full_close_stroke_time_range {
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    constraint def T1_level_upper_bound {
        attribute level : ScalarValues::Real;
    }
    constraint def AllValves_closed_during_stop_interval_220_280 {
        attribute open_closed_state_during_STOP_interval_220_s_to_280_s : ScalarValues::Real;
    }
    constraint def AllValves_closed_during_stop_interval_650_700 {
        attribute open_closed_state_during_STOP_interval_650_s_to_700_s : ScalarValues::Real;
    }
    constraint def V1_commanded_closed_at_700s_shutdown {
        attribute commanded_state_at_700_s_during_shutdown : ScalarValues::Real;
    }
    constraint def V2_V3_commanded_open_at_700s_shutdown {
        attribute commanded_state_at_700_s_during_shutdown : ScalarValues::Real;
    }
    constraint def Controller_simulation_duration_range {
        attribute simulation_duration : ScalarValues::Real;
    }
    constraint def Controller_logging_interval_range {
        attribute logging_interval : ScalarValues::Real;
    }
    constraint def State_boundary_timestamp_tolerance_range {
        attribute timestamp_tolerance : ScalarValues::Real;
    }
    constraint def time_s_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def cmd_start_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def cmd_stop_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def cmd_shut_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def tank1_level_m_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def tank2_level_m_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def valve1_open_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def valve2_open_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def valve3_open_value_range {
        attribute value : ScalarValues::Real;
    }
    constraint def wait_remaining_s_value_range {
        attribute value : ScalarValues::Real;
    }
}
