model IdealClosingSwitch
  parameter Modelica.Units.SI.Time closeTime = 5.0;
  Modelica.Electrical.Analog.Interfaces.Pin p annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Electrical.Analog.Interfaces.Pin n annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Blocks.Interfaces.BooleanOutput closed annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Electrical.Analog.Ideal.IdealClosingSwitch sw annotation(Placement(transformation(extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.BooleanStep cmd(startTime=closeTime, startValue=false) annotation(Placement(transformation(extent={{-70,40},{-50,60}})));
equation
  connect(p, sw.p) annotation(Line(points={{-100,0},{-10,0}}, color={0,127,255}));
  connect(sw.n, n) annotation(Line(points={{10,0},{100,0}}, color={0,127,255}));
  connect(cmd.y, sw.control) annotation(Line(points={{-49,50},{0,50},{0,12}}, color={255,0,255}));
  connect(cmd.y, closed) annotation(Line(points={{-49,50},{110,50},{110,60}}, color={255,0,255}));
  annotation(
    Icon(graphics={
      Line(points={{-90,0},{-20,0}}, color={0,0,0}),
      Line(points={{20,0},{90,0}}, color={0,0,0}),
      Line(points={{-20,0},{20,20}}, color={0,0,0}),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-80,70},{80,90}}, textString="closes at closeTime")})
  );
end IdealClosingSwitch;
