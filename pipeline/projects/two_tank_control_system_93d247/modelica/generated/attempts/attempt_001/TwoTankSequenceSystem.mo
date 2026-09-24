model TwoTankSequenceSystem
  parameter Modelica.Units.SI.Area A1=1.2;
  parameter Modelica.Units.SI.Area A2=1.4;
  parameter Modelica.Units.SI.Height tankHeight=1.0;
  parameter Modelica.Units.SI.Height initialLevel1=0.05;
  parameter Modelica.Units.SI.Height initialLevel2=0.05;
  parameter Modelica.Units.SI.Height T1_High=0.80;
  parameter Modelica.Units.SI.Height T1_Low=0.05;
  parameter Modelica.Units.SI.Height T2_Low=0.05;
  parameter Modelica.Units.SI.VolumeFlowRate qFill=0.006;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer=0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain=0.0050;
  parameter Modelica.Units.SI.Time scanPeriod=0.1;
  parameter Modelica.Units.SI.Time waitAfterFill=10.0;
  parameter Modelica.Units.SI.Time waitAfterTransfer=12.0;
  parameter Modelica.Units.SI.Time waitAfterDrain=8.0;
  parameter Modelica.Units.SI.Time cmdWidth=2*scanPeriod;

  Modelica.Blocks.Sources.BooleanTable PB_START(table={20,20 + cmdWidth,280,280 + cmdWidth}, startValue=false) annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Sources.BooleanTable PB_STOP(table={220,220 + cmdWidth,650,650 + cmdWidth}, startValue=false) annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Sources.BooleanTable PB_SHUT(table={700,700 + cmdWidth}, startValue=false) annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));

  PLC101 PLC_101(scanPeriod=scanPeriod, T1_High=T1_High, T1_Low=T1_Low, T2_Low=T2_Low, waitAfterFill=waitAfterFill, waitAfterTransfer=waitAfterTransfer, waitAfterDrain=waitAfterDrain) annotation(Placement(transformation(extent={{-10,-20},{30,20}})));
  IdealOnOffValve XV_101(nominalFlow=qFill) annotation(Placement(transformation(extent={{-60,60},{-40,80}})));
  IdealOnOffValve XV_102(nominalFlow=qTransfer) annotation(Placement(transformation(extent={{0,60},{20,80}})));
  IdealOnOffValve XV_103(nominalFlow=qDrain) annotation(Placement(transformation(extent={{60,60},{80,80}})));
  TankInventory TK_101(crossSectionArea=A1, initialLevel=initialLevel1, minLevel=0.0, maxLevel=tankHeight) annotation(Placement(transformation(extent={{-60,-20},{-20,20}})));
  TankInventory TK_102(crossSectionArea=A2, initialLevel=initialLevel2, minLevel=0.0, maxLevel=tankHeight) annotation(Placement(transformation(extent={{40,-20},{80,20}})));
  Modelica.Blocks.Sources.RealExpression zeroFlow(y=0.0) annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));

  Real time_s;
  Real tank1_level_m;
  Real tank2_level_m;
  Boolean valve1_cmd;
  Boolean valve2_cmd;
  Boolean valve3_cmd;
  Integer controller_state_id;
  Real wait_remaining_s;
equation
  time_s = time;
  tank1_level_m = TK_101.level_m;
  tank2_level_m = TK_102.level_m;
  valve1_cmd = PLC_101.valve1_cmd;
  valve2_cmd = PLC_101.valve2_cmd;
  valve3_cmd = PLC_101.valve3_cmd;
  controller_state_id = PLC_101.controller_state_id;
  wait_remaining_s = PLC_101.wait_remaining_s;

  connect(PB_START.y, PLC_101.startButton) annotation(Line(points={{-99,80},{-20,80},{-20,16},{-10,16}}, color={255,0,255}));
  connect(PB_STOP.y, PLC_101.stopButton) annotation(Line(points={{-99,30},{-24,30},{-24,8},{-10,8}}, color={255,0,255}));
  connect(PB_SHUT.y, PLC_101.shutButton) annotation(Line(points={{-99,-20},{-24,-20},{-24,0},{-10,0}}, color={255,0,255}));
  connect(TK_101.level_m, PLC_101.LT101_level_m) annotation(Line(points={{-18,10},{-14,10},{-14,-4},{-10,-4}}, color={0,0,127}));
  connect(TK_102.level_m, PLC_101.LT102_level_m) annotation(Line(points={{82,10},{90,10},{90,-60},{-14,-60},{-14,-12},{-10,-12}}, color={0,0,127}));

  connect(PLC_101.valve1_cmd, XV_101.openCmd) annotation(Line(points={{30,16},{40,16},{40,90},{-80,90},{-80,70},{-60,70}}, color={255,0,255}));
  connect(PLC_101.valve2_cmd, XV_102.openCmd) annotation(Line(points={{30,8},{36,8},{36,86},{-10,86},{-10,70},{0,70}}, color={255,0,255}));
  connect(PLC_101.valve3_cmd, XV_103.openCmd) annotation(Line(points={{30,0},{34,0},{34,84},{50,84},{50,70},{60,70}}, color={255,0,255}));

  connect(XV_101.flow_m3s, TK_101.inflow_m3s) annotation(Line(points={{21,70},{30,70},{30,40},{-90,40},{-90,10},{-60,10}}, color={0,127,255}));
  connect(XV_102.flow_m3s, TK_101.outflowRequest_m3s) annotation(Line(points={{21,70},{28,70},{28,34},{-90,34},{-90,-10},{-60,-10}}, color={0,127,255}));
  connect(TK_101.outflowActual_m3s, TK_102.inflow_m3s) annotation(Line(points={{-20,-10},{20,-10},{20,10},{40,10}}, color={0,127,255}));
  connect(XV_103.flow_m3s, TK_102.outflowRequest_m3s) annotation(Line(points={{81,70},{90,70},{90,-10},{40,-10}}, color={0,127,255}));
  connect(zeroFlow.y, TK_102.inflow_m3s) annotation(Line(points={{-99,-80},{20,-80},{20,10},{40,10}}, color={0,0,127}));

  annotation(
    experiment(StartTime=0, StopTime=900, Tolerance=1e-06, Interval=0.1),
    Diagram(graphics={Text(extent={{-132,96},{-78,102}}, textString="PB-START"),Text(extent={{-132,46},{-78,52}}, textString="PB-STOP"),Text(extent={{-132,-4},{-78,2}}, textString="PB-SHUT"),Text(extent={{-72,84},{-30,90}}, textString="XV-101"),Text(extent={{-6,84},{36,90}}, textString="XV-102"),Text(extent={{54,84},{96,90}}, textString="XV-103"),Text(extent={{-64,24},{-16,30}}, textString="TK-101"),Text(extent={{36,24},{84,30}}, textString="TK-102"),Text(extent={{-8,24},{34,30}}, textString="PLC-101"),Text(extent={{-82,-104},{112,-96}}, textString="Reported variables: time_s, tank1_level_m, tank2_level_m, valve1_cmd, valve2_cmd, valve3_cmd, controller_state_id, wait_remaining_s")})
  );
end TwoTankSequenceSystem;
