model RM201System
  parameter Real room_volume_m3 = 100.0;
  parameter Real air_density_kg_m3 = 1.2;
  parameter Real C_nominal_kgkg = 0.001519;
  parameter Real outdoor_co2_mass_fraction_kgkg_param = 0.0004557;
  parameter Real outdoor_co2_ppm_param = 300.0;
  parameter Real co2_generation_per_person_kg_s = 8.18e-6;
  parameter Real C_source_kgkg = 100.0;

  OccupancySchedule occupancySchedule;
  CO2Controller controller;

  Real room_co2_mass_fraction_kgkg(start=outdoor_co2_mass_fraction_kgkg_param, fixed=true);
  Real room_co2_ppm;
  Real normalized_co2_feedback;
  Real ach_command_1_per_h;
  Real source_m_flow_command_kg_s;
  Real physical_supply_m_flow_kg_s;
  Real people_source_carrier_m_flow_kg_s;
  Real actual_co2_generation_kg_s;
  Integer occupants_person;
  Integer controller_mode;
  Boolean sensor_fault_indication;
  Real outdoor_co2_ppm;
  Real outdoor_co2_mass_fraction_kgkg;
  Real time_s;
equation
  occupants_person = occupancySchedule.occupants_person;
  outdoor_co2_ppm = outdoor_co2_ppm_param;
  outdoor_co2_mass_fraction_kgkg = outdoor_co2_mass_fraction_kgkg_param;
  actual_co2_generation_kg_s = occupants_person * co2_generation_per_person_kg_s;
  people_source_carrier_m_flow_kg_s = actual_co2_generation_kg_s / C_source_kgkg;
  controller.room_co2_mass_fraction_kgkg = room_co2_mass_fraction_kgkg;
  controller.signal_valid = true;
  normalized_co2_feedback = controller.normalized_co2_feedback;
  ach_command_1_per_h = controller.ach_command_1_per_h;
  controller_mode = controller.controller_mode;
  sensor_fault_indication = controller.sensor_fault_indication;
  physical_supply_m_flow_kg_s = ach_command_1_per_h * room_volume_m3 * air_density_kg_m3 / 3600.0;
  source_m_flow_command_kg_s = -physical_supply_m_flow_kg_s;
  der(room_co2_mass_fraction_kgkg) = (physical_supply_m_flow_kg_s/(air_density_kg_m3*room_volume_m3))*(outdoor_co2_mass_fraction_kgkg - room_co2_mass_fraction_kgkg) + actual_co2_generation_kg_s/(air_density_kg_m3*room_volume_m3);
  room_co2_ppm = room_co2_mass_fraction_kgkg / C_nominal_kgkg * 1000.0;
  time_s = time;
annotation(experiment(StartTime=0, StopTime=86400, Tolerance=1e-6, Interval=60));
end RM201System;
