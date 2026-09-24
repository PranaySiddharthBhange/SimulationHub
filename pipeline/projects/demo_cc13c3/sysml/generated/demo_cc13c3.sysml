package Two_Tank_Sequence_Controller {
  part def LiquidSource {
    attribute nominal_supply_available : ScalarValues::Boolean = true;
  }

  part def DrainSink {
  }

  part def OnOffValve {
    attribute open_cmd : ScalarValues::Boolean = false;
    attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
    attribute energized_open_voltage_vdc : ScalarValues::Real = 24.0;
    attribute nominal_flow_rate_m3_per_s : ScalarValues::Real;
    attribute stroke_open_time_s : ScalarValues::Real;
    attribute stroke_close_time_s : ScalarValues::Real;
    attribute ideal_boolean_flow_switch_for_simulation : ScalarValues::Boolean = true;
  }

  part def Tank {
    attribute level_m : ScalarValues::Real;
    attribute initial_level_m : ScalarValues::Real;
    attribute low_level_setpoint_m : ScalarValues::Real;
    attribute cross_section_area_m2 : ScalarValues::Real;
    attribute height_m : ScalarValues::Real;
    attribute max_working_level_m : ScalarValues::Real;
    attribute transmitter_range_low_m : ScalarValues::Real;
    attribute transmitter_range_high_m : ScalarValues::Real;
  }

  part def LevelTransmitter {
    attribute measured_level_m : ScalarValues::Real;
    attribute range_low_m : ScalarValues::Real;
    attribute range_high_m : ScalarValues::Real;
  }

  part def ScheduledCommand {
    attribute command_name : ScalarValues::String;
    attribute command_time_s : ScalarValues::Real;
  }

  part def Two_Tank_System {
    part SRC_101 : LiquidSource;
    part DRN_101 : DrainSink;

    part XV_101 : OnOffValve {
      doc /* XV-101, valve V1, valve1 */
      attribute nominal_flow_rate_m3_per_s = 0.0060;
      attribute stroke_open_time_s = 0.8;
      attribute stroke_close_time_s = 0.6;
    }

    part XV_102 : OnOffValve {
      doc /* XV-102, valve V2, valve2 */
      attribute nominal_flow_rate_m3_per_s = 0.0045;
      attribute stroke_open_time_s = 0.8;
      attribute stroke_close_time_s = 0.6;
    }

    part XV_103 : OnOffValve {
      doc /* XV-103, valve V3, valve3 */
      attribute nominal_flow_rate_m3_per_s = 0.0050;
      attribute stroke_open_time_s = 0.8;
      attribute stroke_close_time_s = 0.6;
    }

    part TK_101 : Tank {
      doc /* TK-101, Tank 1, T1, tank1 */
      attribute level_m = 0.05;
      attribute initial_level_m = 0.05;
      attribute low_level_setpoint_m = 0.05;
      attribute cross_section_area_m2 = 1.2;
      attribute height_m = 1.0;
      attribute max_working_level_m = 0.9;
      attribute transmitter_range_low_m = 0.0;
      attribute transmitter_range_high_m = 1.0;
      attribute high_level_setpoint_m : ScalarValues::Real = 0.80;
    }

    part TK_102 : Tank {
      doc /* TK-102, Tank 2, T2, tank2 */
      attribute level_m = 0.05;
      attribute initial_level_m = 0.05;
      attribute low_level_setpoint_m = 0.05;
      attribute cross_section_area_m2 = 1.4;
      attribute height_m = 1.0;
      attribute max_working_level_m = 0.9;
      attribute transmitter_range_low_m = 0.0;
      attribute transmitter_range_high_m = 1.0;
    }

    part LT_101 : LevelTransmitter {
      doc /* LT-101, level1, AI-101 */
      attribute measured_level_m = 0.05;
      attribute range_low_m = 0.0;
      attribute range_high_m = 1.0;
    }

    part LT_102 : LevelTransmitter {
      doc /* LT-102, level2, AI-102 */
      attribute measured_level_m = 0.05;
      attribute range_low_m = 0.0;
      attribute range_high_m = 1.0;
    }

    part START_20_s : ScheduledCommand {
      doc /* PB-START via DI-101; scheduled demonstration command */
      attribute command_name = "START";
      attribute command_time_s = 20.0;
    }

    part STOP_220_s : ScheduledCommand {
      doc /* PB-STOP via DI-102; scheduled demonstration command */
      attribute command_name = "STOP";
      attribute command_time_s = 220.0;
    }

    part START_280_s : ScheduledCommand {
      doc /* PB-START via DI-101; scheduled demonstration command */
      attribute command_name = "START";
      attribute command_time_s = 280.0;
    }

    part STOP_650_s : ScheduledCommand {
      doc /* PB-STOP via DI-102; scheduled demonstration command */
      attribute command_name = "STOP";
      attribute command_time_s = 650.0;
    }

    part SHUT_700_s : ScheduledCommand {
      doc /* PB-SHUT via DI-103; scheduled demonstration command */
      attribute command_name = "SHUT";
      attribute command_time_s = 700.0;
    }

    part PLC_101 {
      doc /* PLC-101, tankController, controller, PLC, tankController (PLC-101) */
      attribute scan_time_s : ScalarValues::Real = 0.1;
      attribute output_power_available : ScalarValues::Boolean = true;
      attribute valve1_open_cmd : ScalarValues::Boolean = false;
      attribute valve2_open_cmd : ScalarValues::Boolean = false;
      attribute valve3_open_cmd : ScalarValues::Boolean = false;
      attribute controller_state_id : ScalarValues::Integer = 0;
      attribute wait_remaining_s : ScalarValues::Real = 0.0;
      attribute stored_resume_state_id : ScalarValues::Integer = 0;
      attribute paused_from_wait_state : ScalarValues::Boolean = false;
      attribute start_20_s_received : ScalarValues::Boolean = false;
      attribute stop_220_s_received : ScalarValues::Boolean = false;
      attribute start_280_s_received : ScalarValues::Boolean = false;
      attribute stop_650_s_received : ScalarValues::Boolean = false;
      attribute shut_700_s_received : ScalarValues::Boolean = false;

      state OperatingCycle {
        entry; then IDLE;

        state IDLE;
        state FILL_T1;
        state WAIT_AFTER_FILL;
        state TRANSFER_T1_T2;
        state WAIT_AFTER_TRANSFER;
        state DRAIN_T2;
        state WAIT_AFTER_DRAIN;
        state PAUSED;
        state SHUTDOWN;

        transition IDLE_to_FILL_T1_on_START_20_s
          first IDLE
          if start_20_s_received
          do action { assign valve1_open_cmd := true; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 1; assign wait_remaining_s := 0.0; assign stored_resume_state_id := 0; assign paused_from_wait_state := false; }
          then FILL_T1;

        transition FILL_T1_to_WAIT_AFTER_FILL
          first FILL_T1
          if LT_101.measured_level_m >= TK_101.high_level_setpoint_m
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 2; assign wait_remaining_s := 10.0; }
          then WAIT_AFTER_FILL;

        transition WAIT_AFTER_FILL_to_TRANSFER_T1_T2
          first WAIT_AFTER_FILL
          if wait_remaining_s <= 0.0
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := false; assign controller_state_id := 3; assign wait_remaining_s := 0.0; }
          then TRANSFER_T1_T2;

        transition TRANSFER_T1_T2_to_WAIT_AFTER_TRANSFER
          first TRANSFER_T1_T2
          if LT_101.measured_level_m <= TK_101.low_level_setpoint_m
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 4; assign wait_remaining_s := 12.0; }
          then WAIT_AFTER_TRANSFER;

        transition WAIT_AFTER_TRANSFER_to_DRAIN_T2
          first WAIT_AFTER_TRANSFER
          if wait_remaining_s <= 0.0
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := true; assign controller_state_id := 5; assign wait_remaining_s := 0.0; }
          then DRAIN_T2;

        transition DRAIN_T2_to_WAIT_AFTER_DRAIN
          first DRAIN_T2
          if LT_102.measured_level_m <= TK_102.low_level_setpoint_m
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 6; assign wait_remaining_s := 8.0; }
          then WAIT_AFTER_DRAIN;

        transition WAIT_AFTER_DRAIN_to_FILL_T1
          first WAIT_AFTER_DRAIN
          if wait_remaining_s <= 0.0
          do action { assign valve1_open_cmd := true; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 1; assign wait_remaining_s := 0.0; }
          then FILL_T1;

        transition FILL_T1_to_PAUSED_on_STOP_220_s
          first FILL_T1
          if stop_220_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 1; assign paused_from_wait_state := false; }
          then PAUSED;

        transition WAIT_AFTER_FILL_to_PAUSED_on_STOP_220_s
          first WAIT_AFTER_FILL
          if stop_220_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 2; assign paused_from_wait_state := true; }
          then PAUSED;

        transition TRANSFER_T1_T2_to_PAUSED_on_STOP_220_s
          first TRANSFER_T1_T2
          if stop_220_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 3; assign paused_from_wait_state := false; }
          then PAUSED;

        transition WAIT_AFTER_TRANSFER_to_PAUSED_on_STOP_220_s
          first WAIT_AFTER_TRANSFER
          if stop_220_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 4; assign paused_from_wait_state := true; }
          then PAUSED;

        transition DRAIN_T2_to_PAUSED_on_STOP_220_s
          first DRAIN_T2
          if stop_220_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 5; assign paused_from_wait_state := false; }
          then PAUSED;

        transition WAIT_AFTER_DRAIN_to_PAUSED_on_STOP_220_s
          first WAIT_AFTER_DRAIN
          if stop_220_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 6; assign paused_from_wait_state := true; }
          then PAUSED;

        transition FILL_T1_to_PAUSED_on_STOP_650_s
          first FILL_T1
          if stop_650_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 1; assign paused_from_wait_state := false; }
          then PAUSED;

        transition WAIT_AFTER_FILL_to_PAUSED_on_STOP_650_s
          first WAIT_AFTER_FILL
          if stop_650_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 2; assign paused_from_wait_state := true; }
          then PAUSED;

        transition TRANSFER_T1_T2_to_PAUSED_on_STOP_650_s
          first TRANSFER_T1_T2
          if stop_650_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 3; assign paused_from_wait_state := false; }
          then PAUSED;

        transition WAIT_AFTER_TRANSFER_to_PAUSED_on_STOP_650_s
          first WAIT_AFTER_TRANSFER
          if stop_650_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 4; assign paused_from_wait_state := true; }
          then PAUSED;

        transition DRAIN_T2_to_PAUSED_on_STOP_650_s
          first DRAIN_T2
          if stop_650_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 5; assign paused_from_wait_state := false; }
          then PAUSED;

        transition WAIT_AFTER_DRAIN_to_PAUSED_on_STOP_650_s
          first WAIT_AFTER_DRAIN
          if stop_650_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 7; assign stored_resume_state_id := 6; assign paused_from_wait_state := true; }
          then PAUSED;

        transition IDLE_to_SHUTDOWN_on_SHUT_700_s
          first IDLE
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign wait_remaining_s := 0.0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition FILL_T1_to_SHUTDOWN_on_SHUT_700_s
          first FILL_T1
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign wait_remaining_s := 0.0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition WAIT_AFTER_FILL_to_SHUTDOWN_on_SHUT_700_s
          first WAIT_AFTER_FILL
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition TRANSFER_T1_T2_to_SHUTDOWN_on_SHUT_700_s
          first TRANSFER_T1_T2
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign wait_remaining_s := 0.0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition WAIT_AFTER_TRANSFER_to_SHUTDOWN_on_SHUT_700_s
          first WAIT_AFTER_TRANSFER
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition DRAIN_T2_to_SHUTDOWN_on_SHUT_700_s
          first DRAIN_T2
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign wait_remaining_s := 0.0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition WAIT_AFTER_DRAIN_to_SHUTDOWN_on_SHUT_700_s
          first WAIT_AFTER_DRAIN
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition PAUSED_to_SHUTDOWN_on_SHUT_700_s
          first PAUSED
          if shut_700_s_received
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 0; assign wait_remaining_s := 0.0; assign paused_from_wait_state := false; }
          then SHUTDOWN;

        transition PAUSED_to_FILL_T1_on_START_280_s
          first PAUSED
          if start_280_s_received and stored_resume_state_id == 1
          do action { assign valve1_open_cmd := true; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 1; }
          then FILL_T1;

        transition PAUSED_to_WAIT_AFTER_FILL_on_START_280_s
          first PAUSED
          if start_280_s_received and stored_resume_state_id == 2
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 2; }
          then WAIT_AFTER_FILL;

        transition PAUSED_to_TRANSFER_T1_T2_on_START_280_s
          first PAUSED
          if start_280_s_received and stored_resume_state_id == 3
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := false; assign controller_state_id := 3; }
          then TRANSFER_T1_T2;

        transition PAUSED_to_WAIT_AFTER_TRANSFER_on_START_280_s
          first PAUSED
          if start_280_s_received and stored_resume_state_id == 4
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 4; }
          then WAIT_AFTER_TRANSFER;

        transition PAUSED_to_DRAIN_T2_on_START_280_s
          first PAUSED
          if start_280_s_received and stored_resume_state_id == 5
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := true; assign controller_state_id := 5; }
          then DRAIN_T2;

        transition PAUSED_to_WAIT_AFTER_DRAIN_on_START_280_s
          first PAUSED
          if start_280_s_received and stored_resume_state_id == 6
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 6; }
          then WAIT_AFTER_DRAIN;

        transition SHUTDOWN_to_IDLE
          first SHUTDOWN
          if LT_101.measured_level_m <= TK_101.low_level_setpoint_m and LT_102.measured_level_m <= TK_102.low_level_setpoint_m
          do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_id := 0; assign wait_remaining_s := 0.0; assign stored_resume_state_id := 0; assign paused_from_wait_state := false; }
          then IDLE;
      }
    }

    connect SRC_101 to XV_101;
    connect XV_101 to TK_101;
    connect TK_101 to XV_102;
    connect XV_102 to TK_102;
    connect TK_102 to XV_103;
    connect XV_103 to DRN_101;
    connect TK_101 to LT_101;
    connect TK_102 to LT_102;
    connect LT_101 to PLC_101;
    connect LT_102 to PLC_101;
    connect START_20_s to PLC_101;
    connect STOP_220_s to PLC_101;
    connect START_280_s to PLC_101;
    connect STOP_650_s to PLC_101;
    connect SHUT_700_s to PLC_101;
    connect PLC_101 to XV_101;
    connect PLC_101 to XV_102;
    connect PLC_101 to XV_103;

    attribute simulation_start_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_s : ScalarValues::Real = 900.0;
    attribute simulation_output_intervals : ScalarValues::Integer = 1000;
    attribute solver_tolerance_assumption : ScalarValues::Real = 0.000001;

    attribute time_s : ScalarValues::Real;
    attribute tank1_level_m : ScalarValues::Real = 0.05;
    attribute tank2_level_m : ScalarValues::Real = 0.05;
    attribute valve1_open_cmd_report : ScalarValues::Integer = 0;
    attribute valve2_open_cmd_report : ScalarValues::Integer = 0;
    attribute valve3_open_cmd_report : ScalarValues::Integer = 0;
    attribute controller_state_id_report : ScalarValues::Integer = 0;
    attribute wait_remaining_s_report : ScalarValues::Real = 0.0;

    doc /* Resolved topology from engineering register interface matrix: SRC-101 -> XV-101 -> TK-101 -> XV-102 -> TK-102 -> XV-103 -> DRN-101. Control diagram note text suggesting ambient1 connected_to valve3 and valve3 connected_to tank2 is discarded for fluid topology because it is lower-authority and inconsistent with the engineering register, requirement specification, control diagram direction elsewhere, and legacy architecture draft. */

    doc /* Continuous plant relationship retained for later executable stages under approved assumption: dh1_dt = (u1*qFill - u2*qTransfer)/A1 with A1 = 1.2 m^2, qFill = 0.0060 m^3/s, qTransfer = 0.0045 m^3/s; dh2_dt = (u2*qTransfer - u3*qDrain)/A2 with A2 = 1.4 m^2, qDrain = 0.0050 m^3/s. u1, u2, u3 are Boolean valve-open commands represented numerically as 1 when open and 0 when closed. Initial conditions are h1(0) = 0.05 m and h2(0) = 0.05 m. No overflow, saturation, leakage, compressibility, or pressure-dependent flow relation is added because the notes do not establish them. */

    requirement Mutual_Exclusion_Normal_Valves {
      doc /* XV-101 shall never be commanded open while XV-102 is open. During normal automatic operation, XV-102 and XV-103 shall not be open simultaneously. During SHUTDOWN, XV-102 and XV-103 may be open simultaneously. Sources: engineering brief interlocks and prohibitions; AC-08 narrative scope. */
    }

    requirement Power_Loss_Fail_Closed {
      doc /* On loss of controller power, all process valves shall move to or remain in the closed position; equivalently, output commands shall be false and the actuators fail closed. Source: engineering brief interlocks and prohibitions; valve family fail-closed behavior. */
    }

    requirement Shutdown_Command_Priority {
      doc /* SHUT has highest priority. A valid SHUT edge from any non-shutdown state immediately abandons stored resume context and enters SHUTDOWN. START and STOP received during SHUTDOWN are ignored until shutdown is complete. STOP has higher priority than START and is accepted from any normal running or wait state, placing the controller in PAUSED with all valve outputs false. START while already running is ignored. Sources: design notes, engineering register, design review minutes, resolved understanding. */
    }

    requirement Pause_Resume_Wait_Retention {
      doc /* If STOP occurs in a wait state, the remaining delay is retained and frozen. START from PAUSED restores the interrupted stored state, and a resumed wait continues from the remaining delay rather than restarting. Sources: design note, engineering register, design review minutes. */
    }
  }

  part system : Two_Tank_System;
}