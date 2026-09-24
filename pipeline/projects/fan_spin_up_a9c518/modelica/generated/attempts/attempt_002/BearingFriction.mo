model BearingFriction
  parameter Real b(unit="N.m.s/rad") = 0.01;
  Modelica.Blocks.Interfaces.RealInput omega_rad_s annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput T_friction_Nm annotation(Placement(transformation(extent={{100,-10},{120,10}})));
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-60},{100,60}}, lineColor={120,60,0}, fillColor={255,230,200}, fillPattern=FillPattern.Solid),
    Text(extent={{-88,-10},{88,30}}, textString="Bearing\nfriction"),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
equation
  T_friction_Nm = b*omega_rad_s;
end BearingFriction;
