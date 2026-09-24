model CoolingTank
  parameter Modelica.Units.SI.Area crossArea;
  parameter Modelica.Units.SI.Height initialLevel;
  parameter Real initialWNaCl(unit="kg/kg") = 0;
  parameter Modelica.Units.SI.Temperature initialTemperature = 353.15;
  parameter Modelica.Units.SI.MassFlowRate inflow_nominal;
  parameter Modelica.Units.SI.MassFlowRate outflow_nominal;
  parameter Modelica.Units.SI.HeatFlowRate coolerDuty;
  Modelica.Blocks.Interfaces.RealInput inflowMassFlow annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput inflowW annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput inflowTempC annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.BooleanInput coolerOn annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.BooleanInput pumpOutOn annotation(Placement(transformation(extent={{-120,-100},{-100,-80}})));
  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.RealOutput temperature_C annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput outflowMass annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
protected 
  constant Modelica.Units.SI.Density rho = 1000;
  Modelica.Units.SI.Mass m(start=crossArea*initialLevel*rho, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=crossArea*initialLevel*rho*initialWNaCl, fixed=true);
  Modelica.Units.SI.Temperature T(start=initialTemperature, fixed=true);
  Modelica.Units.SI.MassFlowRate mIn;
  Modelica.Units.SI.MassFlowRate mOut;
  Real cpMix;
equation
  cpMix = WaterNaClMedium.cp(T, if m > 1e-9 then mSalt/m else initialWNaCl);
  mIn = inflowMassFlow;
  mOut = if pumpOutOn and level_m > 0.02 then min(outflow_nominal, m) else 0;
  der(m) = mIn - mOut;
  der(mSalt) = mIn*inflowW - mOut*(if m > 1e-9 then mSalt/m else 0);
  der(T) = if m > 1e-6 then (mIn*4180*((inflowTempC + 273.15) - T) + (if coolerOn then coolerDuty else 0))/(m*cpMix) else 0;
  level_m = m/(rho*crossArea);
  temperature_C = T - 273.15;
  w_NaCl = if m > 1e-9 then mSalt/m else initialWNaCl;
  outflowMass = mOut;
  annotation(Icon(graphics={Rectangle(extent={{-80,-80},{80,80}}, lineColor={0,128,255}),Rectangle(extent={{-80,-80},{80,0}}, lineColor={0,128,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end CoolingTank;
