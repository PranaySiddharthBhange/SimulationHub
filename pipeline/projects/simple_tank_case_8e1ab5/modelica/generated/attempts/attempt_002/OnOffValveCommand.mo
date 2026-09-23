model OnOffValveCommand
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput flowSignal annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Real nominalFlow = 0;
equation
  flowSignal = if openCmd then nominalFlow else 0;
  annotation(
    Icon(graphics={Polygon(points={{-60,0},{0,40},{0,-40},{-60,0}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),Polygon(points={{60,0},{0,40},{0,-40},{60,0}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end OnOffValveCommand;
