model FanRotor
  parameter Modelica.Units.SI.Inertia J = 0.02;
  parameter Modelica.Units.SI.AngularVelocity w0 = 0;
  Modelica.Mechanics.Rotational.Interfaces.Flange_a shaft
    annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Blocks.Interfaces.RealOutput fan_speed_rad_s
    annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Mechanics.Rotational.Components.Inertia inertia(J=J, w(start=w0, fixed=true))
    annotation(Placement(transformation(extent={{-10,-10},{10,10}})));
equation
  connect(shaft, inertia.flange_a) annotation(Line(points={{-100,0},{-10,0}}, color={0,127,255}));
  fan_speed_rad_s = inertia.w;
  annotation(
    Icon(graphics={
      Ellipse(extent={{-70,-70},{70,70}}, lineColor={0,0,0}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
      Line(points={{0,0},{70,0}}, color={0,0,0}),
      Line(points={{0,0},{0,70}}, color={0,0,0}),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={}));
end FanRotor;
