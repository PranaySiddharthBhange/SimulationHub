model MagneticGroundUnit
  Modelica.Blocks.Interfaces.RealInput reference_At annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
equation
  assert(abs(reference_At) <= 1e-12, "Magnetic ground expects zero magnetic reference potential");
 annotation(
  Icon(graphics={
    Line(points={{0,60},{0,10}}, color={0,0,0}),
    Line(points={{-40,10},{40,10}}, color={0,0,0}),
    Line(points={{-28,-10},{28,-10}}, color={0,0,0}),
    Line(points={{-16,-30},{16,-30}}, color={0,0,0}),
    Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={
    Line(points={{0,60},{0,10}}, color={0,0,0}),
    Line(points={{-40,10},{40,10}}, color={0,0,0}),
    Line(points={{-28,-10},{28,-10}}, color={0,0,0}),
    Line(points={{-16,-30},{16,-30}}, color={0,0,0})}));
end MagneticGroundUnit;
