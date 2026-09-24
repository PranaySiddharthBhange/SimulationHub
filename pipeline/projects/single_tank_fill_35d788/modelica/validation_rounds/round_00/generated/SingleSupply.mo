model SingleSupply
  Modelica.Blocks.Interfaces.RealOutput supplied_flow_m3_s annotation(Placement(transformation(extent={{100,-10},{120,10}})));
annotation(
  Icon(graphics={
    Ellipse(extent={{-70,-50},{30,50}}, lineColor={0,0,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
    Polygon(points={{30,0},{80,25},{80,-25},{30,0}}, lineColor={0,0,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-80,-80},{80,-60}}, textString="supply")
  }));
equation
  supplied_flow_m3_s = 0.01;
end SingleSupply;
