model MeasuringCoil
  parameter Integer N = 50 "Measuring coil turns";
  Modelica.Electrical.Analog.Interfaces.PositivePin p annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Electrical.Analog.Interfaces.NegativePin n annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort port_p annotation(Placement(transformation(extent={{-10,90},{10,110}})));
  Modelica.Magnetic.FluxTubes.Interfaces.NegativeMagneticPort port_n annotation(Placement(transformation(extent={{-10,-110},{10,-90}})));
  Modelica.Magnetic.FluxTubes.Basic.ElectroMagneticConverter converter(N=N)
    annotation(Placement(transformation(extent={{-20,-20},{20,20}})));
equation
  connect(p, converter.p) annotation(Line(points={{-100,0},{-20,0}}, color={0,0,255}));
  connect(n, converter.n) annotation(Line(points={{100,0},{20,0}}, color={0,0,255}));
  connect(port_p, converter.port_p) annotation(Line(points={{0,100},{0,20}}, color={127,0,255}));
  connect(port_n, converter.port_n) annotation(Line(points={{0,-100},{0,-20}}, color={127,0,255}));
annotation(
  Icon(graphics={Rectangle(extent={{-60,40},{60,-40}}, lineColor={0,0,255}),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-40,10},{40,-10}}, textString="N=%N")}),
  Diagram(graphics={}));
end MeasuringCoil;
