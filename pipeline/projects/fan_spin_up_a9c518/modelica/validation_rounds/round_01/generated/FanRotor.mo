model FanRotor
  parameter Modelica.Units.SI.Inertia J = 0.02 "shaft rotational inertia from 01_fan_nonideal_spinup.txt";
  parameter Modelica.Units.SI.AngularVelocity omega_start = 0 "fan initial speed from 01_fan_nonideal_spinup.txt";

  Modelica.Blocks.Interfaces.RealInput motorTorque(unit="N.m")
    annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput bearingTorque(unit="N.m")
    annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput aeroTorque(unit="N.m")
    annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput omega(unit="rad/s")
    annotation(Placement(transformation(extent={{100,-10},{120,10}})));
protected
  Modelica.Units.SI.AngularAcceleration domega_dt;
initial equation
  omega = omega_start;
equation
  J*der(omega) = motorTorque - bearingTorque - aeroTorque;
  domega_dt = der(omega);
  annotation(
    Icon(graphics={
      Ellipse(extent={{-70,-70},{70,70}}, lineColor={0,0,255}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
      Line(points={{0,0},{55,0}}, color={0,0,255}, thickness=1),
      Line(points={{-90,0},{-70,0}}, color={0,0,255}),
      Line(points={{70,0},{90,0}}, color={0,0,255}),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-86,78},{92,58}}, textString="J*der(omega)=Tm-Tb-Ta")}));
end FanRotor;
