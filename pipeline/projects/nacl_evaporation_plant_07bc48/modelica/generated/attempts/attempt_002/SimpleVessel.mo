within ;
model SimpleVessel
  parameter Modelica.Units.SI.Area crossArea;
  parameter Modelica.Units.SI.Height height;
  parameter Modelica.Units.SI.Height maxLevel;
  parameter Modelica.Units.SI.Height initialLevel;
  parameter Real initialWNaCl(unit="kg/kg") = 0;
  parameter Modelica.Units.SI.Temperature initialTemperature = 293.15;
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput qOutCmd annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput wIn annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput TIn annotation(Placement(transformation(extent={{-20,100},{20,120}})));
  Modelica.Blocks.Interfaces.RealInput Qext annotation(Placement(transformation(extent={{-60,100},{-20,120}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput wNaCl annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.RealOutput temperature annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
protected 
  parameter Modelica.Units.SI.Density rho = 1000;
  parameter Modelica.Units.SI.SpecificHeatCapacity cp = 4180;
  Modelica.Units.SI.Volume V;
  Modelica.Units.SI.Mass m(start=rho*crossArea*initialLevel, fixed=true);
  Real mSalt(start=rho*crossArea*initialLevel*initialWNaCl, fixed=true);
  Modelica.Units.SI.Energy U(start=rho*crossArea*initialLevel*cp*initialTemperature, fixed=true);
  Real wMix(unit="kg/kg");
  Modelica.Units.SI.VolumeFlowRate qOutLimited;
equation
  V = m/rho;
  level = V/crossArea;
  wMix = if m > 1e-9 then mSalt/m else 0;
  wNaCl = wMix;
  temperature = if m > 1e-9 then U/(m*cp) else initialTemperature;
  qOutLimited = if level <= 0 and qOutCmd > 0 then 0 else if level >= maxLevel and qIn > qOutCmd then min(qOutCmd, qIn) else qOutCmd;
  qOut = qOutLimited;
  der(m) = rho*(qIn - qOutLimited);
  der(mSalt) = rho*(qIn*wIn - qOutLimited*wMix);
  der(U) = rho*cp*(qIn*TIn - qOutLimited*temperature) + Qext;
  annotation(Icon(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}),Rectangle(extent={{-58,-80},{58,0}}, fillColor={0,127,255}, fillPattern=FillPattern.Solid, lineColor={0,127,255}),Text(extent={{-100,90},{100,130}}, textString="%name"),Text(extent={{-50,-10},{50,30}}, textString="Tank")}), Diagram(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255})}));
end SimpleVessel;
