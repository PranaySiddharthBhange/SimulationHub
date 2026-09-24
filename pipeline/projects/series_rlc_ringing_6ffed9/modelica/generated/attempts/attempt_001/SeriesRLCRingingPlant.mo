model SeriesRLCRingingPlant
  parameter Modelica.Units.SI.Capacitance C = 1;
  parameter Modelica.Units.SI.Resistance R = 0.2;
  parameter Modelica.Units.SI.Inductance L = 1;
  parameter Modelica.Units.SI.Voltage vC0 = 10;
  parameter Modelica.Units.SI.Current i0 = 0;
  Modelica.Blocks.Interfaces.BooleanInput switchClosed annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealOutput capacitor_voltage_V annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput loop_current_A annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
protected 
  Modelica.Units.SI.Voltage vC(start=vC0, fixed=true);
  Modelica.Units.SI.Current iL(start=i0, fixed=true);
annotation(
  Icon(graphics={
    Rectangle(extent={{-80,40},{-40,-40}}, lineColor={0,0,255}),
    Line(points={{-20,40},{-20,-40}}, color={0,0,255}),
    Line(points={{-10,40},{-10,-40}}, color={0,0,255}),
    Line(points={{10,0},{50,0}}, color={0,0,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={
    Text(extent={{-94,88},{94,72}}, textString="Precharged C released into series R-L when switch closes") }));
equation
  capacitor_voltage_V = vC;
  loop_current_A = iL;
  der(vC) = if switchClosed then -iL/C else 0;
  der(iL) = if switchClosed then (vC - R*iL)/L else 0;
end SeriesRLCRingingPlant;
