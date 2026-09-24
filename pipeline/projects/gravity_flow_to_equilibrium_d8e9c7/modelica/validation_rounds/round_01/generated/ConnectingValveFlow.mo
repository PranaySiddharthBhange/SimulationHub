model ConnectingValveFlow
  Modelica.Blocks.Interfaces.RealInput level_A_m annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealInput level_B_m annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-80},{-100,-60}})));
  Modelica.Blocks.Interfaces.RealOutput q_m3s annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Real k(unit="m2/s") = 0.025;
  parameter Real qFloor(unit="m3/s") = 0.0;
equation
  q_m3s = if openCmd then max(qFloor, k*(level_A_m - level_B_m)) else 0;
  annotation(
    Icon(graphics={
      Polygon(points={{-80,20},{-20,60},{-20,-20},{-80,20}}, lineColor={0,0,0}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),
      Polygon(points={{80,20},{20,60},{20,-20},{80,20}}, lineColor={0,0,0}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-90,-90},{90,-120}}, textString="q=k dH")}),
    Diagram(graphics={Line(points={{-100,0},{100,0}}, color={0,127,255})}));
end ConnectingValveFlow;