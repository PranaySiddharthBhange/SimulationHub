model BufferTank
  parameter Modelica.Units.SI.Area crossArea;
  parameter Modelica.Units.SI.Height initialLevel;
  parameter Real initialWNaCl(unit="kg/kg") = 0;
  parameter Modelica.Units.SI.MassFlowRate inflow_nominal;
  parameter Modelica.Units.SI.MassFlowRate outflow_nominal;
  Modelica.Blocks.Interfaces.BooleanInput inflowOn annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.BooleanInput outflowOn annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput inflowW annotation(Placement(transformation(extent={{-120,80},{-100,100}})));
  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.RealOutput massOut annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
protected 
  constant Modelica.Units.SI.Density rho = 1000;
  Modelica.Units.SI.Mass m(start=crossArea*initialLevel*rho, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=crossArea*initialLevel*rho*initialWNaCl, fixed=true);
  Modelica.Units.SI.MassFlowRate mIn;
  Modelica.Units.SI.MassFlowRate mOut;
equation
  mIn = if inflowOn then inflow_nominal else 0;
  mOut = if outflowOn and level_m > 0 then min(outflow_nominal, m) else 0;
  der(m) = mIn - mOut;
  der(mSalt) = mIn*inflowW - mOut*(if m > 1e-9 then mSalt/m else 0);
  level_m = m/(rho*crossArea);
  w_NaCl = if m > 1e-9 then mSalt/m else initialWNaCl;
  massOut = mOut;
  annotation(Icon(graphics={Rectangle(extent={{-80,-80},{80,80}}, lineColor={0,0,255}),Rectangle(extent={{-80,-80},{80,0}}, lineColor={0,0,255}, fillColor={85,170,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end BufferTank;
