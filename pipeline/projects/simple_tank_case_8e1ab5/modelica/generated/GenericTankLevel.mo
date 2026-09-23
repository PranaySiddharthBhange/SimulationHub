model GenericTankLevel
  Modelica.Blocks.Interfaces.RealInput inflow annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput outflow annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Volume level_start = 0;
equation
  level = level_start;
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}, fillColor={215,215,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end GenericTankLevel;
