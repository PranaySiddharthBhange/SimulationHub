model ConnectingValveFlow
  parameter Real k(unit="m2/s") = 0.025;
  Modelica.Blocks.Interfaces.RealInput level_A_m annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealInput level_B_m annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.BooleanInput valveOpen annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput q_m3s annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  q_m3s = if valveOpen then k*(level_A_m - level_B_m) else 0;
annotation(
  Icon(graphics={Polygon(points={{-60,40},{0,0},{-60,-40},{-60,40}}, lineColor={0,0,0}, fillColor={215,215,215}, fillPattern=FillPattern.Solid), Polygon(points={{60,40},{0,0},{60,-40},{60,40}}, lineColor={0,0,0}, fillColor={215,215,215}, fillPattern=FillPattern.Solid), Line(points={{-100,0},{-60,0}}, color={0,127,255}), Line(points={{60,0},{100,0}}, color={0,127,255}), Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-86,62},{88,84}}, textString="q = 0 when closed; q = k*(A-B) when open")})
);
end ConnectingValveFlow;
