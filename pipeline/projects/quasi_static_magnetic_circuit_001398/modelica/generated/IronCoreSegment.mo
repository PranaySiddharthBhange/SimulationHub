model IronCoreSegment
  parameter Modelica.Units.SI.Length length_m;
  parameter Modelica.Units.SI.Area area_m2;
  parameter Real mu_r;
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance reluctance(
    R_m=length_m/(Modelica.Constants.mu_0*mu_r*area_m2)) annotation(Placement(transformation(extent={{-20,-20},{20,20}})));
  Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort port_p annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Magnetic.FluxTubes.Interfaces.NegativeMagneticPort port_n annotation(Placement(transformation(extent={{90,-10},{110,10}})));
equation
  connect(port_p, reluctance.port_p) annotation(Line(points={{-100,0},{-20,0}}, color={0,127,255}));
  connect(reluctance.port_n, port_n) annotation(Line(points={{20,0},{100,0}}, color={0,127,255}));
  annotation(Icon(graphics={Rectangle(extent={{-80,40},{80,-40}}, lineColor={0,127,255}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end IronCoreSegment;
