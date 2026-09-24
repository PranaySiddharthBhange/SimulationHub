model ReleaseCommand
  parameter Modelica.Units.SI.Time releaseTime = 5.0;
  Modelica.Blocks.Interfaces.BooleanOutput engaged
    annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  engaged = time < releaseTime;
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={235,235,255}, fillPattern=FillPattern.Solid),
    Text(extent={{-90,20},{90,60}}, textString="release @ %releaseTime"),
    Text(extent={{-100,110},{100,140}}, textString="%name")
  }));
end ReleaseCommand;
