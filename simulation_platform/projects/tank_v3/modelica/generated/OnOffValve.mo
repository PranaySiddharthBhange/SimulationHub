model OnOffValve
  extends Modelica.Blocks.Icons.PartialBooleanBlock;
  parameter Real qNominal(unit="m3/s") = 0.001;
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,-20},{-80,20}})));
  Modelica.Blocks.Interfaces.RealOutput q(unit="m3/s") annotation(Placement(transformation(extent={{100,-10},{120,10}})));
protected 
  Modelica.Blocks.Math.BooleanToReal cmdToReal(realTrue=qNominal, realFalse=0) annotation(Placement(transformation(extent={{-20,-10},{0,10}})));
equation 
  connect(openCmd, cmdToReal.u) annotation(Line(points={{-100,0},{-22,0}}, color={255,0,255}));
  connect(cmdToReal.y, q) annotation(Line(points={{1,0},{110,0}}, color={0,0,127}));
  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,128,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
                             Polygon(points={{-60,40},{0,40},{0,70},{60,0},{0,-70},{0,-40},{-60,-40},{-60,40}}, lineColor={0,128,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
                             Text(extent={{-92,92},{92,72}}, textString="Valve"),
                             Text(extent={{-94,-76},{94,-94}}, textString="q=%qNominal")}),
             Diagram(graphics={Text(extent={{-90,76},{90,56}}, textString="Boolean open -> nominal flow")}) );
end OnOffValve;
