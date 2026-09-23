package single_tank_transfer_sequence {
  part def Operator {
    attribute START_command : ScalarValues::Boolean;
    attribute STOP_command : ScalarValues::Boolean;
    attribute SHUT_command : ScalarValues::Boolean;
  }

  part def Controller {
    attribute inlet_inhibited : ScalarValues::Boolean;
    attribute experiment_duration_s : ScalarValues::Real = 900.0;
    attribute report_tank_levels : ScalarValues::Boolean = true;
    attribute report_valve_commands : ScalarValues::Boolean = true;
  }

  part def Tank {
    attribute level : ScalarValues::Real;
  }

  part def Valve {
    attribute commanded_open : ScalarValues::Boolean;
  }

  part def LevelSwitch {
    attribute reached : ScalarValues::Boolean;
  }

  state def Sequence_state {
    doc /* Ordered controller states evidenced by 01_single_tank_transfer_description.txt and confirmed shutdown answer: Idle; Fill_Tank_1; Wait_after_fill; Transfer_to_Tank_2; Wait_after_transfer; Drain_Tank_2; Paused; Shutdown_emptying; Shutdown_complete. Initial condition and command event schedule within the 900-second experiment are not provided. */
  }

  requirement def req_900s_experiment {
    doc /* 01_single_tank_transfer_description.txt: the model shall report tank levels and valve commands for a 900-second experiment. */
  }

  requirement def req_stop_pause_resume {
    doc /* 01_single_tank_transfer_description.txt: when STOP is given, every valve closes and the sequence pauses. If START is later given after STOP, the Controller resumes the interrupted state rather than restarting from the beginning. */
  }

  requirement def req_shutdown_override {
    doc /* 01_single_tank_transfer_description.txt + human-confirmed answer: when SHUT is given, the inlet is inhibited and the transfer and drain paths are opened until both tanks are empty. SHUT has priority over STOP while shutdown emptying is active. After both tanks are empty the system remains in Shutdown_complete with inlet inhibited and no automatic return to Idle until a separate reset is defined. */
  }

  action def start_fill {
    doc /* Idle -> Fill_Tank_1; guard: Operator START_command given and shutdown not active; command: open inlet_valve, close transfer_valve, close drain_valve, Controller inlet_inhibited=false; priority: normal sequence start. */
  }

  action def complete_fill_wait {
    doc /* Fill_Tank_1 -> Wait_after_fill; guard: High_level_switch reached while sensing Tank_1 level; command: close inlet_valve; wait/duration: then wait 10 s before next state. */
  }

  action def begin_transfer {
    doc /* Wait_after_fill -> Transfer_to_Tank_2; guard: 10 s wait complete; command: close inlet_valve, open transfer_valve, close drain_valve. */
  }

  action def complete_transfer_wait {
    doc /* Transfer_to_Tank_2 -> Wait_after_transfer; guard: Low_level_switch reached while sensing Tank_1 level; command: close transfer_valve; wait/duration: then wait 10 s before next state. */
  }

  action def begin_drain {
    doc /* Wait_after_transfer -> Drain_Tank_2; guard: 10 s wait complete; command: close inlet_valve, close transfer_valve, open drain_valve. */
  }

  action def complete_drain {
    doc /* Drain_Tank_2 -> Idle; guard: Low_level_switch reached while sensing Tank_2 level; command: close drain_valve; result: normal sequence completion. */
  }

  action def stop_pause {
    doc /* Fill_Tank_1 or Wait_after_fill or Transfer_to_Tank_2 or Wait_after_transfer or Drain_Tank_2 -> Paused; guard: Operator STOP_command given and shutdown emptying not active; command: close inlet_valve, close transfer_valve, close drain_valve; result: pause interrupted state. */
  }

  action def resume_after_stop {
    doc /* Paused -> previously interrupted state; guard: Operator START_command given after STOP and shutdown not active; command: resume interrupted state rather than restart from beginning; valve commands on resume follow the interrupted state. */
  }

  action def enter_shutdown {
    doc /* Any state including Paused -> Shutdown_emptying; guard: Operator SHUT_command given; command: Controller inlet_inhibited=true, close inlet_valve, open transfer_valve, open drain_valve; priority: SHUT overrides normal sequencing and has priority over STOP while shutdown emptying is active. */
  }

  action def complete_shutdown_emptying {
    doc /* Shutdown_emptying -> Shutdown_complete; guard: both tanks empty; command: keep Controller inlet_inhibited=true, close inlet_valve; after both tanks are empty no automatic return to Idle until a separate reset is defined. Transfer and drain valve final commands in Shutdown_complete are not explicitly stated by source. */
  }

  part def Single_tank_transfer_system_def {
    part Operator_unit : Operator;
    part Controller_unit : Controller;
    part Tank_1 : Tank;
    part Tank_2 : Tank;
    part inlet_valve : Valve;
    part transfer_valve : Valve;
    part drain_valve : Valve;
    part High_level_switch : LevelSwitch;
    part Low_level_switch : LevelSwitch;

    connect Operator_unit to Controller_unit;
    connect Controller_unit to inlet_valve;
    connect Controller_unit to transfer_valve;
    connect Controller_unit to drain_valve;
    connect Tank_1 to High_level_switch;
    connect Tank_1 to Low_level_switch;
    connect Tank_2 to Low_level_switch;

    doc /* 01_single_tank_transfer_description.txt: Tank 1 and Tank 2 are stated to be connected by the inlet valve, transfer valve, and drain valve; the source does not specify the physical routing of each valve beyond that statement. Human-confirmed answer clar_002_valve_routing: define explicit physical endpoints for each named valve only after clarification from source material. */
    doc /* clar_001_low_level_switch_identity: one shared Low_level_switch entity senses Tank_1 during transfer completion and Tank_2 during draining completion. */
  }

  part Single_tank_transfer_system : Single_tank_transfer_system_def {
    state sequence_state : Sequence_state;
    requirement experiment_requirement : req_900s_experiment;
    requirement stop_pause_resume_requirement : req_stop_pause_resume;
    requirement shutdown_override_requirement : req_shutdown_override;
    action start_fill_action : start_fill;
    action complete_fill_wait_action : complete_fill_wait;
    action begin_transfer_action : begin_transfer;
    action complete_transfer_wait_action : complete_transfer_wait;
    action begin_drain_action : begin_drain;
    action complete_drain_action : complete_drain;
    action stop_pause_action : stop_pause;
    action resume_after_stop_action : resume_after_stop;
    action enter_shutdown_action : enter_shutdown;
    action complete_shutdown_emptying_action : complete_shutdown_emptying;
  }
}
