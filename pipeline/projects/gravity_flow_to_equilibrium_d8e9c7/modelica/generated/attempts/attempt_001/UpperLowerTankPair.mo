model UpperLowerTankPair
  parameter Modelica.Units.SI.Area area_A = 0.5;
  parameter Modelica.Units.SI.Area area_B = 0.5;
  parameter Modelica.Units.SI.Height height_A = 1.0;
  parameter Modelica.Units.SI.Height height_B = 1.0;
  parameter Modelica.Units.SI.Height level_A_start = 0.80;
  parameter Modelica.Units.SI.Height level_B_start = 0.00;

  Modelica.Blocks.Interfaces.RealInput q_m3s annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput level_A_m annotation(Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput level_B_m annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
protected 
  Modelica.Units.SI.Height level_A(start=level_A_start, fixed=true);
  Modelica.Units.SI.Height level_B(start=level_B_start, fixed=true);
equation
  der(level_A) = -q_m3s/area_A;
  der(level_B) =  q_m3s/area_B;
  level_A_m = level_A;
  level_B_m = level_B;
  assert(level_A >= 0 and level_A <= height_A, "Tank A level out of bounds");
  assert(level_B >= 0 and level_B <= height_B, "Tank B level out of bounds");
annotation(
  Icon(graphics={Rectangle(extent={{-80,40},{-20,-40}}, lineColor={0,0,255}), Rectangle(extent={{20,40},{80,-40}}, lineColor={0,0,255}), Rectangle(extent={{-78,-40},{-22,24}}, lineColor={0,0,255}, fillColor={85,170,255}, fillPattern=FillPattern.Solid), Rectangle(extent={{22,-40},{78,-40}}, lineColor={0,0,255}, fillColor={85,170,255}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-94,74},{94,92}}, textString="Two equal-area open tanks")})
);
end UpperLowerTankPair;
