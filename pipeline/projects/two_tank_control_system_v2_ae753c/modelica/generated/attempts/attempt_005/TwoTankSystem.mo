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
  parameter Modelica.Units.SI.Time cmdWidth = 2*scanPeriod;
  parameter Real levelFloor_m = 1e-6;

  Modelica.Units.SI.Height tank1_level_m(start=tank1_level_start, fixed=true);
  Modelica.Units.SI.Height tank2_level_m(start=tank2_level_start, fixed=true);
  Modelica.Units.SI.Time time_s;
  Real valve1_open_cmd;
  Real valve2_open_cmd;
  Real valve3_open_cmd;
  Integer controller_state_code;
  Modelica.Units.SI.Time wait_remaining_s;
  Real cmd_start;
  Real cmd_stop;
  Real cmd_shut;

  Modelica.Blocks.Sources.BooleanTable startSchedule(table={20,20 + cmdWidth,280,280 + cmdWidth}, startValue=false)
    annotation(Placement(transformation(extent={{-180,120},{-160,140}})));
  Modelica.Blocks.Sources.BooleanTable stopSchedule(table={220,220 + cmdWidth,650,650 + cmdWidth}, startValue=false)
    annotation(Placement(transformation(extent={{-180,80},{-160,100}})));
  Modelica.Blocks.Sources.BooleanTable shutSchedule(table={700,700 + cmdWidth}, startValue=false)
    annotation(Placement(transformation(extent={{-180,40},{-160,60}})));

  TankController PLC_101(scanPeriod=scanPeriod, waitAfterFill_s=10, waitAfterTransfer_s=12, waitAfterDrain_s=8, t1Low_m=T1_low, t2Low_m=T2_low, t1High_m=T1_high)
    annotation(Placement(transformation(extent={{-20,40},{40,120}})));

  Modelica.Blocks.Sources.RealExpression level1Signal(y=tank1_level_m)
    annotation(Placement(transformation(extent={{-100,-20},{-80,0}})));
  Modelica.Blocks.Sources.RealExpression level2Signal(y=tank2_level_m)
    annotation(Placement(transformation(extent={{-100,-60},{-80,-40}})));
  Modelica.Blocks.Math.BooleanToReal v1Report(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{80,90},{100,110}})));
  Modelica.Blocks.Math.BooleanToReal v2Report(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{80,60},{100,80}})));
  Modelica.Blocks.Math.BooleanToReal v3Report(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{80,30},{100,50}})));
  Modelica.Blocks.Math.BooleanToReal startReport(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{-120,120},{-100,140}})));
  Modelica.Blocks.Math.BooleanToReal stopReport(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{-120,80},{-100,100}})));
  Modelica.Blocks.Math.BooleanToReal shutReport(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{-120,40},{-100,60}})));

equation
  time_s = time;

  der(tank1_level_m) = (if PLC_101.valve1Cmd and tank1_level_m < tankHeight then qFill else 0)/A1 - (if PLC_101.valve2Cmd and tank1_level_m > levelFloor_m then qTransfer else 0)/A1;
  der(tank2_level_m) = (if PLC_101.valve2Cmd and tank2_level_m < tankHeight then qTransfer else 0)/A2 - (if PLC_101.valve3Cmd and tank2_level_m > levelFloor_m then qDrain else 0)/A2;

  assert(tank1_level_m >= 0 and tank1_level_m <= tankHeight, "tank1_level_m out of range");
  assert(tank2_level_m >= 0 and tank2_level_m <= tankHeight, "tank2_level_m out of range");

  connect(startSchedule.y, startReport.u) annotation(Line(points={{-159,130},{-140,130},{-140,130},{-121,130}}, color={255,0,255}));
  connect(stopSchedule.y, stopReport.u) annotation(Line(points={{-159,90},{-140,90},{-140,90},{-121,90}}, color={255,0,255}));
  connect(shutSchedule.y, shutReport.u) annotation(Line(points={{-159,50},{-140,50},{-140,50},{-121,50}}, color={255,0,255}));
  connect(startSchedule.y, PLC_101.startButton) annotation(Line(points={{-159,130},{-60,130},{-60,86},{-20,86}}, color={255,0,255}));
  connect(stopSchedule.y, PLC_101.stopButton) annotation(Line(points={{-159,90},{-60,90},{-60,70},{-20,70}}, color={255,0,255}));
  connect(shutSchedule.y, PLC_101.shutButton) annotation(Line(points={{-159,50},{-60,50},{-60,54},{-20,54}}, color={255,0,255}));
  connect(level1Signal.y, PLC_101.level1_m) annotation(Line(points={{-79,-10},{-50,-10},{-50,38},{-10,38},{-10,46},{-20,46}}, color={0,0,127}));
  connect(level2Signal.y, PLC_101.level2_m) annotation(Line(points={{-79,-50},{-40,-50},{-40,42},{-20,42}}, color={0,0,127}));
  connect(PLC_101.valve1Cmd, v1Report.u) annotation(Line(points={{40,98},{60,98},{60,100},{79,100}}, color={255,0,255}));
  connect(PLC_101.valve2Cmd, v2Report.u) annotation(Line(points={{40,82},{60,82},{60,70},{79,70}}, color={255,0,255}));
  connect(PLC_101.valve3Cmd, v3Report.u) annotation(Line(points={{40,66},{60,66},{60,40},{79,40}}, color={255,0,255}));

  valve1_open_cmd = v1Report.y;
  valve2_open_cmd = v2Report.y;
  valve3_open_cmd = v3Report.y;
  controller_state_code = PLC_101.stateCode;
  wait_remaining_s = PLC_101.waitRemaining_s;
  cmd_start = startReport.y;
  cmd_stop = stopReport.y;
  cmd_shut = shutReport.y;

  annotation(
    Diagram(graphics={Rectangle(extent={{-200,-120},{200,160}}, lineColor={0,0,0}),Ellipse(extent={{-170,-10},{-130,30}}, lineColor={0,127,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),Text(extent={{-180,30},{-120,45}}, textString="SRC-101"),Rectangle(extent={{-110,-10},{-90,10}}, lineColor={0,127,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Text(extent={{-120,15},{-80,30}}, textString="XV-101"),Rectangle(extent={{-50,-40},{-10,40}}, lineColor={0,127,255}),Rectangle(extent={{-48,-40},{-12,-20}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),Text(extent={{-65,45},{5,60}}, textString="TK-101"),Rectangle(extent={{10,-10},{30,10}}, lineColor={0,127,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Text(extent={{0,15},{40,30}}, textString="XV-102"),Rectangle(extent={{70,-40},{110,40}}, lineColor={0,127,255}),Rectangle(extent={{72,-40},{108,-20}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),Text(extent={{55,45},{125,60}}, textString="TK-102"),Rectangle(extent={{130,-10},{150,10}}, lineColor={0,127,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Text(extent={{120,15},{160,30}}, textString="XV-103"),Ellipse(extent={{170,-10},{210,30}}, lineColor={0,127,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),Text(extent={{165,30},{215,45}}, textString="DRN-101"),Text(extent={{-100,150},{100,170}}, textString="%name")}),
    experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1));
end TwoTankSystem;
