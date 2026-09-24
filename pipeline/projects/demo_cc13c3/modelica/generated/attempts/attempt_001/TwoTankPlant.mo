model TwoTankPlant
  Modelica.Blocks.Interfaces.RealInput u1 annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput u2 annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput u3 annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealOutput tank1_level_m annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput tank2_level_m annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Area A1 = 1.2;
  parameter Modelica.Units.SI.Area A2 = 1.4;
  parameter Modelica.Units.SI.VolumeFlowRate qFill = 0.0060;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer = 0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain = 0.0050;
  parameter Modelica.Units.SI.Height h1_start = 0.05;
  parameter Modelica.Units.SI.Height h2_start = 0.05;
  parameter Modelica.Units.SI.Height hLow1 = 0.05;
  parameter Modelica.Units.SI.Height hLow2 = 0.05;
  parameter Modelica.Units.SI.Height hHigh1 = 0.80;
  parameter Modelica.Units.SI.Height hMax = 1.0;
  parameter Modelica.Units.SI.Height hFloor = 0.0 "Assumed physical floor strictly below low-level threshold";
  Modelica.Units.SI.Height h1(start=h1_start, nominal=1);
  Modelica.Units.SI.Height h2(start=h2_start, nominal=1);
protected 
  Real q1eff(unit="m3/s");
  Real q2eff(unit="m3/s");
  Real q3eff(unit="m3/s");
equation
  q1eff = if h1 >= hMax then 0 else u1*qFill;
  q2eff = if h1 <= hFloor or h2 >= hMax then 0 else u2*qTransfer;
  q3eff = if h2 <= hFloor then 0 else u3*qDrain;
  der(h1) = (q1eff - q2eff)/A1;
  der(h2) = (q2eff - q3eff)/A2;
  tank1_level_m = h1;
  tank2_level_m = h2;
  assert(h1 >= hFloor - 1e-9 and h1 <= hMax + 1e-9, "Tank 1 level out of physical range");
  assert(h2 >= hFloor - 1e-9 and h2 <= hMax + 1e-9, "Tank 2 level out of physical range");
annotation(
  Icon(graphics={Rectangle(extent={{-80,60},{-20,-60}}, lineColor={0,0,255}, fillColor={213,255,213}, fillPattern=FillPattern.Solid),Rectangle(extent={{20,60},{80,-60}}, lineColor={0,0,255}, fillColor={213,255,213}, fillPattern=FillPattern.Solid),Line(points={{-100,60},{-80,60}}, color={0,0,127}),Line(points={{-100,0},{-20,0}}, color={0,0,127}),Line(points={{-100,-60},{20,-60}}, color={0,0,127}),Line(points={{80,30},{100,30}}, color={0,0,127}),Line(points={{80,-30},{100,-30}}, color={0,0,127}),Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-92,76},{-34,64}}, textString="u1"),Text(extent={{-92,16},{-34,4}}, textString="u2"),Text(extent={{-92,-44},{-34,-56}}, textString="u3"),Text(extent={{30,44},{94,32}}, textString="h1"),Text(extent={{30,-16},{94,-28}}, textString="h2")}));
end TwoTankPlant;
