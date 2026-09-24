package Two_Tank_Fill_Transfer_Drain_Controller_Model {

  part def BoundarySource {
    doc /* SRC-101 upstream boundary source */
  }

  part def BoundarySink {
    doc /* DRN-101 downstream boundary sink, alias ambient1 */
  }

  part def Tank {
    attribute cross_section_area_m2 : ScalarValues::Real;
    attribute height_m : ScalarValues::Real;
    attribute level_m : ScalarValues::Real;
    attribute initial_level_m : ScalarValues::Real;
    attribute low_level_setpoint_m : ScalarValues::Real;
    attribute level_valid_min_m : ScalarValues::Real;
    attribute level_valid_max_m : ScalarValues::Real;
  }

  part def Valve {
    attribute open_cmd : ScalarValues::Boolean;
    attribute nominal_flow_m3_per_s : ScalarValues::Real;
    attribute open_stroke_time_s : ScalarValues::Real;
    attribute close_stroke_time_s : ScalarValues::Real;
    attribute fail_closed_on_power_loss : ScalarValues::Boolean;
  }

  part def LevelTransmitter {
    attribute measured_level_m : ScalarValues::Real;
    attribute update_period_s : ScalarValues::Real;
    attribute signal_min_m : ScalarValues::Real;
    attribute signal_max_m : ScalarValues::Real;
  }

  part def PushButtonCommand {
    attribute pulse_cmd : ScalarValues::Boolean;
    doc /* Momentary operator command */
  }

  part def AnalogInputChannel {
    doc /* PLC analog input channel */
  }

  part def DigitalInputChannel {
    doc /* PLC digital input channel */
  }

  part def DigitalOutputChannel {
    doc /* PLC digital output channel */
  }

  part def PLC_Controller {
    attribute scan_time_s : ScalarValues::Real;
    attribute valve1_open_cmd : ScalarValues::Boolean;
    attribute valve2_open_cmd : ScalarValues::Boolean;
    attribute valve3_open_cmd : ScalarValues::Boolean;
    attribute cmd_start : ScalarValues::Boolean;
    attribute cmd_stop : ScalarValues::Boolean;
    attribute cmd_shut : ScalarValues::Boolean;
    attribute wait_remaining_s : ScalarValues::Real;
    attribute paused_wait_remaining_s : ScalarValues::Real;
    attribute resume_to_fill_t1 : ScalarValues::Boolean;
    attribute resume_to_wait_after_fill : ScalarValues::Boolean;
    attribute resume_to_transfer_t1_t2 : ScalarValues::Boolean;
    attribute resume_to_wait_after_transfer : ScalarValues::Boolean;
    attribute resume_to_drain_t2 : ScalarValues::Boolean;
    attribute resume_to_wait_after_drain : ScalarValues::Boolean;
    attribute controller_state_code : ScalarValues::Integer;
    attribute power_available : ScalarValues::Boolean;
    attribute observed_tank1_level_m : ScalarValues::Real;
    attribute observed_tank2_level_m : ScalarValues::Real;
    attribute observed_t1_low_setpoint_m : ScalarValues::Real;
    attribute observed_t2_low_setpoint_m : ScalarValues::Real;
    attribute observed_t1_high_setpoint_m : ScalarValues::Real;

    doc /* PLC-101 also called tankController, Controller, and Two-Tank Fill/Transfer/Drain Controller. State code reporting convention: IDLE=0, FILL_T1=1, WAIT_AFTER_FILL=2, TRANSFER_T1_T2=3, WAIT_AFTER_TRANSFER=4, DRAIN_T2=5, WAIT_AFTER_DRAIN=6, PAUSED=7, SHUTDOWN=8. START while already running is ignored. START and STOP are ignored during active SHUTDOWN. SHUT has higher priority than STOP, and STOP higher than START. Stored remaining wait time is retained across STOP/START for wait states. This handoff retains explicit wait duration initialization and stored remaining-time attributes; continuous timer countdown realization is deferred to the next stage per human-confirmed answer. */

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
        if cmd_start == true
        do action { assign valve1_open_cmd := true; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 1; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then FILL_T1;

      transition IDLE_to_SHUTDOWN
        first IDLE
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition FILL_T1_to_SHUTDOWN
        first FILL_T1
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition FILL_T1_to_PAUSED
        first FILL_T1
        if cmd_stop == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 7; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := true; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then PAUSED;

      transition FILL_T1_to_WAIT_AFTER_FILL
        first FILL_T1
        if observed_tank1_level_m >= observed_t1_high_setpoint_m
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 2; assign wait_remaining_s := 10.0; }
        then WAIT_AFTER_FILL;

      transition WAIT_AFTER_FILL_to_SHUTDOWN
        first WAIT_AFTER_FILL
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition WAIT_AFTER_FILL_to_PAUSED
        first WAIT_AFTER_FILL
        if cmd_stop == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 7; assign paused_wait_remaining_s := wait_remaining_s; assign wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := true; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then PAUSED;

      transition WAIT_AFTER_FILL_to_TRANSFER_T1_T2
        first WAIT_AFTER_FILL
        if wait_remaining_s <= 0.0
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := false; assign controller_state_code := 3; assign wait_remaining_s := 0.0; }
        then TRANSFER_T1_T2;

      transition TRANSFER_T1_T2_to_SHUTDOWN
        first TRANSFER_T1_T2
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition TRANSFER_T1_T2_to_PAUSED
        first TRANSFER_T1_T2
        if cmd_stop == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 7; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := true; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then PAUSED;

      transition TRANSFER_T1_T2_to_WAIT_AFTER_TRANSFER
        first TRANSFER_T1_T2
        if observed_tank1_level_m <= observed_t1_low_setpoint_m
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 4; assign wait_remaining_s := 12.0; }
        then WAIT_AFTER_TRANSFER;

      transition WAIT_AFTER_TRANSFER_to_SHUTDOWN
        first WAIT_AFTER_TRANSFER
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition WAIT_AFTER_TRANSFER_to_PAUSED
        first WAIT_AFTER_TRANSFER
        if cmd_stop == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 7; assign paused_wait_remaining_s := wait_remaining_s; assign wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := true; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then PAUSED;

      transition WAIT_AFTER_TRANSFER_to_DRAIN_T2
        first WAIT_AFTER_TRANSFER
        if wait_remaining_s <= 0.0
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := true; assign controller_state_code := 5; assign wait_remaining_s := 0.0; }
        then DRAIN_T2;

      transition DRAIN_T2_to_SHUTDOWN
        first DRAIN_T2
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition DRAIN_T2_to_PAUSED
        first DRAIN_T2
        if cmd_stop == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 7; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := true; assign resume_to_wait_after_drain := false; }
        then PAUSED;

      transition DRAIN_T2_to_WAIT_AFTER_DRAIN
        first DRAIN_T2
        if observed_tank2_level_m <= observed_t2_low_setpoint_m
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 6; assign wait_remaining_s := 8.0; }
        then WAIT_AFTER_DRAIN;

      transition WAIT_AFTER_DRAIN_to_SHUTDOWN
        first WAIT_AFTER_DRAIN
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition WAIT_AFTER_DRAIN_to_PAUSED
        first WAIT_AFTER_DRAIN
        if cmd_stop == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 7; assign paused_wait_remaining_s := wait_remaining_s; assign wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := true; }
        then PAUSED;

      transition WAIT_AFTER_DRAIN_to_FILL_T1
        first WAIT_AFTER_DRAIN
        if wait_remaining_s <= 0.0
        do action { assign valve1_open_cmd := true; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 1; assign wait_remaining_s := 0.0; }
        then FILL_T1;

      transition PAUSED_to_SHUTDOWN
        first PAUSED
        if cmd_shut == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := true; assign controller_state_code := 8; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then SHUTDOWN;

      transition PAUSED_to_FILL_T1
        first PAUSED
        if cmd_start == true and resume_to_fill_t1 == true
        do action { assign valve1_open_cmd := true; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 1; assign resume_to_fill_t1 := false; }
        then FILL_T1;

      transition PAUSED_to_WAIT_AFTER_FILL
        first PAUSED
        if cmd_start == true and resume_to_wait_after_fill == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 2; assign wait_remaining_s := paused_wait_remaining_s; assign paused_wait_remaining_s := 0.0; assign resume_to_wait_after_fill := false; }
        then WAIT_AFTER_FILL;

      transition PAUSED_to_TRANSFER_T1_T2
        first PAUSED
        if cmd_start == true and resume_to_transfer_t1_t2 == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := true; assign valve3_open_cmd := false; assign controller_state_code := 3; assign resume_to_transfer_t1_t2 := false; }
        then TRANSFER_T1_T2;

      transition PAUSED_to_WAIT_AFTER_TRANSFER
        first PAUSED
        if cmd_start == true and resume_to_wait_after_transfer == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 4; assign wait_remaining_s := paused_wait_remaining_s; assign paused_wait_remaining_s := 0.0; assign resume_to_wait_after_transfer := false; }
        then WAIT_AFTER_TRANSFER;

      transition PAUSED_to_DRAIN_T2
        first PAUSED
        if cmd_start == true and resume_to_drain_t2 == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := true; assign controller_state_code := 5; assign resume_to_drain_t2 := false; }
        then DRAIN_T2;

      transition PAUSED_to_WAIT_AFTER_DRAIN
        first PAUSED
        if cmd_start == true and resume_to_wait_after_drain == true
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 6; assign wait_remaining_s := paused_wait_remaining_s; assign paused_wait_remaining_s := 0.0; assign resume_to_wait_after_drain := false; }
        then WAIT_AFTER_DRAIN;

      transition SHUTDOWN_to_IDLE
        first SHUTDOWN
        if observed_tank1_level_m <= observed_t1_low_setpoint_m and observed_tank2_level_m <= observed_t2_low_setpoint_m
        do action { assign valve1_open_cmd := false; assign valve2_open_cmd := false; assign valve3_open_cmd := false; assign controller_state_code := 0; assign wait_remaining_s := 0.0; assign paused_wait_remaining_s := 0.0; assign resume_to_fill_t1 := false; assign resume_to_wait_after_fill := false; assign resume_to_transfer_t1_t2 := false; assign resume_to_wait_after_transfer := false; assign resume_to_drain_t2 := false; assign resume_to_wait_after_drain := false; }
        then IDLE;
    }
  }

  part Two_Tank_System {
    attribute time_s : ScalarValues::Real;
    attribute simulation_start_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_s : ScalarValues::Real = 900.0;
    attribute output_intervals : ScalarValues::Integer = 9000;
    doc /* Demonstration scenario horizon 0 s through 900 s with 9000 output intervals retained from merged assumptions so 0.1 s controller scan/update behavior can be represented on the output grid. Required reported variables: time_s [s], tank1_level_m [m], tank2_level_m [m], valve1_open_cmd [0/1], valve2_open_cmd [0/1], valve3_open_cmd [0/1], controller_state_code [-], wait_remaining_s [s], cmd_start [0/1], cmd_stop [0/1], cmd_shut [0/1]. */

    part SRC_101 : BoundarySource;
    part XV_101 : Valve {
      attribute open_cmd : ScalarValues::Boolean = false;
      attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0060;
      attribute open_stroke_time_s : ScalarValues::Real = 0.8;
      attribute close_stroke_time_s : ScalarValues::Real = 0.6;
      attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
      doc /* XV-101 inlet valve V1 valve1 */
    }
    part TK_101 : Tank {
      attribute cross_section_area_m2 : ScalarValues::Real = 1.2;
      attribute height_m : ScalarValues::Real = 1.0;
      attribute level_m : ScalarValues::Real = 0.05;
      attribute initial_level_m : ScalarValues::Real = 0.05;
      attribute low_level_setpoint_m : ScalarValues::Real = 0.05;
      attribute level_valid_min_m : ScalarValues::Real = 0.0;
      attribute level_valid_max_m : ScalarValues::Real = 1.0;
      doc /* TK-101 Tank 1 tank1 T1. Resolved effective high-level setpoint T1_high = 0.80 m is used by PLC-101. */
    }
    part XV_102 : Valve {
      attribute open_cmd : ScalarValues::Boolean = false;
      attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0045;
      attribute open_stroke_time_s : ScalarValues::Real = 0.8;
      attribute close_stroke_time_s : ScalarValues::Real = 0.6;
      attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
      doc /* XV-102 transfer valve V2 valve2 */
    }
    part TK_102 : Tank {
      attribute cross_section_area_m2 : ScalarValues::Real = 1.4;
      attribute height_m : ScalarValues::Real = 1.0;
      attribute level_m : ScalarValues::Real = 0.05;
      attribute initial_level_m : ScalarValues::Real = 0.05;
      attribute low_level_setpoint_m : ScalarValues::Real = 0.05;
      attribute level_valid_min_m : ScalarValues::Real = 0.0;
      attribute level_valid_max_m : ScalarValues::Real = 1.0;
      doc /* TK-102 Tank 2 tank2 T2 */
    }
    part XV_103 : Valve {
      attribute open_cmd : ScalarValues::Boolean = false;
      attribute nominal_flow_m3_per_s : ScalarValues::Real = 0.0050;
      attribute open_stroke_time_s : ScalarValues::Real = 0.8;
      attribute close_stroke_time_s : ScalarValues::Real = 0.6;
      attribute fail_closed_on_power_loss : ScalarValues::Boolean = true;
      doc /* XV-103 drain valve V3 valve3 */
    }
    part DRN_101 : BoundarySink;

    part LT_101 : LevelTransmitter {
      attribute measured_level_m : ScalarValues::Real = 0.05;
      attribute update_period_s : ScalarValues::Real = 0.1;
      attribute signal_min_m : ScalarValues::Real = 0.0;
      attribute signal_max_m : ScalarValues::Real = 1.0;
      doc /* LT-101 also level1, measures TK-101 level and sends it to PLC-101 through AI-101 */
    }
    part LT_102 : LevelTransmitter {
      attribute measured_level_m : ScalarValues::Real = 0.05;
      attribute update_period_s : ScalarValues::Real = 0.1;
      attribute signal_min_m : ScalarValues::Real = 0.0;
      attribute signal_max_m : ScalarValues::Real = 1.0;
      doc /* LT-102 also level2, measures TK-102 level and sends it to PLC-101 through AI-102 */
    }

    part AI_101 : AnalogInputChannel;
    part AI_102 : AnalogInputChannel;
    part DI_101 : DigitalInputChannel;
    part DI_102 : DigitalInputChannel;
    part DI_103 : DigitalInputChannel;
    part DO_101 : DigitalOutputChannel;
    part DO_102 : DigitalOutputChannel;
    part DO_103 : DigitalOutputChannel;

    part PB_START : PushButtonCommand {
      attribute pulse_cmd : ScalarValues::Boolean;
      doc /* PB-START START. Demonstration scheduled command at 20 s and 280 s. */
    }
    part PB_STOP : PushButtonCommand {
      attribute pulse_cmd : ScalarValues::Boolean;
      doc /* PB-STOP STOP. Demonstration scheduled command at 220 s and 650 s. */
    }
    part PB_SHUT : PushButtonCommand {
      attribute pulse_cmd : ScalarValues::Boolean;
      doc /* PB-SHUT SHUT. Demonstration scheduled command at 700 s. */
    }

    part PLC_101 : PLC_Controller {
      attribute scan_time_s : ScalarValues::Real = 0.1;
      attribute valve1_open_cmd : ScalarValues::Boolean = false;
      attribute valve2_open_cmd : ScalarValues::Boolean = false;
      attribute valve3_open_cmd : ScalarValues::Boolean = false;
      attribute cmd_start : ScalarValues::Boolean;
      attribute cmd_stop : ScalarValues::Boolean;
      attribute cmd_shut : ScalarValues::Boolean;
      attribute wait_remaining_s : ScalarValues::Real = 0.0;
      attribute paused_wait_remaining_s : ScalarValues::Real = 0.0;
      attribute resume_to_fill_t1 : ScalarValues::Boolean = false;
      attribute resume_to_wait_after_fill : ScalarValues::Boolean = false;
      attribute resume_to_transfer_t1_t2 : ScalarValues::Boolean = false;
      attribute resume_to_wait_after_transfer : ScalarValues::Boolean = false;
      attribute resume_to_drain_t2 : ScalarValues::Boolean = false;
      attribute resume_to_wait_after_drain : ScalarValues::Boolean = false;
      attribute controller_state_code : ScalarValues::Integer = 0;
      attribute power_available : ScalarValues::Boolean = true;
      attribute observed_tank1_level_m : ScalarValues::Real = 0.05;
      attribute observed_tank2_level_m : ScalarValues::Real = 0.05;
      attribute observed_t1_low_setpoint_m : ScalarValues::Real = 0.05;
      attribute observed_t2_low_setpoint_m : ScalarValues::Real = 0.05;
      attribute observed_t1_high_setpoint_m : ScalarValues::Real = 0.80;
    }

    connect SRC_101 to XV_101;
    connect XV_101 to TK_101;
    connect TK_101 to XV_102;
    connect XV_102 to TK_102;
    connect TK_102 to XV_103;
    connect XV_103 to DRN_101;

    connect LT_101 to TK_101;
    connect LT_101 to AI_101;
    connect AI_101 to PLC_101;

    connect LT_102 to TK_102;
    connect LT_102 to AI_102;
    connect AI_102 to PLC_101;

    connect PB_START to DI_101;
    connect DI_101 to PLC_101;
    connect PB_STOP to DI_102;
    connect DI_102 to PLC_101;
    connect PB_SHUT to DI_103;
    connect DI_103 to PLC_101;

    connect PLC_101 to DO_101;
    connect DO_101 to XV_101;
    connect PLC_101 to DO_102;
    connect DO_102 to XV_102;
    connect PLC_101 to DO_103;
    connect DO_103 to XV_103;

    requirement RQ_Interlock_V1_V2_Mutual_Exclusion {
      doc /* V1 and V2 shall never be commanded open simultaneously. Source: safety and fail-safe behavior; also reflected by AC-08_no_V1_V2_overlap from 11_09_test_procedure_TP17.txt. */
    }

    requirement RQ_Interlock_V2_V3_Normal_Exclusion {
      doc /* During normal automatic operation, V2 and V3 shall not be open simultaneously. Simultaneous opening of V2 and V3 is permitted only in SHUTDOWN. Source: resolved shutdown concurrency and safety behavior. */
    }

    requirement RQ_Priority_SHUT_over_STOP_over_START {
      doc /* SHUT has higher priority than STOP, and STOP higher than START. SHUT abandons stored resume context. START while already running is ignored. START and STOP received during active SHUTDOWN are ignored until shutdown completes. Source: controlled shutdown behavior and pause and resume behavior. */
    }

    requirement RQ_Fail_Closed_On_Power_Loss {
      doc /* On loss of controller power, or loss of valve actuator electrical power, all process valves move to or remain closed. Output commands shall be false on controller power loss and valve actuators return closed by spring action on loss of electrical power. Source: 01_01_customer_URS.txt, 02_02_engineering_data_register.txt, design note, and valve datasheet. */
    }

    doc /* Canonical entities and aliases: PLC-101 also tankController, Controller, Two-Tank Fill/Transfer/Drain Controller. TK-101 also tank1 T1. TK-102 also tank2 T2. XV-101 inlet valve V1 valve1. XV-102 transfer valve V2 valve2. XV-103 drain valve V3 valve3. LT-101 also level1. LT-102 also level2. PB-START START. PB-STOP STOP. PB-SHUT SHUT.
       Physical topology from 02_02_engineering_data_register.txt IF-HYD-01 through IF-HYD-06: SRC-101 -> XV-101 -> TK-101 -> XV-102 -> TK-102 -> XV-103 -> DRN-101.
       Instrument and command topology: LT-101 -> AI-101 -> PLC-101, LT-102 -> AI-102 -> PLC-101, PB-START -> DI-101 -> PLC-101, PB-STOP -> DI-102 -> PLC-101, PB-SHUT -> DI-103 -> PLC-101, PLC-101 -> DO-101 -> XV-101, PLC-101 -> DO-102 -> XV-102, PLC-101 -> DO-103 -> XV-103.
       Continuous relationships established by archived legacy model 09_07_legacy_tank_demo.txt and retained because no later note contradicts their form:
       TK-101: der(tank1_level_m) = (if valve1_open_cmd then qFill else 0)/A1 - (if valve2_open_cmd then qTransfer else 0)/A1.
       TK-102: der(tank2_level_m) = (if valve2_open_cmd then qTransfer else 0)/A2 - (if valve3_open_cmd then qDrain else 0)/A2.
       Derived from the brief: each term has units (m^3/s)/(m^2) = m/s, so the equations are unit-consistent constant-cross-section level balances.
       No later note provides any head-dependent flow law, leakage term, or compressibility term, so none is added.
       Commanded valve outputs are Boolean open/closed commands. Datasheet stroke times are retained as attributes, but no intermediate effective-flow law during stroking is introduced because the notes do not provide one.
       Resolved timing parameters: delay after TK-101 reaches T1_high before XV-102 opens is 10 s; delay after TK-101 reaches T1_low before XV-103 opens is 12 s; inter-cycle delay after TK-102 reaches T2_low before refilling TK-101 begins is 8 s.
       Demonstration scenario scheduled commands: START at 20 s, STOP at 220 s, START at 280 s, STOP at 650 s, SHUT at 700 s.
       Legacy state aliases from 05_04_control_logic_design_notes.txt: FILL=FILL_T1, HOLD1=WAIT_AFTER_FILL, TRANSFER=TRANSFER_T1_T2, HOLD2=WAIT_AFTER_TRANSFER, DRAIN=DRAIN_T2, HOLD3=WAIT_AFTER_DRAIN. */
  }
}
