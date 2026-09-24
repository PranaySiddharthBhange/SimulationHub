model CurrentRamp
  Modelica.Blocks.Interfaces.RealOutput y annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Current offset = 0 "Initial RMS current magnitude";
  parameter Modelica.Units.SI.Current height = 2.0 "Ramp height from offset to final RMS current magnitude";
  parameter Modelica.Units.SI.Time startTime = 0.10 "Ramp start time";
  parameter Modelica.Units.SI.Time duration = 0.40 "Ramp duration";
equation
  y = if time < startTime then offset else if time < startTime + duration then offset + height*(time - startTime)/duration else offset + height;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),
      Line(points={{-80,-60},{-20,-60},{40,40},{80,40}}, color={0,0,255}, thickness=1),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-80,-90},{80,-70}}, textString="I_rms")}),
    Diagram(graphics={
      Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}),
      Line(points={{-80,-60},{-20,-60},{40,40},{80,40}}, color={0,0,255}),
      Text(extent={{-96,70},{96,92}}, textString="0 A to 2 A RMS")
    }));
end CurrentRamp;
