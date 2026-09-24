model TwoTankSystem
  extends Modelica.Icons.Example;
  parameter Modelica.Units.SI.Area A1 = 1.2;
  parameter Modelica.Units.SI.Area A2 = 1.4;
  parameter Modelica.Units.SI.Height tankHeight = 1.0;
  parameter Modelica.Units.SI.Height tank1_level_start = 0.05;
  parameter Modelica.Units.SI.Height tank2_level_start = 0.05;
  parameter Modelica.Units.SI.Height T1_low = 0.05;
  parameter Modelica.Units.SI.Height T2_low = 0.05;
  parameter Modelica.Units.SI.Height T1_high = 0.80;
  parameter Modelica.Units.SI.VolumeFlowRate qFill = 0.0060;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer = 0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain = 0.0050;
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Real cmdWidth = 0.2;

  Modelica.Blocks.Sources.BooleanTable startSchedule(table={20,20.2,280,280.2}, startValue=false) annotation(Placement(transformation(extent={{-180,100},{-160,120}})));
  Modelica.Blocks.Sources.BooleanTable stopSchedule(table={220,220.2,650,650.2}, startValue=false) annotation(Placement(transformation(extent={{-180,60},{-160,80}})));
  Modelica.Blocks.Sources.BooleanTable shutSchedule(table={700,700.2}, startValue=false) annotation(Placement(transformation(extent={{-180,20},{-160,40}})));
  TwoTankController PLC_101(scanPeriod=scanPeriod, t1High=T1_high, t1Low=T1_low, t2Low=T2_low, waitAfterFill=10, waitAfterTransfer=12, waitAfterDrain=8) annotation(Placement(transformation(origin = {4, 26}, extent = {{-40, 10}, {20, 90}})));

  Real tank1_level_m(start=tank1_level_start, fixed=true, nominal=0.5);
  Real tank2_level_m(start=tank2_level_start, fixed=true, nominal=0.5);
  Boolean valve1_open_cmd;
  Boolean valve2_open_cmd;
  Boolean valve3_open_cmd;
  Integer controller_state_code;
  Real wait_remaining_s;
  Boolean cmd_start;
  Boolean cmd_stop;
  Boolean cmd_shut;
  Real time_s;
equation
  cmd_start = startSchedule.y;
  cmd_stop = stopSchedule.y;
  cmd_shut = shutSchedule.y;

  connect(startSchedule.y, PLC_101.startButton) annotation(Line(points={{-159,110},{-100,110},{-100,104},{-39,104}}, color={255,0,255}));
  connect(stopSchedule.y, PLC_101.stopButton) annotation(Line(points={{-159,70},{-97,70},{-97,88},{-39,88}}, color={255,0,255}));
  connect(shutSchedule.y, PLC_101.shutButton) annotation(Line(points={{-159,30},{-80,30},{-80,72},{-39,72}}, color={255,0,255}));

  PLC_101.level1 = tank1_level_m;
  PLC_101.level2 = tank2_level_m;

  valve1_open_cmd = PLC_101.valve1;
  valve2_open_cmd = PLC_101.valve2;
  valve3_open_cmd = PLC_101.valve3;
  controller_state_code = PLC_101.stateCode;
  wait_remaining_s = PLC_101.waitRemaining;
  time_s = time;

  der(tank1_level_m) = ((if valve1_open_cmd then qFill else 0) - (if valve2_open_cmd and tank1_level_m > 0 then qTransfer else 0))/A1;
  der(tank2_level_m) = ((if valve2_open_cmd and tank1_level_m > 0 then qTransfer else 0) - (if valve3_open_cmd and tank2_level_m > 1e-6 then qDrain else 0))/A2;

  assert(tank1_level_m >= -1e-6 and tank1_level_m <= tankHeight + 1e-6, "tank1_level_m out of range");
  assert(tank2_level_m >= -1e-6 and tank2_level_m <= tankHeight + 1e-6, "tank2_level_m out of range");
  assert(not (valve1_open_cmd and valve2_open_cmd), "V1 and V2 commanded open simultaneously");
  assert(not (controller_state_code <> 8 and valve2_open_cmd and valve3_open_cmd), "V2 and V3 commanded open simultaneously outside SHUTDOWN");
annotation(
  experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1),
  Diagram(graphics={Rectangle(extent={{-130,20},{-90,-20}}, lineColor={0,0,255}),Text(extent={{-130,28},{-90,20}}, textString="SRC-101"),Polygon(points={{-85,0},{-75,10},{-75,-10},{-85,0}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),Text(extent={{-90,-22},{-60,-32}}, textString="XV-101"),Rectangle(extent={{-50,20},{-10,-40}}, lineColor={0,0,255}),Rectangle(extent={{-50,-40},{-10,-10}}, lineColor={0,128,255}, fillColor={0,128,255}, fillPattern=FillPattern.Solid),Text(extent={{-52,28},{-8,20}}, textString="TK-101"),Polygon(points={{5,0},{15,10},{15,-10},{5,0}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),Text(extent={{0,-22},{30,-32}}, textString="XV-102"),Rectangle(extent={{40,20},{80,-40}}, lineColor={0,0,255}),Rectangle(extent={{40,-40},{80,-10}}, lineColor={0,128,255}, fillColor={0,128,255}, fillPattern=FillPattern.Solid),Text(extent={{38,28},{82,20}}, textString="TK-102"),Polygon(points={{95,0},{105,10},{105,-10},{95,0}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),Text(extent={{90,-22},{120,-32}}, textString="XV-103"),Ellipse(extent={{125,15},{155,-15}}, lineColor={0,0,255}),Text(extent={{120,28},{160,20}}, textString="DRN-101"),Line(points={{-90,0},{-85,0}}, color={0,127,255}),Line(points={{-75,0},{-50,0}}, color={0,127,255}),Line(points={{-10,0},{5,0}}, color={0,127,255}),Line(points={{15,0},{40,0}}, color={0,127,255}),Line(points={{80,0},{95,0}}, color={0,127,255}),Line(points={{105,0},{125,0}}, color={0,127,255}),Text(extent={{-100,-70},{100,-90}}, textString="PLC-101 commands levels and valves")}),
  Icon(graphics={Text(extent={{-100,100},{100,140}}, textString="%name")}));
end TwoTankSystem;
