model SimpleBatchTank
  parameter Modelica.Units.SI.Area area=0.05;
  parameter Modelica.Units.SI.Height levelMax=0.4;
  parameter Modelica.Units.SI.Height levelStart=0.0;
  parameter Real XStart(unit="kg/kg")=0.0;
  parameter Modelica.Units.SI.Temperature TStart=293.15;
  parameter Modelica.Units.SI.Height levelMin=1e-6;
  parameter Modelica.Units.SI.Mass mMin=1e-6;
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput qOutCmd annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput Xin annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput Tin annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput Qcmd annotation(Placement(transformation(extent={{-20,100},{20,120}})));
  Modelica.Blocks.Interfaces.RealInput evapWater annotation(Placement(transformation(extent={{60,100},{100,120}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput X annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.RealOutput TdegC annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
protected 
  parameter Real rho=1000;
  parameter Real cp=4180;
  Modelica.Units.SI.Mass m(start=rho*area*levelStart, nominal=10);
  Modelica.Units.SI.Mass mSalt(start=rho*area*levelStart*XStart, nominal=1);
  Modelica.Units.SI.Energy E(start=rho*area*levelStart*cp*TStart, nominal=1e6);
  Real Xcalc(unit="kg/kg");
  Modelica.Units.SI.Temperature T;
  Real qOutLimited(unit="kg/s");
  Real evapLimited(unit="kg/s");
 equation 
  qOutLimited = if m <= mMin then 0 else qOutCmd;
  evapLimited = if m <= mMin then 0 else evapWater;
  der(m) = rho*qIn - qOutLimited - evapLimited;
  der(mSalt) = rho*qIn*Xin - qOutLimited*Xcalc;
  der(E) = rho*qIn*cp*Tin - qOutLimited*cp*T - evapLimited*cp*T + Qcmd;
  Xcalc = mSalt/max(m, mMin);
  T = E/max(cp*m, cp*mMin);
  level = m/(rho*area);
  X = Xcalc;
  TdegC = T - 273.15;
  qOut = qOutLimited/rho;
  assert(level >= -1e-6, "level below zero");
  assert(level <= levelMax + 1e-6, "level above maximum");
  assert(X >= -1e-6 and X <= 1 + 1e-6, "mass fraction out of range");
  assert(T > 0, "temperature below absolute zero");
  annotation(
    Icon(graphics={Rectangle(extent={{-80,-100},{80,60}}, lineColor={0,0,255}, fillColor={215,215,255}, fillPattern=FillPattern.Solid), Rectangle(extent={{-80,-100},{80,-20}}, lineColor={0,0,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid), Text(extent={{-100,80},{100,110}}, textString="%name")})
  );
end SimpleBatchTank;
