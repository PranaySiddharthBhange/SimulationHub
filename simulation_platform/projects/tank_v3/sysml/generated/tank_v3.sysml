package two_tank_demo {
  part def Tank {
    attribute area_m2 : ScalarValues::Real;
    attribute initial_level_m : ScalarValues::Real;
    attribute low_level_m : ScalarValues::Real;
    attribute high_level_m : ScalarValues::Real;
  }

  part def Valve {
    attribute nominal_flow_m3_per_s : ScalarValues::Real;
    attribute de_energize_to_close : ScalarValues::Boolean;
  }

  part def Source {}
  part def Drain {}
  part def Controller {
    attribute plc_scan_s : ScalarValues::Real;
    attribute wait_after_fill_s : ScalarValues::Real;
    attribute wait_after_transfer_s : ScalarValues::Real;
    attribute wait_after_drain_s : ScalarValues::Real;
    attribute initial_state : ScalarValues::String;
    attribute resume_after_stop : ScalarValues::Boolean;
  }

  action def idle_to_fill;
  action def fill_to_wait_after_fill;
  action def wait_after_fill_to_transfer;
  action def transfer_to_wait_after_transfer;
  action def wait_after_transfer_to_drain;
  action def drain_to_wait_after_drain;
  action def wait_after_drain_to_fill;
  action def running_to_paused;
  action def paused_to_resume;
  action def any_to_shutdown;
  action def shutdown_to_idle;

  state def SequenceStates {
    state IDLE;
    state FILL_T1;
    state WAIT_AFTER_FILL;
    state TRANSFER_T1_T2;
    state WAIT_AFTER_TRANSFER;
    state DRAIN_T2;
    state WAIT_AFTER_DRAIN;
    state PAUSED;
    state SHUTDOWN;
  }

  part Two_Tank_Fill_Transfer_Drain_Demo {
    part SRC_101 : Source;
    part XV_101 : Valve {
      attribute nominal_flow_m3_per_s = 0.0060;
      attribute de_energize_to_close = true;
    }
    part TK_101 : Tank {
      attribute area_m2 = 1.20;
      attribute initial_level_m = 0.05;
      attribute low_level_m = 0.05;
      attribute high_level_m = 0.80;
    }
    part XV_102 : Valve {
      attribute nominal_flow_m3_per_s = 0.0045;
      attribute de_energize_to_close = true;
    }
    part TK_102 : Tank {
      attribute area_m2 = 1.40;
      attribute initial_level_m = 0.05;
      attribute low_level_m = 0.05;
      attribute high_level_m = 1.0;
    }
    part XV_103 : Valve {
      attribute nominal_flow_m3_per_s = 0.0050;
      attribute de_energize_to_close = true;
    }
    part DRN_101 : Drain;
    part PLC_101 : Controller {
      attribute plc_scan_s = 0.1;
      attribute wait_after_fill_s = 10.0;
      attribute wait_after_transfer_s = 12.0;
      attribute wait_after_drain_s = 8.0;
      attribute initial_state = "IDLE";
      attribute resume_after_stop = true;
    }
    part sequence : SequenceStates;

    connect SRC_101 to XV_101;
    connect XV_101 to TK_101;
    connect TK_101 to XV_102;
    connect XV_102 to TK_102;
    connect TK_102 to XV_103;
    connect XV_103 to DRN_101;

    action idle_to_fill;
    doc /* IDLE -> FILL_T1, guard: PB_START and not already running, wait: none */

    action fill_to_wait_after_fill;
    doc /* FILL_T1 -> WAIT_AFTER_FILL, guard: LT_101 indicates h1 >= 0.80 m, wait: start 10 s */

    action wait_after_fill_to_transfer;
    doc /* WAIT_AFTER_FILL -> TRANSFER_T1_T2, guard: remaining wait expires, wait: 10 s total */

    action transfer_to_wait_after_transfer;
    doc /* TRANSFER_T1_T2 -> WAIT_AFTER_TRANSFER, guard: LT_101 indicates h1 <= 0.05 m, wait: start 12 s */

    action wait_after_transfer_to_drain;
    doc /* WAIT_AFTER_TRANSFER -> DRAIN_T2, guard: remaining wait expires, wait: 12 s total */

    action drain_to_wait_after_drain;
    doc /* DRAIN_T2 -> WAIT_AFTER_DRAIN, guard: LT_102 indicates h2 <= 0.05 m, wait: start 8 s */

    action wait_after_drain_to_fill;
    doc /* WAIT_AFTER_DRAIN -> FILL_T1, guard: remaining wait expires, wait: 8 s total */

    action running_to_paused;
    doc /* FILL_T1/WAIT_AFTER_FILL/TRANSFER_T1_T2/WAIT_AFTER_TRANSFER/DRAIN_T2/WAIT_AFTER_DRAIN -> PAUSED, guard: PB_STOP, wait: freeze remaining timer if active */

    action paused_to_resume;
    doc /* PAUSED -> prior active state, guard: PB_START, wait: resume frozen timer if prior state was a wait */

    action any_to_shutdown;
    doc /* IDLE/FILL_T1/WAIT_AFTER_FILL/TRANSFER_T1_T2/WAIT_AFTER_TRANSFER/DRAIN_T2/WAIT_AFTER_DRAIN/PAUSED -> SHUTDOWN, guard: PB_SHUT, wait: none */

    action shutdown_to_idle;
    doc /* SHUTDOWN -> IDLE, guard: h1 <= 0.05 m and h2 <= 0.05 m, wait: none */

    requirement DR_02_Safety_Exception {
      doc /* During normal automatic operation, XV_101 and XV_102 shall not be open together, and XV_102 and XV_103 shall not be open together. Exception: SHUTDOWN permits XV_102 and XV_103 open simultaneously while XV_101 remains closed. */
    }

    requirement Stop_Behavior {
      doc /* PB_STOP closes all valves and suspends the current sequence position; PB_START from PAUSED resumes the interrupted active step or remaining wait rather than restarting the cycle. */
    }
  }
}