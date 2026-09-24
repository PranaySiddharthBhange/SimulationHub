within ;
model FlowActuator
  import Modelica.Units.SI;
  parameter SI.VolumeFlowRate qNominal;
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-20},{-100,0}}), iconTransformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
equation
  qOut = if openCmd then qNominal else 0;
  annotation(Icon(graphics={Polygon(points={{-60,0},{0,40},{0,-40},{-60,0}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Polygon(points={{60,0},{0,40},{0,-40},{60,0}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end FlowActuator;
