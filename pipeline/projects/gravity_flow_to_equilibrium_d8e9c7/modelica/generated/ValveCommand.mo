model ValveCommand
  Modelica.Blocks.Interfaces.BooleanOutput openCmd annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Time openTime = 5.0;
equation
  openCmd = time >= openTime;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-80,-60},{80,60}}, lineColor={255,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-70,-10},{70,30}}, textString="open@5s")}),
    Diagram(graphics={Rectangle(extent={{-80,-60},{80,60}}, lineColor={255,0,255})}));
end ValveCommand;