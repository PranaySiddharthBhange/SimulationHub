model FanSystem
  FanRotor fanRotor(J=0.02, omega_start=0)
    annotation(Placement(transformation(extent={{-10,-10},{30,30}})));
  MotorTorqueSource motor(torqueMagnitude=0.5, startTime=5)
    annotation(Placement(transformation(extent={{-90,30},{-50,70}})));
  BearingFrictionLoss bearing(b=0.01)
    annotation(Placement(transformation(extent={{-90,-10},{-50,30}})));
  AerodynamicLoadLoss aerodynamic(k_fan=0.0004)
    annotation(Placement(transformation(extent={{-90,-70},{-50,-30}})));
  Modelica.Blocks.Math.BooleanToReal motorCmdReal(realTrue=1, realFalse=0)
    annotation(Placement(transformation(extent={{0,60},{20,80}})));

  Real fan_speed_rad_s;
  Real motor_on_cmd;
  Real motor_torque_Nm;
equation
  connect(motor.motorTorque, fanRotor.motorTorque) annotation(Line(points={{-49,-40},{-30,-40},{-30,20},{-10,20}}, color={0,0,127}));
  connect(bearing.torqueLoss, fanRotor.bearingTorque) annotation(Line(points={{-49,10},{-30,10},{-30,0},{-10,0}}, color={0,0,127}));
  connect(aerodynamic.torqueLoss, fanRotor.aeroTorque) annotation(Line(points={{-49,-50},{-30,-50},{-30,-20},{-10,-20}}, color={0,0,127}));
  connect(fanRotor.omega, bearing.omega) annotation(Line(points={{31,10},{50,10},{50,40},{-110,40},{-110,10},{-90,10}}, color={0,0,127}));
  connect(fanRotor.omega, aerodynamic.omega) annotation(Line(points={{31,10},{60,10},{60,-50},{-90,-50}}, color={0,0,127}));
  connect(motor.motorOnCmd, motorCmdReal.u) annotation(Line(points={{-49,70},{-10,70},{-10,70},{0,70}}, color={255,0,255}));

  fan_speed_rad_s = fanRotor.omega;
  motor_on_cmd = motorCmdReal.y;
  motor_torque_Nm = fanRotor.motorTorque;

  annotation(
    experiment(StartTime=0, StopTime=60, Tolerance=1e-6, Interval=0.01),
    Diagram(graphics={Text(extent={{-112,92},{96,82}}, textString="Fan spin-up with viscous and quadratic aerodynamic losses")}));
end FanSystem;
