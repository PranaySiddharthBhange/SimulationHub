model ValveCommandSource
  parameter Modelica.Units.SI.VolumeFlowRate nominalFlow = 0.01 "Assumed commanded flow when open";
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput qCmd annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  qCmd = if openCmd then nominalFlow else 0;
annotation(
  Icon(graphics={
    Polygon(points={{-80,40},{-10,0},{-80,-40},{-80,40}}, lineColor={0,0,255}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
    Polygon(points={{80,40},{10,0},{80,-40},{80,40}}, lineColor={0,0,255}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
    Line(points={{-100,0},{-80,0}}, color={0,0,255}),
    Line(points={{80,0},{100,0}}, color={0,0,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-94,72},{98,94}}, textString="On/off valve command to nominal flow")})
);
end ValveCommandSource;
