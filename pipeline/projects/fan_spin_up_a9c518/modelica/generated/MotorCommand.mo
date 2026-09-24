model MotorCommand
  parameter Modelica.Units.SI.Time motor_start_time_s = 5.0;
  parameter Modelica.Units.SI.Torque torque_magnitude_Nm = 0.5;
  Modelica.Blocks.Interfaces.BooleanOutput motor_on_cmd annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.RealOutput motor_torque_Nm annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),
    Text(extent={{-90,20},{90,70}}, textString="Motor\nCommand"),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
equation
  motor_on_cmd = time >= motor_start_time_s;
  motor_torque_Nm = if motor_on_cmd then torque_magnitude_Nm else 0;
end MotorCommand;
