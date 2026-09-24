model ConnectingValve
  Modelica.Blocks.Interfaces.BooleanOutput openCmd annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Time openTime_s = 5.0;
equation
  openCmd = time >= openTime_s;
annotation(
  Icon(graphics={
    Polygon(points={{-60,40},{0,0},{-60,-40},{-60,40}}, lineColor={0,0,0}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),
    Polygon(points={{60,40},{0,0},{60,-40},{60,40}}, lineColor={0,0,0}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  })
);
end ConnectingValve;