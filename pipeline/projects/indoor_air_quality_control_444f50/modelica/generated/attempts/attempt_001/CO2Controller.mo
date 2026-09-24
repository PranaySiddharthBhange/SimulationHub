model CO2Controller
  parameter Real C_nominal_kgkg = 0.001519;
  parameter Real Kp_ACH_per_normalized_error = 6.0;
  parameter Real output_bias_ACH = 3.5;
  parameter Real lower_limit_ACH = 0.2;
  parameter Real upper_limit_ACH = 6.0;
  parameter Real sensor_fault_output_ACH = 4.0;
  input Real room_co2_mass_fraction_kgkg;
  input Boolean signal_valid;
  output Real normalized_co2_feedback;
  output Real ach_command_1_per_h;
  output Integer controller_mode;
  output Boolean sensor_fault_indication;
protected 
  Real requested_ach_1_per_h;
algorithm 
  normalized_co2_feedback := room_co2_mass_fraction_kgkg / C_nominal_kgkg;
  requested_ach_1_per_h := output_bias_ACH + Kp_ACH_per_normalized_error*(normalized_co2_feedback - 1.0);
  if not signal_valid then
    ach_command_1_per_h := sensor_fault_output_ACH;
    controller_mode := 3;
    sensor_fault_indication := true;
  elseif requested_ach_1_per_h <= lower_limit_ACH then
    ach_command_1_per_h := lower_limit_ACH;
    controller_mode := 0;
    sensor_fault_indication := false;
  elseif requested_ach_1_per_h >= upper_limit_ACH then
    ach_command_1_per_h := upper_limit_ACH;
    controller_mode := 2;
    sensor_fault_indication := false;
  else
    ach_command_1_per_h := requested_ach_1_per_h;
    controller_mode := 1;
    sensor_fault_indication := false;
  end if;
end CO2Controller;
