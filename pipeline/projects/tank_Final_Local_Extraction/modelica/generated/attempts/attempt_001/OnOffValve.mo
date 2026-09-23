model OnOffValve
  import Modelica.Units.SI;
  parameter SI.VolumeFlowRate nominalFlow;
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput flowOut annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  flowOut = if openCmd then nominalFlow else 0;
  annotation(
    Icon(graphics={Polygon(points={{-80,40},{0,0},{-80,-40},{-80,40}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid), Polygon(points={{80,40},{0,0},{80,-40},{80,40}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end OnOffValve;