model Two_Tank_Sequence_Controller_System
  TwoTankPlant plant annotation(Placement(transformation(extent={{-10,-20},{70,40}})));
  PLC101 PLC_101 annotation(Placement(transformation(extent={{-10,70},{70,150}})));
  Modelica.Blocks.Sources.BooleanTable PB_START(table={20.0,20.05,280.0,280.05}, startValue=false) annotation(Placement(transformation(extent={{-120,130},{-100,150}})));
  Modelica.Blocks.Sources.BooleanTable PB_STOP(table={220.0,220.05,650.0,650.05}, startValue=false) annotation(Placement(transformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Sources.BooleanTable PB_SHUT(table={700.0,700.05}, startValue=false) annotation(Placement(transformation(extent={{-120,50},{-100,70}})));

  Real time_s;
  Real tank1_level_m;
  Real tank2_level_m;
  Real valve1_cmd;
  Real valve2_cmd;
  Real valve3_cmd;
  Integer controller_state_id;
  Real wait_remaining_s;

equation 
  connect(PB_START.y, PLC_101.startButton) annotation(Line(points={{-99,140},{-60,140},{-60,136},{-10,136}}, color={255,0,255}));
  connect(PB_STOP.y, PLC_101.stopButton) annotation(Line(points={{-99,100},{-50,100},{-50,116},{-10,116}}, color={255,0,255}));
  connect(PB_SHUT.y, PLC_101.shutButton) annotation(Line(points={{-99,60},{-40,60},{-40,96},{-10,96}}, color={255,0,255}));
  connect(plant.tank1_level_m, PLC_101.LT101_level_m) annotation(Line(points={{71,20},{90,20},{90,34},{-30,34},{-30,86},{-10,86}}, color={0,0,127}));
  connect(plant.tank2_level_m, PLC_101.LT102_level_m) annotation(Line(points={{71,-20},{96,-20},{96,10},{-36,10},{-36,76},{-10,76}}, color={0,0,127}));
  connect(PLC_101.valve1_cmd, plant.valve1_cmd) annotation(Line(points={{71,130},{80,130},{80,54},{-20,54},{-20,30},{-10,30}}, color={255,0,255}));
  connect(PLC_101.valve2_cmd, plant.valve2_cmd) annotation(Line(points={{71,90},{84,90},{84,10},{-20,10},{-20,0},{-10,0}}, color={255,0,255}));
  connect(PLC_101.valve3_cmd, plant.valve3_cmd) annotation(Line(points={{71,40},{88,40},{88,-34},{-20,-34},{-20,-30},{-10,-30}}, color={255,0,255}));

  time_s = time;
  tank1_level_m = plant.tank1_level_m;
  tank2_level_m = plant.tank2_level_m;
  valve1_cmd = if PLC_101.valve1_cmd then 1 else 0;
  valve2_cmd = if PLC_101.valve2_cmd then 1 else 0;
  valve3_cmd = if PLC_101.valve3_cmd then 1 else 0;
  controller_state_id = PLC_101.controller_state_id;
  wait_remaining_s = PLC_101.wait_remaining_s;

  annotation(
    experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1),
    Diagram(graphics={
      Text(extent={{-140,166},{-74,154}}, textString="Commands"),
      Text(extent={{-2,162},{66,150}}, textString="PLC-101"),
      Text(extent={{4,54},{58,42}}, textString="Plant")
    }));
end Two_Tank_Sequence_Controller_System;
