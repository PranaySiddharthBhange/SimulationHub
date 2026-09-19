package Requirements {
    requirement def START_initiates_automatic_operation {
        doc /* START command.behavior in initial condition == initiates automatic operation */
        attribute behavior_in_initial_condition : ScalarValues::Real;
    }
    requirement def V1_open_during_normal_operation {
        doc /* V1.state during normal operation == open */
        attribute state_during_normal_operation : ScalarValues::Real;
    }
    requirement def V1_closed_at_T1_high_limit {
        doc /* V1.state at Tank 1 high-level limit == closed */
        attribute state_at_Tank_1_high_level_limit : ScalarValues::Real;
    }
    requirement def wait_after_T1_high_duration {
        doc /* wait after Tank 1 high.duration == 10.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def V2_open_after_T1_high_wait {
        doc /* V2.state after wait following Tank 1 high == open */
        attribute state_after_wait_following_Tank_1_high : ScalarValues::Real;
    }
    requirement def V2_closed_at_T1_minimum_level {
        doc /* V2.state at Tank 1 minimum operating level == closed */
        attribute state_at_Tank_1_minimum_operating_level : ScalarValues::Real;
    }
    requirement def wait_after_T1_low_duration {
        doc /* wait after Tank 1 low.duration == 10.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def V3_open_after_T1_low_wait {
        doc /* V3.state after wait following Tank 1 low == open */
        attribute state_after_wait_following_Tank_1_low : ScalarValues::Real;
    }
    requirement def V3_closed_at_T2_minimum_level {
        doc /* V3.state at Tank 2 minimum operating level == closed */
        attribute state_at_Tank_2_minimum_operating_level : ScalarValues::Real;
    }
    requirement def wait_after_T2_low_duration {
        doc /* wait after Tank 2 low.duration == 10.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def automatic_process_cyclic_continuation {
        doc /* automatic process.continuation mode == cyclic */
        attribute continuation_mode : ScalarValues::Real;
    }
    requirement def STOP_closes_all_three_valves {
        doc /* STOP command.state of all three valves == closed */
        attribute state_of_all_three_valves : ScalarValues::Real;
    }
    requirement def STOP_suspends_automatic_operation {
        doc /* STOP command.automatic operation == suspended */
        attribute automatic_operation : ScalarValues::Real;
    }
    requirement def START_after_STOP_continues_existing_process {
        doc /* START after STOP.process operation mode == continue existing process */
        attribute process_operation_mode : ScalarValues::Real;
    }
    requirement def START_after_STOP_no_new_empty_cycle {
        doc /* START after STOP.initialization mode == not force new empty-cycle initialization */
        attribute initialization_mode : ScalarValues::Real;
    }
    requirement def SHUT_empties_T1_and_T2 {
        doc /* SHUT command.Tank 1 and Tank 2 state == empty */
        attribute Tank_1_and_Tank_2_state : ScalarValues::Real;
    }
    requirement def SHUT_opens_V2 {
        doc /* SHUT command.V2 state == open */
        attribute V2_state : ScalarValues::Real;
    }
    requirement def SHUT_opens_V3 {
        doc /* SHUT command.V3 state == open */
        attribute V3_state : ScalarValues::Real;
    }
    requirement def SHUT_inhibits_V1 {
        doc /* SHUT command.V1 state == inhibited */
        attribute V1_state : ScalarValues::Real;
    }
    requirement def shutdown_emptying_closes_V2_V3 {
        doc /* V2 and V3.state after shutdown emptying is achieved == closed */
        attribute state_after_shutdown_emptying_is_achieved : ScalarValues::Real;
    }
    requirement def shutdown_complete_controller_start_configuration {
        doc /* controller.state after shutdown emptying is achieved == start configuration */
        attribute state_after_shutdown_emptying_is_achieved : ScalarValues::Real;
    }
    requirement def T1_initial_level_005m {
        doc /* Tank 1 initial level.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T2_initial_level_005m {
        doc /* Tank 2 initial level.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T1_high_limit_078m {
        doc /* Tank 1 high limit.value == 0.78 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T1_low_limit_005m {
        doc /* Tank 1 low limit.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T2_low_limit_005m {
        doc /* Tank 2 low limit.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def wait_after_T1_high_10s {
        doc /* Wait after T1 high.value == 10.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def wait_after_T1_low_10s {
        doc /* Wait after T1 low.value == 10.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def wait_after_T2_low_10s {
        doc /* Wait after T2 low.value == 10.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def actuators_power_loss_fail_safe_closed {
        doc /* actuators.power-loss fail-safe state == closed */
        attribute power_loss_fail_safe_state : ScalarValues::Real;
    }
    requirement def START_valid_when_idle_or_paused {
        doc /* controller.automatic fill-transfer-drain sequence start condition == valid START command when the process is idle or paused */
        attribute automatic_fill_transfer_drain_sequence_start_condition : ScalarValues::Real;
    }
    requirement def automatic_sequence_inlet_valve_V1 {
        doc /* automatic sequence.inlet valve == V1 */
        attribute inlet_valve : ScalarValues::Real;
    }
    requirement def wait_after_T1_high_before_V2_10s {
        doc /* controller.wait time after Tank 1 reaches high-level limit before opening V2 == 10.0 s */
        attribute wait_time_after_Tank_1_reaches_high_level_limit_before_opening_V2 : ScalarValues::Real;
    }
    requirement def V2_transfers_until_T1_low {
        doc /* V2.transfer liquid until Tank 1 low-level limit is reached == Tank 1 reaches its low-level limit */
        attribute transfer_liquid_until_Tank_1_low_level_limit_is_reached : ScalarValues::Real;
    }
    requirement def wait_after_T1_low_before_V3_10s {
        doc /* controller.wait time after Tank 1 reaches low-level limit before opening V3 == 10.0 s */
        attribute wait_time_after_Tank_1_reaches_low_level_limit_before_opening_V3 : ScalarValues::Real;
    }
    requirement def V3_drains_T2_until_low {
        doc /* V3.drain Tank 2 until == Tank 2 reaches its low-level limit */
        attribute drain_Tank_2_until : ScalarValues::Real;
    }
    requirement def wait_after_T2_low_before_fill_10s {
        doc /* controller.return to Tank 1 filling operation wait time after Tank 2 reaches low-level limit == 10.0 s */
        attribute return_to_Tank_1_filling_operation_wait_time_after_Tank_2_reaches_low_level_limit : ScalarValues::Real;
    }
    requirement def STOP_closes_valves_and_pauses_controller {
        doc /* controller.STOP command effect == close V1, V2 and V3 and place the controller in a paused condition */
        attribute STOP_command_effect : ScalarValues::Real;
    }
    requirement def START_after_STOP_resumes_from_pause {
        doc /* controller.START after STOP behavior == continue the sequence from the point at which STOP was accepted */
        attribute START_after_STOP_behavior : ScalarValues::Real;
    }
    requirement def SHUT_opens_V2_V3_inhibits_V1 {
        doc /* controller.SHUT command effect == command V2 and V3 open to drain both tanks and inhibit V1 */
        attribute SHUT_command_effect : ScalarValues::Real;
    }
    requirement def post_shutdown_all_valves_closed_idle_configuration {
        doc /* controller.post-shutdown state == all three valves closed and initial idle configuration */
        attribute post_shutdown_state : ScalarValues::Real;
    }
    requirement def power_loss_valves_closed {
        doc /* process valves.position on controller power loss == closed */
        attribute position_on_controller_power_loss : ScalarValues::Real;
    }
    requirement def command_priority_SHUT_STOP_START {
        doc /* command priority.ordering == SHUT > STOP > START */
        attribute ordering : ScalarValues::Real;
    }
    requirement def V1_never_open_while_V2_open {
        doc /* V1.commanded open while V2 is open == never */
        attribute commanded_open_while_V2_is_open : ScalarValues::Real;
    }
    requirement def V2_V3_simultaneous_open_not_allowed_normal_auto {
        doc /* V2 and V3.simultaneous open state during normal automatic operation == not allowed */
        attribute simultaneous_open_state_during_normal_automatic_operation : ScalarValues::Real;
    }
    requirement def V2_V3_simultaneous_open_allowed {
        doc /* V2 and V3.simultaneous open state == allowed */
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    requirement def T1_high_level_setpoint_080m {
        doc /* Tank 1 high-level setpoint.value == 0.8 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T1_low_level_setpoint_005m {
        doc /* Tank 1 low-level setpoint.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T2_low_level_setpoint_005m {
        doc /* Tank 2 low-level setpoint.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def post_transfer_waiting_time_12s {
        doc /* post-transfer waiting time.value == 12.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def inter_cycle_wait_after_T2_low_8s {
        doc /* inter-cycle waiting time after Tank 2 reaches low level.value == 8.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def controller_receives_two_level_measurements {
        doc /* controller.number of analog level measurements received == 2.0 */
        attribute number_of_analog_level_measurements_received : ScalarValues::Real;
    }
    requirement def controller_receives_three_momentary_digital_commands {
        doc /* controller.number of momentary digital commands received == 3.0 */
        attribute number_of_momentary_digital_commands_received : ScalarValues::Real;
    }
    requirement def controller_provides_three_discrete_valve_open_commands {
        doc /* controller.number of discrete valve-open commands provided == 3.0 */
        attribute number_of_discrete_valve_open_commands_provided : ScalarValues::Real;
    }
    requirement def wait_timer_freezes_on_STOP {
        doc /* wait timer.behavior on STOP during wait state == freeze rather than restart */
        attribute behavior_on_STOP_during_wait_state : ScalarValues::Real;
    }
    requirement def START_ignored_when_already_running {
        doc /* START commands.behavior while already running == ignored */
        attribute behavior_while_already_running : ScalarValues::Real;
    }
    requirement def STOP_ignored_during_SHUT_mode {
        doc /* STOP commands.behavior during SHUT mode == ignored until shutdown is complete */
        attribute behavior_during_SHUT_mode : ScalarValues::Real;
    }
    requirement def START_ignored_during_SHUT_mode {
        doc /* START commands.behavior during SHUT mode == ignored until shutdown is complete */
        attribute behavior_during_SHUT_mode : ScalarValues::Real;
    }
    requirement def shutdown_complete_when_both_tanks_below_low_setpoint {
        doc /* shutdown completion.tank level condition == Tank 1 and Tank 2 both at or below their low-level setpoints */
        attribute tank_level_condition : ScalarValues::Real;
    }
    requirement def demonstration_run_duration_900s_max {
        doc /* 0.0 RANGE demonstration run.simulation duration RANGE 900.0 s */
        attribute simulation_duration : ScalarValues::Real;
    }
    requirement def demo_run_START_time_20s {
        doc /* demonstration run.event schedule START time == 20.0 s */
        attribute event_schedule_START_time : ScalarValues::Real;
    }
    requirement def demo_run_STOP_time_220s {
        doc /* demonstration run.event schedule STOP time == 220.0 s */
        attribute event_schedule_STOP_time : ScalarValues::Real;
    }
    requirement def demo_run_START_time_280s {
        doc /* demonstration run.event schedule START time == 280.0 s */
        attribute event_schedule_START_time : ScalarValues::Real;
    }
    requirement def demo_run_STOP_time_650s {
        doc /* demonstration run.event schedule STOP time == 650.0 s */
        attribute event_schedule_STOP_time : ScalarValues::Real;
    }
    requirement def demo_run_SHUT_time_700s {
        doc /* demonstration run.event schedule SHUT time == 700.0 s */
        attribute event_schedule_SHUT_time : ScalarValues::Real;
    }
    requirement def level_values_internal_units_metres {
        doc /* level values.internal representation units == metres */
        attribute internal_representation_units : ScalarValues::Real;
    }
    requirement def level_values_nominal_range_0_to_1m {
        doc /* 0.0 RANGE level values.nominal valid range RANGE 1.0 m */
        attribute nominal_valid_range : ScalarValues::Real;
    }
    requirement def valve_commands_boolean_open_closed {
        doc /* valve commands.representation == Boolean open/closed commands */
        attribute representation : ScalarValues::Real;
    }
    requirement def TK_101_cross_section_area_12m2 {
        doc /* TK-101.cross-section area == 1.2 m^2 */
        attribute cross_section_area : ScalarValues::Real;
    }
    requirement def TK_101_height_1m {
        doc /* TK-101.height == 1.0 m */
        attribute height : ScalarValues::Real;
    }
    requirement def TK_101_max_working_level_09m {
        doc /* TK-101.max working level == 0.9 m */
        attribute max_working_level : ScalarValues::Real;
    }
    requirement def TK_102_cross_section_area_14m2 {
        doc /* TK-102.cross-section area == 1.4 m^2 */
        attribute cross_section_area : ScalarValues::Real;
    }
    requirement def TK_102_height_1m {
        doc /* TK-102.height == 1.0 m */
        attribute height : ScalarValues::Real;
    }
    requirement def TK_102_max_working_level_09m {
        doc /* TK-102.max working level == 0.9 m */
        attribute max_working_level : ScalarValues::Real;
    }
    requirement def XV_101_nominal_flow_0006 {
        doc /* XV-101.nominal flow == 0.006 m^3/s */
        attribute nominal_flow : ScalarValues::Real;
    }
    requirement def XV_101_fail_position_closed {
        doc /* XV-101.fail position == Closed */
        attribute fail_position : ScalarValues::Real;
    }
    requirement def XV_101_full_open_time_08s {
        doc /* XV-101.full-open time == 0.8 s */
        attribute full_open_time : ScalarValues::Real;
    }
    requirement def XV_102_nominal_flow_00045 {
        doc /* XV-102.nominal flow == 0.0045 m^3/s */
        attribute nominal_flow : ScalarValues::Real;
    }
    requirement def XV_102_fail_position_closed {
        doc /* XV-102.fail position == Closed */
        attribute fail_position : ScalarValues::Real;
    }
    requirement def XV_103_nominal_flow_0005 {
        doc /* XV-103.nominal flow == 0.005 m^3/s */
        attribute nominal_flow : ScalarValues::Real;
    }
    requirement def XV_103_fail_position_closed {
        doc /* XV-103.fail position == Closed */
        attribute fail_position : ScalarValues::Real;
    }
    requirement def LT_101_signal_mapping_4_20mA {
        doc /* LT-101.signal mapping == 4-20 mA mapped 0.0-1.0 m */
        attribute signal_mapping : ScalarValues::Real;
    }
    requirement def LT_102_signal_mapping_4_20mA {
        doc /* LT-102.signal mapping == 4-20 mA mapped 0.0-1.0 m */
        attribute signal_mapping : ScalarValues::Real;
    }
    requirement def PLC_101_scan_time_100ms {
        doc /* PLC-101.scan time == 100.0 ms */
        attribute scan_time : ScalarValues::Real;
    }
    requirement def DI_101_engineering_range_0_to_1 {
        doc /* 0.0 RANGE DI-101.engineering range RANGE 1.0 */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def DI_102_engineering_range_0_to_1 {
        doc /* 0.0 RANGE DI-102.engineering range RANGE 1.0 */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def DI_103_engineering_range_0_to_1 {
        doc /* 0.0 RANGE DI-103.engineering range RANGE 1.0 */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def AI_101_engineering_range_0_to_1m {
        doc /* 0.0 RANGE AI-101.engineering range RANGE 1.0 m */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def AI_101_normal_state_005m {
        doc /* AI-101.normal state == 0.05 m */
        attribute normal_state : ScalarValues::Real;
    }
    requirement def AI_101_update_period_100ms {
        doc /* AI-101.update period == 100.0 ms */
        attribute update_period : ScalarValues::Real;
    }
    requirement def AI_102_engineering_range_0_to_1m {
        doc /* 0.0 RANGE AI-102.engineering range RANGE 1.0 m */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def AI_102_normal_state_005m {
        doc /* AI-102.normal state == 0.05 m */
        attribute normal_state : ScalarValues::Real;
    }
    requirement def AI_102_update_period_100ms {
        doc /* AI-102.update period == 100.0 ms */
        attribute update_period : ScalarValues::Real;
    }
    requirement def DO_101_engineering_range_0_to_1 {
        doc /* 0.0 RANGE DO-101.engineering range RANGE 1.0 */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def DO_101_normal_state_0 {
        doc /* DO-101.normal state == 0.0 */
        attribute normal_state : ScalarValues::Real;
    }
    requirement def DO_101_update_period_100ms {
        doc /* DO-101.update period == 100.0 ms */
        attribute update_period : ScalarValues::Real;
    }
    requirement def DO_102_engineering_range_0_to_1 {
        doc /* 0.0 RANGE DO-102.engineering range RANGE 1.0 */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def DO_102_normal_state_0 {
        doc /* DO-102.normal state == 0.0 */
        attribute normal_state : ScalarValues::Real;
    }
    requirement def DO_102_update_period_100ms {
        doc /* DO-102.update period == 100.0 ms */
        attribute update_period : ScalarValues::Real;
    }
    requirement def DO_103_engineering_range_0_to_1 {
        doc /* 0.0 RANGE DO-103.engineering range RANGE 1.0 */
        attribute engineering_range : ScalarValues::Real;
    }
    requirement def DO_103_normal_state_0 {
        doc /* DO-103.normal state == 0.0 */
        attribute normal_state : ScalarValues::Real;
    }
    requirement def DO_103_update_period_100ms {
        doc /* DO-103.update period == 100.0 ms */
        attribute update_period : ScalarValues::Real;
    }
    requirement def simulation_stop_time_900s {
        doc /* simulation stop time.value == 900.0 s */
        attribute value : ScalarValues::Real;
    }
    requirement def controller_initial_level_for_TK_101_005m {
        doc /* controller.initial level for TK-101 == 0.05 m */
        attribute initial_level_for_TK_101 : ScalarValues::Real;
    }
    requirement def controller_initial_level_for_TK_102_005m {
        doc /* controller.initial level for TK-102 == 0.05 m */
        attribute initial_level_for_TK_102 : ScalarValues::Real;
    }
    requirement def T1_high_limit_effective_080m {
        doc /* Tank 1 high-level limit.value == 0.8 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T1_low_limit_effective_005m {
        doc /* Tank 1 low-level limit.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def T2_low_limit_effective_005m {
        doc /* Tank 2 low-level limit.value == 0.05 m */
        attribute value : ScalarValues::Real;
    }
    requirement def controller_wait_after_T1_high_10s {
        doc /* controller.wait after Tank 1 high == 10.0 s */
        attribute wait_after_Tank_1_high : ScalarValues::Real;
    }
    requirement def controller_wait_after_T1_low_12s {
        doc /* controller.wait after Tank 1 low == 12.0 s */
        attribute wait_after_Tank_1_low : ScalarValues::Real;
    }
    requirement def controller_wait_after_T2_low_8s {
        doc /* controller.wait after Tank 2 low == 8.0 s */
        attribute wait_after_Tank_2_low : ScalarValues::Real;
    }
    requirement def controller_nominal_inlet_flow_0006 {
        doc /* controller.nominal inlet flow == 0.006 m^3/s */
        attribute nominal_inlet_flow : ScalarValues::Real;
    }
    requirement def controller_nominal_transfer_flow_00045 {
        doc /* controller.nominal transfer flow == 0.0045 m^3/s */
        attribute nominal_transfer_flow : ScalarValues::Real;
    }
    requirement def controller_nominal_drain_flow_0005 {
        doc /* controller.nominal drain flow == 0.005 m^3/s */
        attribute nominal_drain_flow : ScalarValues::Real;
    }
    requirement def PLC_101_controller_scan_time_01s {
        doc /* PLC-101.controller scan time == 0.1 s */
        attribute controller_scan_time : ScalarValues::Real;
    }
    requirement def tank1_level_default_005g {
        doc /* tank1.level.default value == 0.05 g */
        attribute default_value : ScalarValues::Real;
    }
    requirement def tank2_level_default_005g {
        doc /* tank2.level.default value == 0.05 g */
        attribute default_value : ScalarValues::Real;
    }
    requirement def controller_command_priority_SHUT_highest {
        doc /* controller.command priority of SHUT == highest */
        attribute command_priority_of_SHUT : ScalarValues::Real;
    }
    requirement def controller_command_priority_STOP_next_after_SHUT {
        doc /* controller.command priority of STOP == next after SHUT */
        attribute command_priority_of_STOP : ScalarValues::Real;
    }
    requirement def controller_command_priority_START_lowest {
        doc /* controller.command priority of START == lowest */
        attribute command_priority_of_START : ScalarValues::Real;
    }
    requirement def controller_state_on_valid_SHUT_edge_SHUTDOWN {
        doc /* controller.state on valid SHUT edge == SHUTDOWN */
        attribute state_on_valid_SHUT_edge : ScalarValues::Real;
    }
    requirement def controller_state_on_STOP_command_PAUSED {
        doc /* controller.state on STOP command == PAUSED */
        attribute state_on_STOP_command : ScalarValues::Real;
    }
    requirement def controller_valve_outputs_during_PAUSED_false {
        doc /* controller.valve outputs during PAUSED after STOP == false */
        attribute valve_outputs_during_PAUSED_after_STOP : ScalarValues::Real;
    }
    requirement def controller_state_on_START_from_IDLE_FILL_T1 {
        doc /* controller.state on START from IDLE == FILL_T1 */
        attribute state_on_START_from_IDLE : ScalarValues::Real;
    }
    requirement def controller_state_on_START_from_PAUSED_resume_stored_state {
        doc /* controller.state on START from PAUSED == stored interrupted state */
        attribute state_on_START_from_PAUSED : ScalarValues::Real;
    }
    requirement def controller_START_ignored_when_running {
        doc /* controller.START while already running behavior == ignored */
        attribute START_while_already_running_behavior : ScalarValues::Real;
    }
    requirement def controller_commands_do_not_interrupt_SHUTDOWN {
        doc /* controller.commands during SHUTDOWN behavior == do not interrupt shutdown sequence */
        attribute commands_during_SHUTDOWN_behavior : ScalarValues::Real;
    }
    requirement def controller_command_required_after_shutdown_START {
        doc /* controller.command required after shutdown completes == START */
        attribute command_required_after_shutdown_completes : ScalarValues::Real;
    }
    requirement def controller_remaining_delay_retained_after_STOP {
        doc /* controller.remaining delay after STOP in wait states == retained */
        attribute remaining_delay_after_STOP_in_wait_states : ScalarValues::Real;
    }
    requirement def controller_resume_timer_with_remaining_delay {
        doc /* controller.resume timer behavior after START == resume with remaining delay */
        attribute resume_timer_behavior_after_START : ScalarValues::Real;
    }
    requirement def V1_V2_simultaneous_open_not_allowed {
        doc /* V1 and V2.simultaneous open state == not allowed */
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    requirement def V2_V3_simultaneous_open_not_allowed {
        doc /* V2 and V3.simultaneous open state == not allowed */
        attribute simultaneous_open_state : ScalarValues::Real;
    }
    requirement def V2_V3_simultaneous_open_restriction_waived {
        doc /* V2 and V3.simultaneous open restriction == waived */
        attribute simultaneous_open_restriction : ScalarValues::Real;
    }
    requirement def valves_de_energize_to_close {
        doc /* valves.actuation mode == de-energize-to-close */
        attribute actuation_mode : ScalarValues::Real;
    }
    requirement def controller_outputs_false_on_power_loss {
        doc /* controller output commands.state on controller power loss == false */
        attribute state_on_controller_power_loss : ScalarValues::Real;
    }
    requirement def level_threshold_comparisons_include_equality {
        doc /* level threshold comparisons.comparison includes equality == true */
        attribute comparison_includes_equality : ScalarValues::Real;
    }
    requirement def FILL_T1_guard_LT_101_gte_T1_High {
        doc /* FILL_T1 transition guard.LT-101 threshold relation >= T1_High */
        attribute LT_101_threshold_relation : ScalarValues::Real;
    }
    requirement def TRANSFER_T1_T2_guard_LT_101_lte_T1_Low {
        doc /* TRANSFER_T1_T2 transition guard.LT-101 threshold relation <= T1_Low */
        attribute LT_101_threshold_relation : ScalarValues::Real;
    }
    requirement def DRAIN_T2_guard_LT_102_lte_T2_Low {
        doc /* DRAIN_T2 transition guard.LT-102 threshold relation <= T2_Low */
        attribute LT_102_threshold_relation : ScalarValues::Real;
    }
    requirement def WAIT_AFTER_DRAIN_next_state_FILL_T1 {
        doc /* WAIT_AFTER_DRAIN.automatic next state after timer expiry == FILL_T1 */
        attribute automatic_next_state_after_timer_expiry : ScalarValues::Real;
    }
    requirement def SHUTDOWN_exit_condition_IDLE {
        doc /* SHUTDOWN.exit condition == IDLE */
        attribute exit_condition : ScalarValues::Real;
    }
    requirement def command_precedence_SHUT_STOP_START {
        doc /* command precedence.priority order == SHUT > STOP > START */
        attribute priority_order : ScalarValues::Real;
    }
    requirement def STOP_command_all_valves_closed {
        doc /* STOP command.valve command state == all valves closed */
        attribute valve_command_state : ScalarValues::Real;
    }
    requirement def STOP_command_interrupted_state_stored {
        doc /* STOP command.interrupted state == stored */
        attribute interrupted_state : ScalarValues::Real;
    }
    requirement def STOP_during_any_delay_remaining_delay_frozen {
        doc /* STOP during any delay.remaining delay == frozen */
        attribute remaining_delay : ScalarValues::Real;
    }
    requirement def START_remaining_delay_resumed {
        doc /* START command.remaining delay == resumed */
        attribute remaining_delay : ScalarValues::Real;
    }
    requirement def automatic_sequence_ignored_on_START {
        doc /* automatic sequence.behavior on START == ignored */
        attribute behavior_on_START : ScalarValues::Real;
    }
    requirement def START_ignored_during_active_SHUT {
        doc /* START command.behavior during active SHUT == ignored */
        attribute behavior_during_active_SHUT : ScalarValues::Real;
    }
    requirement def STOP_ignored_during_active_SHUT {
        doc /* STOP command.behavior during active SHUT == ignored */
        attribute behavior_during_active_SHUT : ScalarValues::Real;
    }
    requirement def SHUT_completion_LT_101_LT_102_below_low_setpoints {
        doc /* SHUT.completion criterion == LT-101 and LT-102 at or below their low-level setpoints */
        attribute completion_criterion : ScalarValues::Real;
    }
    requirement def after_shutdown_all_valves_closed {
        doc /* after shutdown completion.valve command state == all valves closed */
        attribute valve_command_state : ScalarValues::Real;
    }
    requirement def sequence_context_state_IDLE {
        doc /* sequence context.state == IDLE */
        attribute state_value : ScalarValues::Real;
    }
    requirement def V1_V2_commanded_open_together_never {
        doc /* V1 and V2.commanded open together == never */
        attribute commanded_open_together : ScalarValues::Real;
    }
    requirement def V2_V3_commanded_open_together_not_allowed_normal_auto {
        doc /* V2 and V3.commanded open together in normal auto operation == not allowed */
        attribute commanded_open_together_in_normal_auto_operation : ScalarValues::Real;
    }
    requirement def T1_high_setpoint_080m {
        doc /* T1 high.setpoint == 0.8 m */
        attribute setpoint : ScalarValues::Real;
    }
    requirement def post_transfer_delay_12s {
        doc /* post-transfer delay.duration == 12.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def inter_cycle_delay_after_T2_low_8s {
        doc /* inter-cycle delay after Tank 2 low.duration == 8.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def T1_fill_target_080m {
        doc /* T1 fill target.target level == 0.8 m */
        attribute target_level : ScalarValues::Real;
    }
    requirement def controls_wait_after_T1_low_dead_time_12s {
        doc /* controls wait after T1 low.dead time == 12.0 s */
        attribute dead_time : ScalarValues::Real;
    }
    requirement def new_fill_after_T2_low_delay_8s {
        doc /* new fill after T2 low.delay == 8.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def system_idle_duration_after_shutdown_900s {
        doc /* system.idle duration after shutdown finishes == 900.0 s */
        attribute idle_duration_after_shutdown_finishes : ScalarValues::Real;
    }
    requirement def T1_high_limit_effective_value_080m {
        doc /* T1 high limit.effective value == 0.8 m */
        attribute effective_value : ScalarValues::Real;
    }
    requirement def time_after_T1_low_before_opening_drain_valve_12s {
        doc /* time after T1 reaches low level before opening the drain valve.delay == 12.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def time_after_T2_low_before_next_fill_8s {
        doc /* time after T2 reaches low before the next fill starts.delay == 8.0 s */
        attribute delay : ScalarValues::Real;
    }
    requirement def SHUT_state_priority_higher_than_STOP {
        doc /* SHUT state priority relative to STOP.priority relationship == higher than */
        attribute priority_relationship : ScalarValues::Real;
    }
    requirement def V2_V3_commanded_state_open_during_SHUT {
        doc /* V2 and V3 commanded state during SHUT.commanded state == open */
        attribute commanded_state : ScalarValues::Real;
    }
    requirement def START_ignored_during_SHUT {
        doc /* START command handling during SHUT.effect == ignored */
        attribute effect : ScalarValues::Real;
    }
    requirement def TankDemo_Rev12_stopped_state_on_startCmd_edge {
        doc /* model TankDemo_Rev12.stopped state on startCmd edge == None */
        attribute stopped_state_on_startCmd_edge : ScalarValues::Real;
    }
    requirement def TankDemo_Rev12_stopped_state_on_stopCmd_edge {
        doc /* model TankDemo_Rev12.stopped state on stopCmd edge == None */
        attribute stopped_state_on_stopCmd_edge : ScalarValues::Real;
    }
    requirement def valve1_command_state_seq_FILL_not_stopped {
        doc /* valve1.command state == (seq == StepState.FILL) and not stopped */
        attribute command_state : ScalarValues::Real;
    }
    requirement def valve2_command_state_seq_TRANSFER_not_stopped {
        doc /* valve2.command state == (seq == StepState.TRANSFER) and not stopped */
        attribute command_state : ScalarValues::Real;
    }
    requirement def valve3_command_state_seq_DRAIN_not_stopped {
        doc /* valve3.command state == (seq == StepState.DRAIN) and not stopped */
        attribute command_state : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_101_deenergized_position_closed {
        doc /* VXS-24 valve for project tag XV-101.de-energized position == Closed */
        attribute de_energized_position : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_102_deenergized_position_closed {
        doc /* VXS-24 valve for project tag XV-102.de-energized position == Closed */
        attribute de_energized_position : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_103_deenergized_position_closed {
        doc /* VXS-24 valve for project tag XV-103.de-energized position == Closed */
        attribute de_energized_position : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_101_nominal_flow_coeff_0006 {
        doc /* VXS-24 valve for project tag XV-101.nominal demo flow coefficient equivalent == 0.006 m^3/s */
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_102_nominal_flow_coeff_00045 {
        doc /* VXS-24 valve for project tag XV-102.nominal demo flow coefficient equivalent == 0.0045 m^3/s */
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_103_nominal_flow_coeff_0005 {
        doc /* VXS-24 valve for project tag XV-103.nominal demo flow coefficient equivalent == 0.005 m^3/s */
        attribute nominal_demo_flow_coefficient_equivalent : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_101_full_open_stroke_time_08s {
        doc /* VXS-24 valve for project tag XV-101.full open stroke time == 0.8 s */
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_102_full_open_stroke_time_08s {
        doc /* VXS-24 valve for project tag XV-102.full open stroke time == 0.8 s */
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_103_full_open_stroke_time_08s {
        doc /* VXS-24 valve for project tag XV-103.full open stroke time == 0.8 s */
        attribute full_open_stroke_time : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_101_full_close_stroke_time_06s {
        doc /* VXS-24 valve for project tag XV-101.full close stroke time == 0.6 s */
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_102_full_close_stroke_time_06s {
        doc /* VXS-24 valve for project tag XV-102.full close stroke time == 0.6 s */
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    requirement def VXS_24_valve_XV_103_full_close_stroke_time_06s {
        doc /* VXS-24 valve for project tag XV-103.full close stroke time == 0.6 s */
        attribute full_close_stroke_time : ScalarValues::Real;
    }
    requirement def VXS_24_valve_actuator_XV_101_24VDC_energized_open {
        doc /* VXS-24 valve actuator for project tag XV-101.command == 24 VDC energized=open */
        attribute command : ScalarValues::Real;
    }
    requirement def VXS_24_valve_actuator_XV_102_24VDC_energized_open {
        doc /* VXS-24 valve actuator for project tag XV-102.command == 24 VDC energized=open */
        attribute command : ScalarValues::Real;
    }
    requirement def VXS_24_valve_actuator_XV_103_24VDC_energized_open {
        doc /* VXS-24 valve actuator for project tag XV-103.command == 24 VDC energized=open */
        attribute command : ScalarValues::Real;
    }
    requirement def T1_initial_level_005m_repeat {
        doc /* T1.initial level == 0.05 m */
        attribute initial_level : ScalarValues::Real;
    }
    requirement def T2_initial_level_005m_repeat {
        doc /* T2.initial level == 0.05 m */
        attribute initial_level : ScalarValues::Real;
    }
    requirement def simulation_duration_900s {
        doc /* simulation.duration == 900.0 s */
        attribute duration : ScalarValues::Real;
    }
    requirement def logging_interval_1s {
        doc /* logging.interval == 1.0 s */
        attribute interval : ScalarValues::Real;
    }
    requirement def T1_effective_high_level_setpoint_080m {
        doc /* T1.effective high-level setpoint == 0.8 m */
        attribute effective_high_level_setpoint : ScalarValues::Real;
    }
    requirement def all_valves_command_state_closed {
        doc /* all valves.command state == closed */
        attribute command_state : ScalarValues::Real;
    }
    requirement def controller_resume_interrupted_transfer_on_START_at_280s {
        doc /* controller.operation after START at 280 s == resume interrupted transfer */
        attribute operation_after_START_at_280_s : ScalarValues::Real;
    }
    requirement def controller_inter_cycle_delay_8s {
        doc /* controller.inter-cycle delay == 8.0 s */
        attribute inter_cycle_delay : ScalarValues::Real;
    }
    requirement def all_valves_command_state_closed_repeat {
        doc /* all valves.command state == closed */
        attribute command_state : ScalarValues::Real;
    }
    requirement def V1_command_state_closed {
        doc /* V1.command state == closed */
        attribute command_state : ScalarValues::Real;
    }
    requirement def V2_V3_command_state_open {
        doc /* V2 and V3.command state == open */
        attribute command_state : ScalarValues::Real;
    }
    requirement def controller_state_IDLE {
        doc /* controller.state == IDLE */
        attribute state_value : ScalarValues::Real;
    }
    requirement def all_valves_command_state_closed_again {
        doc /* all valves.command state == closed */
        attribute command_state : ScalarValues::Real;
    }
    requirement def controller_command_compatibility_V1_V2_and_V2_V3 {
        doc /* controller.command compatibility == V1 and V2 never simultaneously; V2 and V3 never simultaneously in normal automatic operation */
        attribute command_compatibility : ScalarValues::Real;
    }
    requirement def state_boundary_comparison_tolerance_2s {
        doc /* state-boundary comparison tolerance.tolerance == 2.0 s */
        attribute tolerance : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_row_count_901 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.row_count == 901.0 rows */
        attribute row_count : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_time_s_minimum_0s {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.time_s minimum >= 0.0 s */
        attribute time_s_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_time_s_maximum_900s {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.time_s maximum <= 900.0 s */
        attribute time_s_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_sampling_period_1s {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.sampling_period == 1.0 s */
        attribute sampling_period : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_tank1_level_min_005m {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.tank1_level_m minimum >= 0.05 m */
        attribute tank1_level_m_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_tank1_level_max_08m {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.tank1_level_m maximum <= 0.8 m */
        attribute tank1_level_m_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_tank2_level_min_005m {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.tank2_level_m minimum >= 0.05 m */
        attribute tank2_level_m_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_tank2_level_max_069286m {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.tank2_level_m maximum <= 0.69286 m */
        attribute tank2_level_m_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_cmd_start_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.cmd_start minimum >= 0.0 1 */
        attribute cmd_start_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_cmd_start_max_1 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.cmd_start maximum <= 1.0 1 */
        attribute cmd_start_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_cmd_stop_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.cmd_stop minimum >= 0.0 1 */
        attribute cmd_stop_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_cmd_stop_max_1 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.cmd_stop maximum <= 1.0 1 */
        attribute cmd_stop_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_cmd_shut_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.cmd_shut minimum >= 0.0 1 */
        attribute cmd_shut_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_cmd_shut_max_1 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.cmd_shut maximum <= 1.0 1 */
        attribute cmd_shut_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_valve1_open_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.valve1_open minimum >= 0.0 1 */
        attribute valve1_open_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_valve1_open_max_1 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.valve1_open maximum <= 1.0 1 */
        attribute valve1_open_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_valve2_open_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.valve2_open minimum >= 0.0 1 */
        attribute valve2_open_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_valve2_open_max_1 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.valve2_open maximum <= 1.0 1 */
        attribute valve2_open_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_valve3_open_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.valve3_open minimum >= 0.0 1 */
        attribute valve3_open_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_valve3_open_max_1 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.valve3_open maximum <= 1.0 1 */
        attribute valve3_open_maximum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_wait_remaining_s_min_0 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.wait_remaining_s minimum >= 0.0 s */
        attribute wait_remaining_s_minimum : ScalarValues::Real;
    }
    requirement def dataset_10_demo_run_900s_wait_remaining_s_max_12 {
        doc /* dataset 09_datasets/10_demo_run_900s.csv.wait_remaining_s maximum <= 12.0 s */
        attribute wait_remaining_s_maximum : ScalarValues::Real;
    }
}
