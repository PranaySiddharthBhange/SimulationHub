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
  parameter SI.Height emptyThreshold = 0.0;
  parameter Boolean useHeatPort = false;

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
  SI.Temperature Tstate(start=initialTemperature, fixed=true);
  Real M_salt(start=(crossArea*initialLevel + V0)*WaterNaClMedium.density(initialTemperature,101325,initial_w_NaCl)*initial_w_NaCl, fixed=true);
  SI.Density rho;
  SI.Density rhoIn;
  SI.Density rhoOut;
  SI.Mass m;
  SI.SpecificHeatCapacity cp;
  SI.VolumeFlowRate qOutLimited;
  SI.Power Qin;
  Real wState(unit="kg/kg");

equation
  level = (V - V0)/crossArea;
  rho = WaterNaClMedium.density(Tstate, 101325, wState);
  m = rho*V;
  wState = if m > 1e-9 then max(0.0, min(1.0, M_salt/m)) else initial_w_NaCl;
  cp = WaterNaClMedium.specificHeatCapacityCp(Tstate, wState);
  rhoIn = WaterNaClMedium.density(TIn, 101325, wIn);
  rhoOut = WaterNaClMedium.density(Tstate, 101325, wState);
  qOutLimited = if level <= emptyThreshold then 0 else max(qOutCmd, 0);
  qOut = qOutLimited;
  der(V) = qIn - qOutLimited;
  der(M_salt) = qIn*rhoIn*wIn - qOutLimited*rhoOut*wState;
  Qin = if useHeatPort then Qcmd else 0;
  der(Tstate) = (qIn*rhoIn*WaterNaClMedium.specificHeatCapacityCp(TIn, wIn)*(TIn - Tstate) + Qin)/(max(1.0, m*cp));
  w_NaCl = wState;
  T = Tstate;
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}),Rectangle(extent={{-58,-78},{58,0}}, lineColor={0,127,255}, fillColor={170,213,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-90,86},{92,96}}, textString="BatchTank")})
  );
end BatchTank;
