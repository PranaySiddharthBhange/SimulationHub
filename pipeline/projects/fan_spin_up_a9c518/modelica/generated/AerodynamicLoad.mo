model AerodynamicLoad
  parameter Real k_fan(unit="N.m.s2/rad2") = 0.0004;
  Modelica.Blocks.Interfaces.RealInput omega_rad_s annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput T_aero_Nm annotation(Placement(transformation(extent={{100,-10},{120,10}})));
annotation(
  Icon(graphics={
    Ellipse(extent={{-80,-60},{80,60}}, lineColor={0,100,200}, fillColor={210,235,255}, fillPattern=FillPattern.Solid),
    Text(extent={{-88,-10},{88,30}}, textString="Aero\nload"),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
equation
  T_aero_Nm = k_fan*omega_rad_s*omega_rad_s;
end AerodynamicLoad;
