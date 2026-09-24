package Single_Tank_Fill_Model {
  part def Supply;

  part def InletValve {
    attribute nominal_inflow_m3_per_s : ScalarValues::Real = 0.01;
    attribute nominal_inflow_L_per_s : ScalarValues::Real = 10.0;
    attribute valve_open_cmd : ScalarValues::Integer = 1;
    doc /* Single inlet valve feeding the Tank. Nominal inflow is 0.01 m^3/s, also stated equivalently as 10 L/s [nominal], from 01_single_tank_fill.txt. valve_open_cmd is the reported variable contract for later stages, with 1 meaning open and 0 meaning closed. */
  }

  part def TankDef {
    attribute cross_sectional_area_m2 : ScalarValues::Real = 0.5;
    attribute height_m : ScalarValues::Real = 1.0;
    attribute initial_level_m : ScalarValues::Real = 0.0;
    attribute tank_level_m : ScalarValues::Real = 0.0;
    attribute fill_target_m : ScalarValues::Real = 0.8;
    doc /* Tank from 01_single_tank_fill.txt. Cross-sectional area 0.5 m^2 [current], height 1.0 m [current], initial level 0 m [current]. Reported variable contract includes tank_level_m [m]. */
  }

  part def SingleTankFillSystemDef {
    part Single_Supply : Supply;
    part Inlet_Valve : InletValve;
    part Tank : TankDef;

    attribute simulation_start_s : ScalarValues::Real = 0.0;
    attribute simulation_stop_s : ScalarValues::Real = 100.0;
    attribute expected_fill_time_s : ScalarValues::Real = 40.0;

    connect Single_Supply to Inlet_Valve;
    connect Inlet_Valve to Tank;

    doc /* Topology from 01_single_tank_fill.txt: the single supply fills through the Inlet valve, and the Inlet valve feeds the Tank. Assumptions already merged: no outlet, leak, evaporation, or other mass loss path is stated and such paths are omitted; stated nominal inflow 0.01 m^3/s is treated as constant while the inlet valve is commanded open; tank cross-sectional area is treated as constant at 0.5 m^2. The note explicitly gives 0.80 m * 0.5 m^2 / 0.01 m^3/s = 40 s <AC-01>. Derived from stated quantities and merged assumptions: filling from 0 m to 0.80 m requires 0.40 m^3, so expected fill time is 40 s. */

    requirement REQ_FUN_001 {
      doc /* <REQ-FUN-001> Starting from empty, the tank fills until its level reaches the 0.80 m fill target, at which point the inlet valve closes and the level stops rising. The valve is open whenever tank level is below the fill target, and closed once the target is reached. Once closed, the valve never reopens during this run. Source: 01_single_tank_fill.txt. */
    }

    state OperatingCycle {
      entry; then Filling;

      state Filling;
      state Filled_Closed;

      transition Filling_to_Filled_Closed
        first Filling
        if Tank.tank_level_m >= Tank.fill_target_m
        do assign Inlet_Valve.valve_open_cmd := 0
        then Filled_Closed;
    }
  }

  part Single_Tank_Fill_System : SingleTankFillSystemDef;
}
