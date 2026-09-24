model TwoTankPlant
  parameter Modelica.Units.SI.Area A1 = 1.2;
  parameter Modelica.Units.SI.Area A2 = 1.4;
  parameter Modelica.Units.SI.Height tankHeight1 = 1.0;
  parameter Modelica.Units.SI.Height tankHeight2 = 1.0;
  parameter Modelica.Units.SI.Height level1_start = 0.05;
  parameter Modelica.Units.SI.Height level2_start = 0.05;
  parameter Modelica.Units.SI.VolumeFlowRate qFill = 0.006;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer = 0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain = 0.0050;

  Modelica.Blocks.Interfaces.BooleanInput valve1_cmd annotation(Placement(transformation(extent={{-120,50},{-100,70}}), iconTransformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.BooleanInput valve2_cmd annotation(Placement(transformation(extent={{-120,-10},{-100,10}}), iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.BooleanInput valve3_cmd annotation(Placement(transformation(extent={{-120,-70},{-100,-50}}), iconTransformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealOutput tank1_level_m annotation(Placement(transformation(extent={{100,40},{120,60}}), iconTransformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput tank2_level_m annotation(Placement(transformation(extent={{100,-60},{120,-40}}), iconTransformation(extent={{100,-60},{120,-40}})));

protected 
  Real valve1_open;
  Real valve2_open;
  Real valve3_open;
  Modelica.Units.SI.Height h1(start=level1_start, fixed=true);
  Modelica.Units.SI.Height h2(start=level2_start, fixed=true);
  Modelica.Units.SI.VolumeFlowRate q1in;
  Modelica.Units.SI.VolumeFlowRate q12;
  Modelica.Units.SI.VolumeFlowRate q2out;

equation 
  valve1_open = if valve1_cmd then 1 else 0;
  valve2_open = if valve2_cmd then 1 else 0;
  valve3_open = if valve3_cmd then 1 else 0;

  q1in = if h1 >= tankHeight1 then 0 else valve1_open*qFill;
  q12 = if h1 <= 0 then 0 else valve2_open*qTransfer;
  q2out = if h2 <= 0 then 0 else valve3_open*qDrain;

  der(h1) = (q1in - q12)/A1;
  der(h2) = (if h2 >= tankHeight2 then 0 else q12 - q2out)/A2;

  tank1_level_m = h1;
  tank2_level_m = h2;

  annotation(
    Icon(graphics={
      Rectangle(extent={{-90,20},{-20,-80}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{20,20},{90,-80}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),
      Polygon(points={{-100,60},{-80,70},{-80,50},{-100,60}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),
      Polygon(points={{0,-10},{20,0},{20,-20},{0,-10}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),
      Polygon(points={{100,-50},{80,-40},{80,-60},{100,-50}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-88,8},{-22,-8}}, textString="TK-101"),
      Text(extent={{22,8},{88,-8}}, textString="TK-102")
    }),
    Diagram(graphics={
      Rectangle(extent={{-90,20},{-20,-80}}, lineColor={0,0,255}),
      Rectangle(extent={{20,20},{90,-80}}, lineColor={0,0,255}),
      Text(extent={{-92,34},{-18,24}}, textString="Tank 1"),
      Text(extent={{18,34},{92,24}}, textString="Tank 2")
    }));
end TwoTankPlant;
