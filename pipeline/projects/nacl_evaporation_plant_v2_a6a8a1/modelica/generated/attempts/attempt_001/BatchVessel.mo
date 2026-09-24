model BatchVessel
  parameter Modelica.Units.SI.Area area = 0.05;
  parameter Modelica.Units.SI.Height level_start = 0;
  parameter Modelica.Units.SI.Height levelMin = 1e-4;
  parameter Real X_start(unit="kg/kg") = 0;
  parameter Modelica.Units.SI.Temperature T_start = 293.15;
  parameter Modelica.Units.SI.Temperature T_in_default = 293.15;
  parameter Real X_in_default(unit="kg/kg") = 0;
  parameter Modelica.Units.SI.Density rho = 1000;
  parameter Modelica.Units.SI.SpecificHeatCapacity cp = 4180;
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput qOutCmd annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput Xin annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput Tin annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput Qdot annotation(Placement(transformation(extent={{-20,100},{20,120}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.RealOutput X annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput T annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
protected 
  parameter Modelica.Units.SI.Mass m_floor = 0.1;
  Modelica.Units.SI.Mass m(start=rho*area*level_start, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=rho*area*level_start*X_start, fixed=true);
  Modelica.Units.SI.Energy U(start=rho*area*level_start*cp*T_start, fixed=true);
  Real Xmix(unit="kg/kg");
  Modelica.Units.SI.VolumeFlowRate qOutEff;
  Modelica.Units.SI.MassFlowRate mIn;
  Modelica.Units.SI.MassFlowRate mOut;
equation 
  mIn = rho*max(qIn, 0);
  qOutEff = if level <= levelMin and qOutCmd > 0 then 0 else max(qOutCmd, 0);
  mOut = rho*qOutEff;
  der(m) = mIn - mOut;
  der(mSalt) = mIn*(if qIn > 0 then Xin else X_in_default) - mOut*Xmix;
  der(U) = mIn*cp*(if qIn > 0 then Tin else T_in_default) - mOut*cp*T + Qdot;
  Xmix = mSalt/max(m, m_floor);
  level = m/(rho*area);
  X = Xmix;
  T = U/(max(m, m_floor)*cp);
  qOut = qOutEff;
  assert(level >= -1e-6, "level below zero");
  assert(X >= -1e-6 and X <= 1 + 1e-6, "mass fraction out of range");
  assert(T > 0, "temperature below absolute zero");
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-100},{60,80}}, lineColor={0,0,255}), Rectangle(extent={{-58,-100},{58,-20}}, fillColor={170,213,255}, fillPattern=FillPattern.Solid, lineColor={0,0,255}), Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-90,86},{90,98}}, textString="Well-mixed vessel")})
  );
end BatchVessel;
