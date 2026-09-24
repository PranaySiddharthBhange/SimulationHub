model OpenTankLevel
  Modelica.Blocks.Interfaces.RealInput qIn_m3s annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput qOut_m3s annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Area crossArea = 0.5;
  parameter Modelica.Units.SI.Height height = 1.0;
  parameter Modelica.Units.SI.Height level_start = 0.0;
initial equation
  level_m = level_start;
equation
  der(level_m) = (qIn_m3s - qOut_m3s)/crossArea;
  assert(level_m >= 0 and level_m <= height, "tank level out of bounds");
  annotation(
    Icon(graphics={
      Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{-58,-80},{58,0}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-80,-100},{80,-140}}, textString="level")}),
    Diagram(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255})}));
end OpenTankLevel;