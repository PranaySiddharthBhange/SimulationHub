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
  IdealOnOffValve XV_101(nominalFlow=qFill) annotation(Placement(transformation(extent={{-80,40},{-60,60}})));
  Tank1Inventory TK_101(crossSectionArea=A1, initialLevel=initialLevel1, minLevel=0.0, maxLevel=tankHeight) annotation(Placement(transformation(extent={{-30,30},{10,70}})));
  IdealOnOffValve XV_102(nominalFlow=qTransfer) annotation(Placement(transformation(extent={{30,40},{50,60}})));
  Tank2Inventory TK_102(crossSectionArea=A2, initialLevel=initialLevel2, minLevel=0.0, maxLevel=tankHeight) annotation(Placement(transformation(extent={{70,30},{110,70}})));
  IdealOnOffValve XV_103(nominalFlow=qDrain) annotation(Placement(transformation(extent={{130,40},{150,60}})));

  Real time_s;
  Real tank1_level_m;
  Real tank2_level_m;
  Boolean valve1_cmd;
  Boolean valve2_cmd;
  Boolean valve3_cmd;
  Integer controller_state_id;
  Real wait_remaining_s;
  Modelica.Units.SI.VolumeFlowRate transferRequest_m3s;
  Modelica.Units.SI.VolumeFlowRate drainRequest_m3s;
equation
  time_s = time;
  tank1_level_m = TK_101.level_m;
  tank2_level_m = TK_102.level_m;
  valve1_cmd = PLC_101.valve1_cmd;
  valve2_cmd = PLC_101.valve2_cmd;
  valve3_cmd = PLC_101.valve3_cmd;
  controller_state_id = PLC_101.controller_state_id;
  wait_remaining_s = PLC_101.wait_remaining_s;
  transferRequest_m3s = XV_102.flow_m3s;
  drainRequest_m3s = XV_103.flow_m3s;

  connect(PB_START.y, PLC_101.startButton) annotation(Line(points={{-99,80},{-20,80},{-20,16},{-10,16}}, color={255,0,255}));
  connect(PB_STOP.y, PLC_101.stopButton) annotation(Line(points={{-99,30},{-24,30},{-24,8},{-10,8}}, color={255,0,255}));
  connect(PB_SHUT.y, PLC_101.shutButton) annotation(Line(points={{-99,-20},{-24,-20},{-24,0},{-10,0}}, color={255,0,255}));
  connect(TK_101.level_m, PLC_101.LT101_level_m) annotation(Line(points={{12,60},{18,60},{18,-4},{-10,-4}}, color={0,0,127}));
  connect(TK_102.level_m, PLC_101.LT102_level_m) annotation(Line(points={{112,60},{118,60},{118,-60},{-14,-60},{-14,-12},{-10,-12}}, color={0,0,127}));

  connect(PLC_101.valve1_cmd, XV_101.openCmd) annotation(Line(points={{30,16},{38,16},{38,70},{-100,70},{-100,50},{-80,50}}, color={255,0,255}));
  connect(PLC_101.valve2_cmd, XV_102.openCmd) annotation(Line(points={{30,8},{36,8},{36,68},{20,68},{20,50},{30,50}}, color={255,0,255}));
  connect(PLC_101.valve3_cmd, XV_103.openCmd) annotation(Line(points={{30,0},{36,0},{36,76},{120,76},{120,50},{130,50}}, color={255,0,255}));

  connect(XV_101.flow_m3s, TK_101.inflow_m3s) annotation(Line(points={{-59,50},{-40,50},{-40,60},{-30,60}}, color={0,127,255}));
  connect(XV_102.flow_m3s, TK_101.outflowRequest_m3s) annotation(Line(points={{51,50},{58,50},{58,20},{-40,20},{-40,40},{-30,40}}, color={0,127,255}));
  connect(TK_101.level_m, TK_102.inflow_m3s) annotation(Line(points={{12,60},{40,60},{40,60},{70,60}}, color={0,127,255}));
  connect(XV_103.flow_m3s, TK_102.outflowRequest_m3s) annotation(Line(points={{151,50},{158,50},{158,20},{60,20},{60,40},{70,40}}, color={0,127,255}));

  annotation(
    experiment(StartTime=0, StopTime=900, Tolerance=1e-06, Interval=0.1)
  );
end TwoTankSequenceSystem;
