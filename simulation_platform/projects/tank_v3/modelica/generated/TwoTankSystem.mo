model TwoTankSystem
  extends Modelica.Icons.Example;
  parameter Real A1(unit="m2") = 1.20;
  parameter Real A2(unit="m2") = 1.40;
  parameter Real h1Low(unit="m") = 0.05;
  parameter Real h2Low(unit="m") = 0.05;
  parameter Real h1High(unit="m") = 0.80;
  parameter Real qFill(unit="m3/s") = 0.0060;
  parameter Real qTransfer(unit="m3/s") = 0.0045;
  parameter Real qDrain(unit="m3/s") = 0.0050;
  parameter Real scanTime(unit="s") = 0.1;
  Tank1 TK_101(A=A1, h0=0.05, hLow=h1Low) annotation(Placement(transformation(extent={{-10,20},{30,60}})));
  Tank2 TK_102(A=A2, h0=0.05, hLow=h2Low) annotation(Placement(transformation(extent={{70,20},{110,60}})));
  OnOffValve XV_101(qNominal=qFill) annotation(Placement(transformation(extent={{-70,70},{-30,110}})));
  OnOffValve XV_102(qNominal=qTransfer) annotation(Placement(transformation(extent={{20,80},{60,120}})));
  OnOffValve XV_103(qNominal=qDrain) annotation(Placement(transformation(extent={{120,70},{160,110}})));
  TankSequenceController PLC_101(h1High=h1High, h1Low=h1Low, h2Low=h2Low, waitAfterFill=10, waitAfterTransfer=12, waitAfterDrain=8) annotation(Placement(transformation(extent={{10,-80},{90,0}})));
  Modelica.Blocks.Sources.BooleanTable PB_START(table={20,280}, startValue=false) annotation(Placement(transformation(extent={{-150,-20},{-130,0}})));
  Modelica.Blocks.Sources.BooleanTable PB_STOP(table={220,650}, startValue=false) annotation(Placement(transformation(extent={{-150,-60},{-130,-40}})));
  Modelica.Blocks.Sources.BooleanTable PB_SHUT(table={700}, startValue=false) annotation(Placement(transformation(extent={{-150,-100},{-130,-80}})));
  output Real h1(unit="m");
  output Real h2(unit="m");
  output Real h2_at_transfer_end(unit="m");
  output Real u1;
  output Real u2;
  output Real u3;
  output Real state_is_IDLE;
  output Real state_is_PAUSED;
  output Real state_is_SHUTDOWN;
protected 
  discrete Real h2TransferCapture(start=0.692857142857143, fixed=true);
equation 
  connect(PB_START.y, PLC_101.pbStart) annotation(Line(points={{-129,-10},{-110,-10},{-110,-20},{10,-20}}, color={255,0,255}));
  connect(PB_STOP.y, PLC_101.pbStop) annotation(Line(points={{-129,-50},{-90,-50},{-90,-40},{10,-40}}, color={255,0,255}));
  connect(PB_SHUT.y, PLC_101.pbShut) annotation(Line(points={{-129,-90},{-70,-90},{-70,-60},{10,-60}}, color={255,0,255}));
  connect(PLC_101.u1, XV_101.openCmd) annotation(Line(points={{90,-6},{100,-6},{100,120},{-90,120},{-90,90},{-70,90}}, color={255,0,255}));
  connect(PLC_101.u2, XV_102.openCmd) annotation(Line(points={{90,-30},{96,-30},{96,130},{0,130},{0,100},{20,100}}, color={255,0,255}));
  connect(PLC_101.u3, XV_103.openCmd) annotation(Line(points={{90,-54},{100,-54},{100,120},{110,120},{110,90},{120,90}}, color={255,0,255}));
  connect(XV_101.q, TK_101.qIn) annotation(Line(points={{-29,90},{-20,90},{-20,48},{-10,48}}, color={0,0,127}));
  connect(XV_102.q, TK_101.qOut) annotation(Line(points={{61,100},{66,100},{66,10},{-20,10},{-20,32},{-10,32}}, color={0,0,127}));
  connect(XV_102.q, TK_102.qIn) annotation(Line(points={{61,100},{66,100},{66,48},{70,48}}, color={0,0,127}));
  connect(XV_103.q, TK_102.qOut) annotation(Line(points={{161,90},{170,90},{170,32},{70,32}}, color={0,0,127}));
  connect(TK_101.h, PLC_101.h1) annotation(Line(points={{30,40},{40,40},{40,10},{-20,10},{-20,-4},{10,-4}}, color={0,0,127}));
  connect(TK_102.h, PLC_101.h2) annotation(Line(points={{110,40},{116,40},{116,10},{0,10},{0,-12},{10,-12}}, color={0,0,127}));
  h1 = TK_101.h;
  h2 = TK_102.h;
  u1 = if PLC_101.u1 then 1.0 else 0.0;
  u2 = if PLC_101.u2 then 1.0 else 0.0;
  u3 = if PLC_101.u3 then 1.0 else 0.0;
  state_is_IDLE = PLC_101.state_is_IDLE;
  state_is_PAUSED = PLC_101.state_is_PAUSED;
  state_is_SHUTDOWN = PLC_101.state_is_SHUTDOWN;
  h2_at_transfer_end = h2TransferCapture;
  when PLC_101.mode == TankSequenceController.Mode.WAIT_AFTER_TRANSFER and pre(PLC_101.mode) <> TankSequenceController.Mode.WAIT_AFTER_TRANSFER then
    h2TransferCapture = h2;
  end when;
  annotation(experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1),
             Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,0}, fillColor={245,245,245}, fillPattern=FillPattern.Solid),
                           Text(extent={{-100,78},{100,50}}, textString="Two Tank Demo")}),
             Diagram(graphics={Text(extent={{-160,140},{180,122}}, textString="SRC-101 -> XV-101 -> TK-101 -> XV-102 -> TK-102 -> XV-103 -> DRN-101")}) );
end TwoTankSystem;
