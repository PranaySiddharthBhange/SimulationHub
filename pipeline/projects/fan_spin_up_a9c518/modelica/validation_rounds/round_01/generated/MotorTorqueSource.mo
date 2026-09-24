model MotorTorqueSource
  parameter Modelica.Units.SI.Torque torqueMagnitude = 0.5 "motor torque magnitude from 01_fan_nonideal_spinup.txt";
  parameter Modelica.Units.SI.Time startTime = 5 "motor start time from 01_fan_nonideal_spinup.txt";

  Modelica.Blocks.Interfaces.BooleanOutput motorOnCmd
    annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.RealOutput motorTorque(unit="N.m")
    annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
equation
  motorOnCmd = time >= startTime;
  motorTorque = if motorOnCmd then torqueMagnitude else 0;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,-80},{100,80}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),
      Text(extent={{-90,20},{90,60}}, textString="Motor"),
      Text(extent={{-90,-10},{90,20}}, textString="step torque"),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-92,-92},{94,-112}}, textString="on at t>=startTime")}));
end MotorTorqueSource;
