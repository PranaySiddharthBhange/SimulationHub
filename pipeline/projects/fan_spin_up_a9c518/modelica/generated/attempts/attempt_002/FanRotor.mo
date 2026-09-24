model FanRotor
  parameter Modelica.Units.SI.Inertia J = 0.02;
  parameter Modelica.Units.SI.AngularVelocity initial_fan_speed_rad_s = 0.0;
  Modelica.Blocks.Interfaces.RealInput motor_torque_Nm annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput T_friction_Nm annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput T_aero_Nm annotation(Placement(transformation(extent={{-120,-80},{-100,-60}})));
  Modelica.Blocks.Interfaces.RealOutput fan_speed_rad_s annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Units.SI.AngularAcceleration domega_dt;
annotation(
  Icon(graphics={
    Ellipse(extent={{-70,-70},{70,70}}, lineColor={0,0,0}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
    Line(points={{0,0},{50,0}}, color={0,0,0}, thickness=1),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
initial equation
  fan_speed_rad_s = initial_fan_speed_rad_s;
equation
  J*domega_dt = motor_torque_Nm - T_friction_Nm - T_aero_Nm;
  der(fan_speed_rad_s) = domega_dt;
  assert(fan_speed_rad_s >= 0, "fan speed became negative");
end FanRotor;
