model CondenserK1
  parameter Modelica.Units.SI.Temperature condensateTemperature = 353.15;
  Modelica.Blocks.Interfaces.RealInput qVapor annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealOutput qCond annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput Tcond annotation(Placement(transformation(extent={{100,-20},{120,0}})));
equation 
  qCond = max(qVapor, 0);
  Tcond = condensateTemperature;
  annotation(
    Icon(graphics={Ellipse(extent={{-70,-70},{70,70}}, lineColor={0,0,255}), Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end CondenserK1;
