package Series_RLC_Ringing_Model {
  part def Capacitor {
    attribute capacitance_F : ScalarValues::Real = 1.0;
    attribute capacitor_voltage_V : ScalarValues::Real = 10.0;
    doc /* Canonical entity: capacitor. Reported signal capacitor_voltage_V alias v_C. Initial capacitor voltage = 10 V [current]. */
  }

  part def Resistor {
    attribute resistance_Ohm : ScalarValues::Real = 0.2;
    doc /* Canonical entity: resistor. Resistance R = 0.2 Ohm [current]. */
  }

  part def Inductor {
    attribute inductance_H : ScalarValues::Real = 1.0;
    attribute loop_current_A : ScalarValues::Real = 0.0;
    doc /* Canonical entity: inductor. Inductance L = 1 H [current]. Reported signal loop_current_A is the loop current around the series loop. Initial loop current = 0 A [current]. */
  }

  part def Switch {
    attribute switch_closed : ScalarValues::Integer = 0;
    attribute switch_close_time_s : ScalarValues::Real = 5.0;
    doc /* Canonical entity: switch. Reported signal switch_closed uses 0 for open and 1 for closed. The switch closes once at t = 5 s. */
  }

  part def SimulationControl {
    attribute start_time_s : ScalarValues::Real = 0.0;
    attribute stop_time_s : ScalarValues::Real = 150.0;
    attribute intervals : ScalarValues::Integer = 1000;
    doc /* Required simulation/reporting: simulate for 150 s and report capacitor_voltage_V, loop_current_A, and switch_closed for the whole run. No solver tolerance or sample count requirement is stated; intervals is left at 1000 by modeling choice for output sampling density per merged assumption. */
  }

  part Series_RLC_Ringing {
    part capacitor : Capacitor;
    part resistor : Resistor;
    part inductor : Inductor;
    part switch : Switch;
    part simulation_control : SimulationControl;

    attribute damping_ratio_zeta : ScalarValues::Real = 0.1;
    attribute natural_frequency_omega_n_rad_per_s : ScalarValues::Real = 1.0;

    connect capacitor to switch;
    connect switch to resistor;
    connect resistor to inductor;
    connect inductor to capacitor;

    doc /* Topology: when the switch is open, the capacitor is isolated from the resistor-inductor series loop. The switch closes once at t = 5 s, connecting the capacitor into a loop with the resistor and inductor in series. After closing, the capacitor discharges through the resistor and through the inductor around the loop. */
    doc /* Continuous physical relationship from note [current]: L*C*d^2(v_C)/dt^2 + R*C*d(v_C)/dt + v_C = 0. Derived consistency check: with L = 1 H, C = 1 F, and R = 0.2 Ohm, zeta = (R/2)*sqrt(C/L) = 0.1 and omega_n = 1/sqrt(L*C) = 1 rad/s, matching the stated values. */
    doc /* Required reported variables contract for later stages: capacitor_voltage_V [V] = capacitor voltage; loop_current_A [A] = loop current around the series loop; switch_closed [-] = switch state, with 0 for open and 1 for closed. */
    doc /* Human-confirmed modeling answer: treat switch_close_time_s = 5.0 as the scheduled command time for later execution stages, and document the pre-close and post-close phases in the state machine while leaving exact time-trigger implementation to the execution environment. */
    doc /* Derived: the stated response is underdamped because the provided damping ratio zeta = 0.1 is less than 1, and the brief explicitly states the response shall cross below 0 V and swing negative before settling rather than decay monotonically. */

    state OperatingFlow {
      entry; then Pre_Close_Isolated;

      state Pre_Close_Isolated;
      state Post_Close_Ringing;
      state Complete;

      transition Pre_Close_Isolated_to_Post_Close_Ringing
        first Pre_Close_Isolated
        do action { assign switch.switch_closed := 1; }
        then Post_Close_Ringing;

      transition Post_Close_Ringing_to_Complete
        first Post_Close_Ringing
        then Complete;

      doc /* Pre-close phase: from t = 0 s to t = 5 s while the switch is open, capacitor_voltage_V shall stay exactly 10 V and loop_current_A shall stay exactly 0 A. Scheduled command: at switch_close_time_s = 5.0 s, the switch shall close once. Post-close phase: capacitor_voltage_V shall begin falling from 10 V, discharge through the resistor and inductor around the loop, ring with negative swing, and decay toward 0 V well before the end of the 150 s run. Exact time-trigger implementation is deferred to the execution environment per confirmed answer. */
    }
  }
}
