model OnOffFlowValve
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-10},{-100,10}}), iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput volumeFlow annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.VolumeFlowRate nominalFlow = 0.001;
equation
  volumeFlow = if openCmd then nominalFlow else 0;
  annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={Polygon(points={{-60,40},{0,0},{-60,-40},{-60,40}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid), Polygon(points={{60,40},{0,0},{60,-40},{60,40}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name")}), Diagram(coordinateSystem(extent={{-100,-100},{100,100}})));
end OnOffFlowValve;
