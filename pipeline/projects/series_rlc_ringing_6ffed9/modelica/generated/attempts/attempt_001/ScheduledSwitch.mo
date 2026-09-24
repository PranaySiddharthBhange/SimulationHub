model ScheduledSwitch
  parameter Modelica.Units.SI.Time closeTime = 5.0;
  Modelica.Blocks.Interfaces.BooleanOutput closed annotation(Placement(transformation(extent={{100,-10},{120,10}})));
annotation(
  Icon(graphics={
    Line(points={{-80,0},{-10,0}}, color={0,0,0}),
    Line(points={{10,0},{80,0}}, color={0,0,0}),
    Line(points={{-10,0},{30,30}}, color={0,0,0}),
    Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={
    Text(extent={{-90,60},{90,20}}, textString="closes at closeTime") }));
equation
  closed = time >= closeTime;
end ScheduledSwitch;
