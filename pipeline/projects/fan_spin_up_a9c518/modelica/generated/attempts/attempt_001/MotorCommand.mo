model MotorCommand
  parameter Modelica.Units.SI.Time motor_start_time_s = 5;
  Modelica.Blocks.Interfaces.BooleanOutput motor_on_cmd
    annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  motor_on_cmd = time >= motor_start_time_s;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-80,-60},{80,60}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),
      Text(extent={{-70,-10},{70,30}}, textString="start@5s"),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={}));
end MotorCommand;
