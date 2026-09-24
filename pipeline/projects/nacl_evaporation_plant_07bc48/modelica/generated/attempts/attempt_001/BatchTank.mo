within ;
model BatchTank
  import Modelica.Units.SI;
  parameter SI.Area crossArea;
  parameter SI.Height height;
  parameter SI.Height maxLevel;
  parameter SI.Height initialLevel;
  parameter Real initial_w_NaCl(unit="kg/kg") = 0;
  parameter SI.Temperature initialTemperature = 293.15;
  parameter SI.Volume V0 = 0;
  parameter Boolean useHeatPort = false;
  parameter SI.Height emptyThreshold = 0.0;

  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,60},{-100,80}}), iconTransformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput qOutCmd annotation(Placement(transformation(extent={{-120,20},{-100,40}}), iconTransformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput wIn annotation(Placement(transformation(extent={{-120,-20},{-100,0}}), iconTransformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput TIn annotation(Placement(transformation(extent={{-120,-60},{-100,-40}}), iconTransformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput Qcmd if useHeatPort annotation(Placement(transformation(extent={{-20,100},{20,120}}), iconTransformation(extent={{-20,100},{20,120}})));

  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,60},{120,80}}), iconTransformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,20},{120,40}}), iconTransformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,-20},{120,0}}), iconTransformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput T annotation(Placement(transformation(extent={{100,-60},{120,-40}}), iconTransformation(extent={{100,-60},{120,-40}})));

protected 
  SI.Volume V(start=crossArea*initialLevel + V0, fixed=true);
  Real M_salt(start=(crossArea*initialLevel + V0)*WaterNaClMedium.density(initialTemperature,101325,initial_w_NaCl)*initial_w_NaCl, fixed=true);
  SI.Temperature Tstate(start=initialTemperature, fixed=true);
  SI.Density rho;
  SI.Mass m;
  SI.SpecificHeatCapacity cp;
  SI.VolumeFlowRate qOutLimited;
  SI.Power Qin;
  Real denom;

equation 
  rho = WaterNaClMedium.density(Tstate, 101325, max(0, min(1, if V > 0 then M_salt/max(1e-9, rho*V) else initial_w_NaCl)));
  m = rho*V;
  cp = WaterNaClMedium.specificHeatCapacityCp(Tstate, if m > 1e-9 then M_salt/m else initial_w_NaCl);
  level = (V - V0)/crossArea;
  qOutLimited = if level <= emptyThreshold then 0 else if level >= maxLevel and qIn < qOutCmd then max(qOutCmd,0) else max(qOutCmd,0);
  qOut = qOutLimited;
  der(V) = qIn - qOutLimited;
  der(M_salt) = qIn*wIn*WaterNaClMedium.density(TIn,101325,wIn) - qOutLimited*WaterNaClMedium.density(Tstate,101325,if m > 1e-9 then M_salt/m else initial_w_NaCl)*(if m > 1e-9 then M_salt/m else initial_w_NaCl);
  Qin = if useHeatPort then Qcmd else 0;
  denom = max(1.0, m*cp);
  der(Tstate) = (qIn*WaterNaClMedium.density(TIn,101325,wIn)*WaterNaClMedium.specificHeatCapacityCp(TIn,wIn)*(TIn - Tstate) + Qin)/denom;
  w_NaCl = if m > 1e-9 then max(0, min(1, M_salt/m)) else initial_w_NaCl;
  T = Tstate;
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}),Rectangle(extent={{-58,-78},{58,0}}, lineColor={0,127,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-90,86},{92,96}}, textString="BatchTank")})
  );
end BatchTank;
