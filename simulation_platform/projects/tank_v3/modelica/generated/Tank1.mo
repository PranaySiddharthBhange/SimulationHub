model Tank1
  extends Modelica.Blocks.Icons.Block;
  parameter Real A(unit="m2") = 1.20;
  parameter Real h0(unit="m") = 0.05;
  parameter Real hLow(unit="m") = 0.05;
  Modelica.Blocks.Interfaces.RealInput qIn(unit="m3/s") annotation(Placement(transformation(extent={{-120,20},{-80,60}})));
  Modelica.Blocks.Interfaces.RealInput qOut(unit="m3/s") annotation(Placement(transformation(extent={{-120,-60},{-80,-20}})));
  Modelica.Blocks.Interfaces.RealOutput h(unit="m") annotation(Placement(transformation(extent={{100,-10},{120,10}})));
protected 
  Modelica.Blocks.Math.Add netFlow(k1=1, k2=-1) annotation(Placement(transformation(extent={{-50,-10},{-30,10}})));
  Modelica.Blocks.Math.Gain invArea(k=1/A) annotation(Placement(transformation(extent={{0,-10},{20,10}})));
  Modelica.Blocks.Continuous.Integrator levelInt(k=1, y_start=h0, initType=Modelica.Blocks.Types.Init.InitialOutput) annotation(Placement(transformation(extent={{40,-10},{60,10}})));
equation 
  connect(qIn, netFlow.u1) annotation(Line(points={{-100,40},{-70,40},{-70,6},{-52,6}}, color={0,0,127}));
  connect(qOut, netFlow.u2) annotation(Line(points={{-100,-40},{-70,-40},{-70,-6},{-52,-6}}, color={0,0,127}));
  connect(netFlow.y, invArea.u) annotation(Line(points={{-29,0},{-2,0}}, color={0,0,127}));
  connect(invArea.y, levelInt.u) annotation(Line(points={{21,0},{38,0}}, color={0,0,127}));
  connect(levelInt.y, h) annotation(Line(points={{61,0},{110,0}}, color={0,0,127}));
  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),
                             Rectangle(extent={{-60,60},{60,-60}}, lineColor={0,0,255}),
                             Text(extent={{-80,88},{80,66}}, textString="TK-101"),
                             Text(extent={{-94,-70},{94,-92}}, textString="A=%A")}),
             Diagram(graphics={Text(extent={{-92,88},{92,72}}, textString="Tank 1 level integrator")}) );
end Tank1;
