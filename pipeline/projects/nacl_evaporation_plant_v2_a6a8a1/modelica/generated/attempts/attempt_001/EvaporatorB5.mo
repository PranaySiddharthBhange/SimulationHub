model EvaporatorB5
  parameter Modelica.Units.SI.Area area = 0.06;
  parameter Modelica.Units.SI.Height level_start = 0;
  parameter Real X_start(unit="kg/kg") = 0.08;
  parameter Modelica.Units.SI.Temperature T_start = 293.15;
  parameter Modelica.Units.SI.Temperature T_in_default = 293.15;
  parameter Real X_in_default(unit="kg/kg") = 0.08;
  parameter Modelica.Units.SI.Density rho = 1000;
  parameter Modelica.Units.SI.SpecificHeatCapacity cp = 4180;
  parameter Modelica.Units.SI.SpecificEnthalpy hvMinusHl = 2.256e6;
  parameter Modelica.Units.SI.Height levelMin = 1e-4;
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput Xin annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput Tin annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput heaterQ annotation(Placement(transformation(extent={{-20,100},{20,120}})));
  Modelica.Blocks.Interfaces.RealInput condenserFlow annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput qConcCmd annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput X annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.RealOutput T annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Interfaces.RealOutput qVapor annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
  Modelica.Blocks.Interfaces.RealOutput qConc annotation(Placement(transformation(extent={{100,-90},{120,-70}})));
protected 
  parameter Modelica.Units.SI.Mass m_floor = 0.1;
  Modelica.Units.SI.Mass m(start=rho*area*level_start, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=rho*area*level_start*X_start, fixed=true);
  Modelica.Units.SI.Energy U(start=rho*area*level_start*cp*T_start, fixed=true);
  Real Xmix(unit="kg/kg");
  Modelica.Units.SI.VolumeFlowRate qConcEff;
  Modelica.Units.SI.MassFlowRate mIn;
  Modelica.Units.SI.MassFlowRate mConc;
  Modelica.Units.SI.MassFlowRate mVap;
  Modelica.Units.SI.Power Qup;
equation 
  mIn = rho*max(qIn, 0);
  Xmix = mSalt/max(m, m_floor);
  qConcEff = if level <= levelMin and qConcCmd > 0 then 0 else max(qConcCmd, 0);
  mConc = rho*qConcEff;
  Qup = condenserFlow*4200*10;
  mVap = if heaterQ > Qup and m > m_floor then (heaterQ - Qup)/hvMinusHl else 0;
  der(m) = mIn - mConc - mVap;
  der(mSalt) = mIn*Xin - mConc*Xmix;
  der(U) = mIn*cp*Tin - mConc*cp*T - mVap*hvMinusHl + heaterQ;
  level = m/(rho*area);
  X = Xmix;
  T = U/(max(m, m_floor)*cp);
  qVapor = mVap/rho;
  qConc = qConcEff;
  assert(level >= -1e-6, "B5 level below zero");
  assert(X >= -1e-6 and X <= 1 + 1e-6, "B5 mass fraction out of range");
  assert(T > 0, "B5 temperature below absolute zero");
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-100},{60,80}}, lineColor={255,0,0}), Rectangle(extent={{-58,-100},{58,-20}}, fillColor={255,230,170}, fillPattern=FillPattern.Solid, lineColor={255,0,0}), Ellipse(extent={{-30,20},{30,70}}, lineColor={255,0,0}), Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end EvaporatorB5;
