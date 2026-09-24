model ValveOpenSchedule
  parameter Modelica.Units.SI.Time valveOpenTime_s = 5.0;
  Modelica.Blocks.Interfaces.BooleanOutput valveOpen annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  valveOpen = time >= valveOpenTime_s;
annotation(
  Icon(graphics={Rectangle(extent={{-80,60},{80,-60}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-70,10},{70,-10}}, textString="t>=5 s"), Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-98,72},{98,92}}, textString="Closed for 0..5 s, open afterwards")})
);
end ValveOpenSchedule;
