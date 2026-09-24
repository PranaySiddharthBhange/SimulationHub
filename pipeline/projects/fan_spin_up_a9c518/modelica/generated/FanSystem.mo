model FanSystem
  MotorCommand motorCommand annotation(Placement(transformation(extent={{-90,50},{-50,90}})));
  BearingFriction bearingFriction annotation(Placement(transformation(extent={{-10,40},{30,80}})));
  AerodynamicLoad aerodynamicLoad annotation(Placement(transformation(extent={{-10,-20},{30,20}})));
  FanRotor fanRotor annotation(Placement(transformation(extent={{60,10},{100,50}})));

  Real fan_speed_rad_s;
  Real motor_on_cmd;
  Real motor_torque_Nm;
  Real torque_balance_residual_Nm;
annotation(
  experiment(StartTime=0, StopTime=60, Tolerance=1e-6, Interval=0.1),
  Icon(graphics={
    Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0}),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
equation
  connect(motorCommand.motor_torque_Nm, fanRotor.motor_torque_Nm) annotation(Line(points={{-49,20},{20,20},{20,40},{60,40}}, color={0,0,127}));
  connect(fanRotor.fan_speed_rad_s, bearingFriction.omega_rad_s) annotation(Line(points={{101,30},{120,30},{120,90},{-40,90},{-40,60},{-10,60}}, color={0,0,127}));
  connect(bearingFriction.T_friction_Nm, fanRotor.T_friction_Nm) annotation(Line(points={{31,60},{40,60},{40,24},{60,24}}, color={0,0,127}));
  connect(fanRotor.fan_speed_rad_s, aerodynamicLoad.omega_rad_s) annotation(Line(points={{101,30},{120,30},{120,-40},{-40,-40},{-40,0},{-10,0}}, color={0,0,127}));
  connect(aerodynamicLoad.T_aero_Nm, fanRotor.T_aero_Nm) annotation(Line(points={{31,0},{40,0},{40,-8},{60,-8}}, color={0,0,127}));
  fan_speed_rad_s = fanRotor.fan_speed_rad_s;
  motor_on_cmd = if motorCommand.motor_on_cmd then 1 else 0;
  motor_torque_Nm = motorCommand.motor_torque_Nm;
  torque_balance_residual_Nm = motor_torque_Nm - (0.01*fan_speed_rad_s + 0.0004*fan_speed_rad_s*fan_speed_rad_s);
end FanSystem;
