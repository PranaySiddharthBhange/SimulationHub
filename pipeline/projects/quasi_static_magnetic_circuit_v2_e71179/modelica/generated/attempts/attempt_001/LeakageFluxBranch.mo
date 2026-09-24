model LeakageFluxBranch
  parameter Real sigma(min=0, max=1) = 0.08 "Leakage flux ratio";
  parameter Real c_usefulFlux = 1/sigma - 1 "Useful-to-leakage flux ratio";
  Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort port_p annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Magnetic.FluxTubes.Interfaces.NegativeMagneticPort port_n annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Magnetic.FluxTubes.Basic.LeakageWithCoefficient leakage(c_usefulFlux=c_usefulFlux) annotation(Placement(transformation(extent={{-20,-20},{20,20}})));
equation
  connect(port_p, leakage.port_p) annotation(Line(points={{-100,0},{-20,0}}, color={0,127,255}));
  connect(leakage.port_n, port_n) annotation(Line(points={{20,0},{100,0}}, color={0,127,255}));
  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,-60},{100,60}}, lineColor={0,127,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
      Line(points={{-100,0},{-30,0}}, color={0,127,255}),
      Line(points={{30,0},{100,0}}, color={0,127,255}),
      Line(points={{-30,0},{0,30},{30,0}}, color={0,127,255}),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-80,-50},{80,-30}}, textString="leak" )}),
    Diagram(graphics={
      Rectangle(extent={{-100,-60},{100,60}}, lineColor={0,127,255}),
      Text(extent={{-90,30},{90,50}}, textString="LeakageWithCoefficient")
    }));
end LeakageFluxBranch;
