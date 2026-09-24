model MotorDrive
  parameter Modelica.Units.SI.Torque torqueMagnitude = 0.5;
  Modelica.Blocks.Interfaces.BooleanInput motor_on_cmd
    annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Mechanics.Rotational.Interfaces.Flange_b shaft
    annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Blocks.Interfaces.RealOutput motor_torque_Nm
    annotation(Placement(transformation(extent={{100,50},{120,70}})));
protected 
  Modelica.Units.SI.Torque tau;
equation
  tau = if motor_on_cmd then torqueMagnitude else 0;
  shaft.tau = -tau;
  motor_torque_Nm = tau;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-80,-60},{80,60}}, lineColor={0,0,0}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-60,-20},{60,20}}, textString="M"),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={}));
end MotorDrive;
