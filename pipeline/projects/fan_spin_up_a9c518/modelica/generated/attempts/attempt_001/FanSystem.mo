model FanSystem
  FanRotor fanRotor(J=0.02, w0=0)
    annotation(Placement(transformation(extent={{-10,-10},{30,30}})));
  LossTorque lossTorque(b=0.01, k_fan=0.0004)
    annotation(Placement(transformation(extent={{50,-10},{90,30}})));
  MotorDrive motorDrive(torqueMagnitude=0.5)
    annotation(Placement(transformation(extent={{-10,-70},{30,-30}})));
  MotorCommand motorCommand(motor_start_time_s=5)
    annotation(Placement(transformation(extent={{-90,-70},{-50,-30}})));

  Modelica.Mechanics.Rotational.Components.Fixed fixed
    annotation(Placement(transformation(extent={{110,-10},{130,10}})));

  Modelica.Units.SI.AngularVelocity fan_speed_rad_s;
  Real motor_on_cmd;
  Modelica.Units.SI.Torque motor_torque_Nm;
equation
  connect(fanRotor.shaft, lossTorque.shaft) annotation(Line(points={{-10,0},{50,0}}, color={0,127,255}));
  connect(lossTorque.shaft, fixed.flange) annotation(Line(points={{110,0},{120,0}}, color={0,127,255}));
  connect(motorDrive.shaft, fanRotor.shaft) annotation(Line(points={{30,-50},{40,-50},{40,0},{-10,0}}, color={0,127,255}));
  connect(motorCommand.motor_on_cmd, motorDrive.motor_on_cmd) annotation(Line(points={{-49,-50},{-10,-50}}, color={255,0,255}));

  fan_speed_rad_s = fanRotor.fan_speed_rad_s;
  motor_on_cmd = if motorCommand.motor_on_cmd then 1 else 0;
  motor_torque_Nm = motorDrive.motor_torque_Nm;

  annotation(
    experiment(StartTime=0, StopTime=60, Tolerance=1e-8, Interval=0.01),
    Diagram(graphics={}),
    Icon(graphics={Text(extent={{-100,100},{100,140}}, textString="%name")}));
end FanSystem;
