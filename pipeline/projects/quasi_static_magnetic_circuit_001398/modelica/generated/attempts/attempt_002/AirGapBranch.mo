model AirGapBranch
  parameter Modelica.Units.SI.Length length_m;
  parameter Modelica.Units.SI.Area area_m2;
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance gapReluctance(
    R_m=length_m/(Modelica.Constants.mu_0*area_m2)) annotation(Placement(transformation(extent={{-20,-20},{20,20}})));
  Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor fluxSensor annotation(Placement(transformation(extent={{40,-20},{80,20}})));
  Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort port_p annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Magnetic.FluxTubes.Interfaces.NegativeMagneticPort port_n annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_gap_Wb annotation(Placement(transformation(extent={{100,50},{120,70}})));
equation
  connect(port_p, gapReluctance.port_p) annotation(Line(points={{-100,0},{-20,0}}, color={0,127,255}));
  connect(gapReluctance.port_n, fluxSensor.port_p) annotation(Line(points={{20,0},{40,0}}, color={0,127,255}));
  connect(fluxSensor.port_n, port_n) annotation(Line(points={{80,0},{100,0}}, color={0,127,255}));
  Phi_gap_Wb = fluxSensor.Phi;
  annotation(Icon(graphics={Line(points={{-80,0},{-20,0}}, color={0,127,255}),Line(points={{20,0},{80,0}}, color={0,127,255}),Line(points={{-20,30},{-20,-30}}, color={0,127,255}),Line(points={{20,30},{20,-30}}, color={0,127,255}),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end AirGapBranch;
