model RM201System
  extends Modelica.Icons.Example;
  parameter Modelica.Units.SI.Volume room_volume_m3 = 100;
  parameter Real C_nominal = 0.001519;
  parameter Real outdoor_co2_mass_fraction_kgkg_param = 0.0004557;
  parameter Real outdoor_co2_ppm_param = 300;
  parameter Real rho_air = 1.2;
  parameter Real co2_gen_per_person = 8.18e-6;
  parameter Real people_source_concentration_kgkg = 100;
  parameter Real kg_s_per_ACH = room_volume_m3*rho_air/3600;

  OccupancySchedule occupancySchedule annotation(Placement(transformation(extent={{-160,20},{-120,60}})));
  CO2RoomController controller annotation(Placement(transformation(extent={{20,20},{80,80}})));
  Modelica.Blocks.Sources.BooleanConstant sensorValid(k=true) annotation(Placement(transformation(extent={{-60,-60},{-40,-40}})));
  Modelica.Blocks.Sources.RealExpression normalizedFeedbackExpr(y=normalized_co2_feedback) annotation(Placement(transformation(extent={{-60,40},{-40,60}})));

  Real room_co2_mass_state(start=outdoor_co2_mass_fraction_kgkg_param*room_volume_m3*rho_air, fixed=true);
  Real time_s;
  Real occupants_person;
  Real outdoor_co2_ppm;
  Real outdoor_co2_mass_fraction_kgkg;
  Real room_co2_mass_fraction_kgkg;
  Real room_co2_ppm;
  Real normalized_co2_feedback;
  Real ach_command_1_per_h;
  Real source_m_flow_command_kg_s;
  Real physical_supply_m_flow_kg_s;
  Real people_source_carrier_m_flow_kg_s;
  Real actual_co2_generation_kg_s;
  Integer controller_mode;
  Boolean sensor_fault_indication;
  parameter Real roomAirMass = room_volume_m3*rho_air;
equation
  der(room_co2_mass_state) = physical_supply_m_flow_kg_s*outdoor_co2_mass_fraction_kgkg + actual_co2_generation_kg_s - physical_supply_m_flow_kg_s*room_co2_mass_fraction_kgkg;
  time_s = time;
  occupants_person = occupancySchedule.occupants_person;
  outdoor_co2_ppm = outdoor_co2_ppm_param;
  outdoor_co2_mass_fraction_kgkg = outdoor_co2_mass_fraction_kgkg_param;
  actual_co2_generation_kg_s = occupants_person*co2_gen_per_person;
  people_source_carrier_m_flow_kg_s = actual_co2_generation_kg_s/people_source_concentration_kgkg;
  room_co2_mass_fraction_kgkg = room_co2_mass_state/roomAirMass;
  normalized_co2_feedback = room_co2_mass_fraction_kgkg/C_nominal;
  room_co2_ppm = room_co2_mass_fraction_kgkg*1e6*28.97/44.01;
  ach_command_1_per_h = controller.ach_command_1_per_h;
  physical_supply_m_flow_kg_s = ach_command_1_per_h*kg_s_per_ACH;
  source_m_flow_command_kg_s = -physical_supply_m_flow_kg_s;
  controller_mode = controller.controller_mode;
  sensor_fault_indication = controller.sensor_fault_indication;

  connect(normalizedFeedbackExpr.y, controller.normalized_co2_feedback) annotation(Line(points={{-39,50},{0,50},{0,60},{20,60}}, color={0,0,127}));
  connect(sensorValid.y, controller.sensor_valid) annotation(Line(points={{-39,-50},{0,-50},{0,32},{20,32}}, color={255,0,255}));

  annotation(experiment(StartTime=0, StopTime=86400, Tolerance=1e-6, Interval=60), Diagram(graphics={Rectangle(extent={{-170,10},{-110,70}}, lineColor={0,0,255}), Text(extent={{-170,74},{-110,86}}, textString="SCH-OCC-201"), Rectangle(extent={{-20,20},{0,80}}, lineColor={0,127,255}), Text(extent={{-34,84},{14,96}}, textString="ZON-201"), Rectangle(extent={{20,20},{80,80}}, lineColor={255,127,0}), Text(extent={{20,84},{80,96}}, textString="CTL-CO2-201"), Text(extent={{-92,-6},{10,8}}, textString="Well-mixed CO2 balance") }));
end RM201System;
