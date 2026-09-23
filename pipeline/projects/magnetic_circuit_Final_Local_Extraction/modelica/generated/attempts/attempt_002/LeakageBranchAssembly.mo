model LeakageBranchAssembly
  parameter Modelica.Units.SI.Reluctance R_gap=1909859.3171027435;
  parameter Modelica.Units.SI.Reluctance R_leak=21963382.14668155;
  Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort port_p annotation(Placement(transformation(extent={{-110,-10},{-90,10}})));
  Modelica.Magnetic.FluxTubes.Interfaces.NegativeMagneticPort port_n annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance airGap(R_m=R_gap) annotation(Placement(transformation(extent={{-10,30},{10,50}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance leakagePath(R_m=R_leak) annotation(Placement(transformation(extent={{-10,-50},{10,-30}})));
  Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor gapFluxSensor annotation(Placement(transformation(extent={{30,30},{50,50}})));
  Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor leakFluxSensor annotation(Placement(transformation(extent={{30,-50},{50,-30}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_gap annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_leak annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
equation
  connect(port_p, airGap.port_p) annotation(Line(points={{-100,0},{-60,0},{-60,40},{-10,40}}, color={0,127,255}));
  connect(port_p, leakagePath.port_p) annotation(Line(points={{-100,0},{-60,0},{-60,-40},{-10,-40}}, color={0,127,255}));
  connect(airGap.port_n, gapFluxSensor.port_p) annotation(Line(points={{10,40},{30,40}}, color={0,127,255}));
  connect(gapFluxSensor.port_n, port_n) annotation(Line(points={{50,40},{70,40},{70,0},{100,0}}, color={0,127,255}));
  connect(leakagePath.port_n, leakFluxSensor.port_p) annotation(Line(points={{10,-40},{30,-40}}, color={0,127,255}));
  connect(leakFluxSensor.port_n, port_n) annotation(Line(points={{50,-40},{70,-40},{70,0},{100,0}}, color={0,127,255}));
  Phi_gap = gapFluxSensor.Phi;
  Phi_leak = leakFluxSensor.Phi;
  annotation(
    Icon(graphics={Line(points={{-100,0},{-40,0},{-40,40},{-10,40}}, color={0,127,255}),Line(points={{-100,0},{-40,0},{-40,-40},{-10,-40}}, color={0,127,255}),Line(points={{10,40},{40,40},{40,0},{100,0}}, color={0,127,255}),Line(points={{10,-40},{40,-40},{40,0},{100,0}}, color={0,127,255}),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-30,50},{30,80}}, textString="Gap"),Text(extent={{-40,-80},{40,-50}}, textString="Leak")})
  );
end LeakageBranchAssembly;
