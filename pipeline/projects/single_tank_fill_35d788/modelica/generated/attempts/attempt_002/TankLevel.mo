model TankLevel
  parameter Modelica.Units.SI.Area crossArea = 0.5;
  parameter Modelica.Units.SI.Height tankHeight = 1.0;
  parameter Modelica.Units.SI.Height initialLevel = 0.0;
  Modelica.Blocks.Interfaces.RealInput inflow_m3_s annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput tank_level_m annotation(Placement(transformation(extent={{100,-10},{120,10}})));
annotation(
  Icon(graphics={
    Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
    Rectangle(extent={{-58,-80},{58,20}}, lineColor={0,0,255}, fillColor={85,170,255}, fillPattern=FillPattern.Solid),
    Line(points={{-80,80},{80,80}}, color={0,0,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-90,-110},{90,-90}}, textString="level")
  }));
initial equation
  tank_level_m = initialLevel;
equation
  der(tank_level_m) = if tank_level_m >= tankHeight and inflow_m3_s > 0 then 0 else inflow_m3_s / crossArea;
  assert(tank_level_m >= 0, "tank_level_m below 0 m");
  assert(tank_level_m <= tankHeight + 1e-6, "tank_level_m above tank height");
end TankLevel;
