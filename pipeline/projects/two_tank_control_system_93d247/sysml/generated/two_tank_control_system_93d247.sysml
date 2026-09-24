package Two_Tank_Sequence_Controller {
  part def BoundarySource;
  part def BoundarySink;

  part def Valve {
    attribute nominal_flow_m3_per_s : ScalarValues::Real;
    attribute stroke_open_s : ScalarValues::Real;
    attribute stroke_close_s : ScalarValues::Real;
    attribute command_open : ScalarValues::Boolean;
    attribute fail_closed_on_power_loss : ScalarValues::Boolean;
    doc /* Hackathon simulation neglects dynamic stroke and uses command_open directly as an ideal Boolean flow switch. Datasheet stroke times are retained as sourced parameters only. */
  }

  part def Tank {
    attribute cross_section_area_m2 : ScalarValues::Real;
    attribute height_m : ScalarValues::Real;
    attribute max_working_level_m : ScalarValues::Real;
    attribute level_m : ScalarValues::Real;
    attribute initial_level_m : ScalarValues::Real;
    attribute transmitter_range_low_m : ScalarValues::Real;
    attribute transmitter_range_high_m : ScalarValues::Real;
  }

  part def LevelTransmitter {
    attribute measured_level_m : ScalarValues::Real;
    attribute range_low_m : ScalarValues::Real;
    attribute range_high_m : ScalarValues::Real;
    attribute valid_low_m : ScalarValues::Real;
    attribute valid_high_m : ScalarValues::Real;
  }

  part def OperatorCommand {
    attribute signal : ScalarValues::Boolean;
    attribute momentary : ScalarValues::Boolean;
  }

  part def Controller {
    attribute scan_time_s : ScalarValues::Real;
    attribute valve1_cmd : ScalarValues::Boolean;
    attribute valve2_cmd : ScalarValues::Boolean;
    attribute valve3_cmd : ScalarValues::Boolean;
    attribute controller_state_id : ScalarValues::Integer;
    attribute wait_remaining_s : ScalarValues::Real;
    attribute T1_High_m : ScalarValues::Real;
    attribute T1_Low_m : ScalarValues::Real;
    attribute T2_Low_m : ScalarValues::Real;
    attribute WAIT_AFTER_FILL_s : ScalarValues::Real;
    attribute WAIT_AFTER_TRANSFER_s : ScalarValues::Real;
    attribute WAIT_AFTER_DRAIN_s : ScalarValues::Real;
    attribute stored_resume_state_id : ScalarValues::Integer;
    attribute stored_wait_remaining_s : ScalarValues::Real;
    attribute start_edge : ScalarValues::Boolean;
    attribute stop_edge : ScalarValues::Boolean;
    attribute shut_edge : ScalarValues::Boolean;
    attribute LT_101_measured_level_m : ScalarValues::Real;
    attribute LT_102_measured_level_m : ScalarValues::Real;

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

      transition IDLE_to_FILL_T1
        first IDLE
        if start_edge == true
        do action { assign valve1_cmd := true; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 1; assign wait_remaining_s := 0.0; }
        then FILL_T1;

      transition FILL_T1_to_WAIT_AFTER_FILL
        first FILL_T1
        if LT_101_measured_level_m >= T1_High_m
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 2; assign wait_remaining_s := WAIT_AFTER_FILL_s; }
        then WAIT_AFTER_FILL;

      transition WAIT_AFTER_FILL_to_TRANSFER_T1_T2
        first WAIT_AFTER_FILL
        if wait_remaining_s <= 0.0
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := false; assign controller_state_id := 3; assign wait_remaining_s := 0.0; }
        then TRANSFER_T1_T2;

      transition TRANSFER_T1_T2_to_WAIT_AFTER_TRANSFER
        first TRANSFER_T1_T2
        if LT_101_measured_level_m <= T1_Low_m
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 4; assign wait_remaining_s := WAIT_AFTER_TRANSFER_s; }
        then WAIT_AFTER_TRANSFER;

      transition WAIT_AFTER_TRANSFER_to_DRAIN_T2
        first WAIT_AFTER_TRANSFER
        if wait_remaining_s <= 0.0
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := true; assign controller_state_id := 5; assign wait_remaining_s := 0.0; }
        then DRAIN_T2;

      transition DRAIN_T2_to_WAIT_AFTER_DRAIN
        first DRAIN_T2
        if LT_102_measured_level_m <= T2_Low_m
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 6; assign wait_remaining_s := WAIT_AFTER_DRAIN_s; }
        then WAIT_AFTER_DRAIN;

      transition WAIT_AFTER_DRAIN_to_FILL_T1
        first WAIT_AFTER_DRAIN
        if wait_remaining_s <= 0.0
        do action { assign valve1_cmd := true; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 1; assign wait_remaining_s := 0.0; }
        then FILL_T1;

      transition FILL_T1_to_PAUSED
        first FILL_T1
        if stop_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign stored_resume_state_id := 1; assign stored_wait_remaining_s := 0.0; assign controller_state_id := 7; assign wait_remaining_s := 0.0; }
        then PAUSED;

      transition WAIT_AFTER_FILL_to_PAUSED
        first WAIT_AFTER_FILL
        if stop_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign stored_resume_state_id := 2; assign stored_wait_remaining_s := wait_remaining_s; assign controller_state_id := 7; }
        then PAUSED;

      transition TRANSFER_T1_T2_to_PAUSED
        first TRANSFER_T1_T2
        if stop_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign stored_resume_state_id := 3; assign stored_wait_remaining_s := 0.0; assign controller_state_id := 7; assign wait_remaining_s := 0.0; }
        then PAUSED;

      transition WAIT_AFTER_TRANSFER_to_PAUSED
        first WAIT_AFTER_TRANSFER
        if stop_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign stored_resume_state_id := 4; assign stored_wait_remaining_s := wait_remaining_s; assign controller_state_id := 7; }
        then PAUSED;

      transition DRAIN_T2_to_PAUSED
        first DRAIN_T2
        if stop_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign stored_resume_state_id := 5; assign stored_wait_remaining_s := 0.0; assign controller_state_id := 7; assign wait_remaining_s := 0.0; }
        then PAUSED;

      transition WAIT_AFTER_DRAIN_to_PAUSED
        first WAIT_AFTER_DRAIN
        if stop_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign stored_resume_state_id := 6; assign stored_wait_remaining_s := wait_remaining_s; assign controller_state_id := 7; }
        then PAUSED;

      transition PAUSED_to_FILL_T1_resume
        first PAUSED
        if start_edge == true and stored_resume_state_id == 1
        do action { assign valve1_cmd := true; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 1; assign wait_remaining_s := 0.0; }
        then FILL_T1;

      transition PAUSED_to_WAIT_AFTER_FILL_resume
        first PAUSED
        if start_edge == true and stored_resume_state_id == 2
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 2; assign wait_remaining_s := stored_wait_remaining_s; }
        then WAIT_AFTER_FILL;

      transition PAUSED_to_TRANSFER_T1_T2_resume
        first PAUSED
        if start_edge == true and stored_resume_state_id == 3
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := false; assign controller_state_id := 3; assign wait_remaining_s := 0.0; }
        then TRANSFER_T1_T2;

      transition PAUSED_to_WAIT_AFTER_TRANSFER_resume
        first PAUSED
        if start_edge == true and stored_resume_state_id == 4
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 4; assign wait_remaining_s := stored_wait_remaining_s; }
        then WAIT_AFTER_TRANSFER;

      transition PAUSED_to_DRAIN_T2_resume
        first PAUSED
        if start_edge == true and stored_resume_state_id == 5
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := true; assign controller_state_id := 5; assign wait_remaining_s := 0.0; }
        then DRAIN_T2;

      transition PAUSED_to_WAIT_AFTER_DRAIN_resume
        first PAUSED
        if start_edge == true and stored_resume_state_id == 6
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 6; assign wait_remaining_s := stored_wait_remaining_s; }
        then WAIT_AFTER_DRAIN;

      transition IDLE_to_SHUTDOWN
        first IDLE
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition FILL_T1_to_SHUTDOWN
        first FILL_T1
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition WAIT_AFTER_FILL_to_SHUTDOWN
        first WAIT_AFTER_FILL
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition TRANSFER_T1_T2_to_SHUTDOWN
        first TRANSFER_T1_T2
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition WAIT_AFTER_TRANSFER_to_SHUTDOWN
        first WAIT_AFTER_TRANSFER
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition DRAIN_T2_to_SHUTDOWN
        first DRAIN_T2
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition WAIT_AFTER_DRAIN_to_SHUTDOWN
        first WAIT_AFTER_DRAIN
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition PAUSED_to_SHUTDOWN
        first PAUSED
        if shut_edge == true
        do action { assign valve1_cmd := false; assign valve2_cmd := true; assign valve3_cmd := true; assign controller_state_id := 8; assign stored_resume_state_id := 8; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then SHUTDOWN;

      transition SHUTDOWN_to_IDLE
        first SHUTDOWN
        if LT_101_measured_level_m <= T1_Low_m and LT_102_measured_level_m <= T2_Low_m
        do action { assign valve1_cmd := false; assign valve2_cmd := false; assign valve3_cmd := false; assign controller_state_id := 0; assign stored_resume_state_id := 0; assign stored_wait_remaining_s := 0.0; assign wait_remaining_s := 0.0; }
        then IDLE;
    }
  }

  part Two_Tank_Sequence_Controller_System {
    attribute time_s : ScalarValues::Real;
    attribute experiment_start_time_s : ScalarValues::Real = 0.0;
    attribute experiment_stop_time_s : ScalarValues::Real = 900.0;
    attribute sample_interval_s : ScalarValues::Real = 0.1;
    attribute tank1_level_m : ScalarValues::Real = 0.05;
    attribute tank2_level_m : ScalarValues::Real = 0.05;
    doc /* Demonstration scenario is a 900 s run from 0 s through 900 s. Dataset timing is reference evidence only, not a forcing input schedule. */

    part SRC_101 : BoundarySource;
    part DRN_101 : BoundarySink;

    part XV_101 : Valve {
      attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.006;
      attribute stroke_open_s : ScalarValues::Real = 0.8;
      attribute stroke_close_s : ScalarValues::Real = 0.6;
      attribute command_open : ScalarValues::Boolean = false;
      attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
      doc /* Canonical name XV_101, alias V1, valve1. */
    }

    part XV_102 : Valve {
      attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0045;
      attribute stroke_open_s : ScalarValues::Real = 0.8;
      attribute stroke_close_s : ScalarValues::Real = 0.6;
      attribute command_open : ScalarValues::Boolean = false;
      attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
      doc /* Canonical name XV_102, alias V2, valve2. */
    }

    part XV_103 : Valve {
      attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0050;
      attribute stroke_open_s : ScalarValues::Real = 0.8;
      attribute stroke_close_s : ScalarValues::Real = 0.6;
      attribute command_open : ScalarValues::Boolean = false;
      attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
      doc /* Canonical name XV_103, alias V3, valve3. Higher-authority topology places Tank 2 discharge through XV_103 to DRN_101; conflicting diagram relation was treated as non-governing inconsistency. */
    }

    part TK_101 : Tank {
      attribute cross_section_area_m2 : ScalarValues::Real = 1.2;
      attribute height_m : ScalarValues::Real = 1.0;
      attribute max_working_level_m : ScalarValues::Real = 0.9;
      attribute level_m : ScalarValues::Real = 0.05;
      attribute initial_level_m : ScalarValues::Real = 0.05;
      attribute transmitter_range_low_m : ScalarValues::Real = 0.0;
      attribute transmitter_range_high_m : ScalarValues::Real = 1.0;
      doc /* Canonical name TK_101, aliases Tank 1, tank1, T1. */
    }

    part TK_102 : Tank {
      attribute cross_section_area_m2 : ScalarValues::Real = 1.4;
      attribute height_m : ScalarValues::Real = 1.0;
      attribute max_working_level_m : ScalarValues::Real = 0.9;
      attribute level_m : ScalarValues::Real = 0.05;
      attribute initial_level_m : ScalarValues::Real = 0.05;
      attribute transmitter_range_low_m : ScalarValues::Real = 0.0;
      attribute transmitter_range_high_m : ScalarValues::Real = 1.0;
      doc /* Canonical name TK_102, aliases Tank 2, tank2, T2. */
    }

    part LT_101 : LevelTransmitter {
      attribute measured_level_m : ScalarValues::Real = 0.05;
      attribute range_low_m : ScalarValues::Real = 0.0;
      attribute range_high_m : ScalarValues::Real = 1.0;
      attribute valid_low_m : ScalarValues::Real = 0.0;
      attribute valid_high_m : ScalarValues::Real = 1.0;
      doc /* Canonical name LT_101, aliases level1, AI_101. Measures TK_101 level and sends measurement to PLC_101. */
    }

    part LT_102 : LevelTransmitter {
      attribute measured_level_m : ScalarValues::Real = 0.05;
      attribute range_low_m : ScalarValues::Real = 0.0;
      attribute range_high_m : ScalarValues::Real = 1.0;
      attribute valid_low_m : ScalarValues::Real = 0.0;
      attribute valid_high_m : ScalarValues::Real = 1.0;
      doc /* Canonical name LT_102, aliases level2, AI_102. Measures TK_102 level and sends measurement to PLC_101. */
    }

    part PB_START_DI_101 : OperatorCommand {
      attribute signal : ScalarValues::Boolean;
      attribute momentary : ScalarValues::Boolean = true;
      doc /* START momentary operator command, aliases PB_START, DI_101. Demonstration command times are 20 s and 280 s. */
    }

    part PB_STOP_DI_102 : OperatorCommand {
      attribute signal : ScalarValues::Boolean;
      attribute momentary : ScalarValues::Boolean = true;
      doc /* STOP momentary operator command, aliases PB_STOP, DI_102. Demonstration command times are 220 s and 650 s. */
    }

    part PB_SHUT_DI_103 : OperatorCommand {
      attribute signal : ScalarValues::Boolean;
      attribute momentary : ScalarValues::Boolean = true;
      doc /* SHUT momentary operator command, aliases PB_SHUT, DI_103. Demonstration command time is 700 s. */
    }

    part PLC_101 : Controller {
      attribute scan_time_s : ScalarValues::Real = 0.1;
      attribute valve1_cmd : ScalarValues::Boolean = false;
      attribute valve2_cmd : ScalarValues::Boolean = false;
      attribute valve3_cmd : ScalarValues::Boolean = false;
      attribute controller_state_id : ScalarValues::Integer = 0;
      attribute wait_remaining_s : ScalarValues::Real = 0.0;
      attribute T1_High_m : ScalarValues::Real = 0.80;
      attribute T1_Low_m : ScalarValues::Real = 0.05;
      attribute T2_Low_m : ScalarValues::Real = 0.05;
      attribute WAIT_AFTER_FILL_s : ScalarValues::Real = 10.0;
      attribute WAIT_AFTER_TRANSFER_s : ScalarValues::Real = 12.0;
      attribute WAIT_AFTER_DRAIN_s : ScalarValues::Real = 8.0;
      attribute stored_resume_state_id : ScalarValues::Integer = 0;
      attribute stored_wait_remaining_s : ScalarValues::Real = 0.0;
      attribute start_edge : ScalarValues::Boolean;
      attribute stop_edge : ScalarValues::Boolean;
      attribute shut_edge : ScalarValues::Boolean;
      attribute LT_101_measured_level_m : ScalarValues::Real = 0.05;
      attribute LT_102_measured_level_m : ScalarValues::Real = 0.05;
      doc /* Canonical name PLC_101, aliases tankController, Controller, PLC, tankController1. START while already running is ignored. STOP is accepted from any normal running or wait state and places the controller in PAUSED with all valve outputs false. PAUSED preserves the interrupted state and freezes any active wait timer remaining value. START after STOP resumes the interrupted state rather than forcing a new initialization. During SHUTDOWN, START and STOP are ignored until shutdown is complete. Command precedence is SHUT greater than STOP greater than START. wait_remaining_s is represented as a continuously decreasing remaining-time variable while a wait state is active, frozen during PAUSED, and zero outside wait contexts after transition completion. */
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
    connect PB_START_DI_101 to PLC_101;
    connect PB_STOP_DI_102 to PLC_101;
    connect PB_SHUT_DI_103 to PLC_101;
    connect PLC_101 to XV_101;
    connect PLC_101 to XV_102;
    connect PLC_101 to XV_103;

    requirement RQ_Command_Precedence {
      doc /* SHUT has priority over STOP and START; STOP has priority over START. Source: resolved shutdown behavior and priorities in the engineering brief. */
    }

    requirement RQ_Stop_Pause_Resume {
      doc /* STOP from any normal running or wait state places PLC_101 in PAUSED with all valve outputs false. PAUSED preserves interrupted sequence state, and if interruption occurred during WAIT_AFTER_FILL, WAIT_AFTER_TRANSFER, or WAIT_AFTER_DRAIN it preserves the remaining timer value. START after STOP resumes the interrupted state rather than restarting from IDLE or FILL_T1. Source: resolved pause and resume behavior. */
    }

    requirement RQ_Shutdown_Behavior {
      doc /* Any valid SHUT edge from any non_SHUTDOWN state immediately abandons stored resume context and enters SHUTDOWN with XV_101 commanded closed and XV_102 and XV_103 commanded open. While SHUTDOWN is active, XV_101 remains inhibited and START and STOP are ignored until both TK_101 and TK_102 satisfy low-level completion conditions, after which the controller returns to IDLE with all valves closed. Source: resolved shutdown behavior and priorities; URS_CTL_005 context. */
    }

    requirement RQ_Valve_Command_Exclusion {
      doc /* XV_101 shall never be commanded open while XV_102 is open. During normal automatic operation, XV_102 and XV_103 shall not be open simultaneously. The XV_102 and XV_103 simultaneous-open restriction is waived in SHUTDOWN. Source: valve-command prohibitions and allowed concurrency; AC_08. */
    }

    requirement RQ_Fail_Closed_On_Power_Loss {
      doc /* On loss of controller power, all process valves move to or remain closed; simulation representation is false output commands. No demonstration power-loss command schedule is provided. Source: engineering register and valve-command prohibitions section. */
    }

    doc /* Physical balances adopted from archived legacy model because they are explicit note evidence and unit-consistent with current geometry and nominal flows when valves are ideal Boolean flow switches: d tank1_level_m dt = (valve1_cmd*qFill - valve2_cmd*qTransfer)/A1 with qFill=0.006 m3/s, qTransfer=0.0045 m3/s, A1=1.2 m2; d tank2_level_m dt = (valve2_cmd*qTransfer - valve3_cmd*qDrain)/A2 with qDrain=0.0050 m3/s, A2=1.4 m2. Derived normal-state rates from those balances are Tank 1 fill 0.005 m/s, Tank 1 transfer depletion 0.00375 m/s, Tank 2 transfer rise about 0.0032142857 m/s, and Tank 2 drain depletion about 0.0035714286 m/s. Reported-variable contract for later stages: time_s, tank1_level_m, tank2_level_m, valve1_cmd, valve2_cmd, valve3_cmd, controller_state_id with mapping IDLE=0 FILL_T1=1 WAIT_AFTER_FILL=2 TRANSFER_T1_T2=3 WAIT_AFTER_TRANSFER=4 DRAIN_T2=5 WAIT_AFTER_DRAIN=6 PAUSED=7 SHUTDOWN=8, and wait_remaining_s. Demonstration schedule from current requirements register and approved test procedure is START at 20 s, STOP at 220 s, START at 280 s, STOP at 650 s, and SHUT at 700 s for a 900 s run. This schedule is evidenced for the demonstration scenario; the recorded dataset is reference evidence only and is not a forcing input schedule. */
  }
}
