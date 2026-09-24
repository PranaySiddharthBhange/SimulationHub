model ScheduledSwitch
  parameter Modelica.Units.SI.Time closeTime = 5.0;
  Modelica.Blocks.Interfaces.BooleanOutput closed annotation(Placement(transformation(extent={{100,-10},{120,10}})));
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-60},{100,60}}, lineColor={0,0,0}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
    Line(points={{-80,0},{-10,0}}, color={0,0,0}),
    Line(points={{10,0},{80,0}}, color={0,0,0}),
    Line(points={{-10,0},{30,25}}, color={0,0,0}, thickness=1),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-90,-100},{90,-70}}, textString="t=%closeTime")
  }));
equation
  closed = time >= closeTime;
end ScheduledSwitch;
