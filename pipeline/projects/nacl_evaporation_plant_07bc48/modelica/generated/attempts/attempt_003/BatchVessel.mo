model BatchVessel
  parameter Modelica.Units.SI.Area crossArea = 0.05;
  parameter Modelica.Units.SI.Height height = 0.4;
  parameter Modelica.Units.SI.Height level_start = 0.01;
  parameter Real w_start(unit="kg/kg") = 0.0;
  parameter Modelica.Units.SI.Temperature T_start = 293.15;
  parameter Modelica.Units.SI.Height max_level = height;

  Modelica.Blocks.Interfaces.RealInput mIn annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput wIn annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput TIn annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput mOutCmd annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput Qcmd annotation(Placement(transformation(extent={{-10,100},{10,120}})));

  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput temperatureK annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput mOut annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
protected
  Modelica.Units.SI.Mass m(start=WaterNaClMedium.density_pTw(T_start, 101325, w_start)*crossArea*level_start, fixed=true);
  Modelica.Units.SI.Mass mNaCl(start=WaterNaClMedium.density_pTw(T_start, 101325, w_start)*crossArea*level_start*w_start, fixed=true);
  Modelica.Units.SI.Temperature T(start=T_start, fixed=true);
  Modelica.Units.SI.Density rho;
  Real w(unit="kg/kg");
  Modelica.Units.SI.SpecificHeatCapacity cp;
  Modelica.Units.SI.MassFlowRate mOutLimited;
  Modelica.Units.SI.MassFlowRate mInLimited;
  Modelica.Units.SI.Volume V;
equation
  w = if m > 1e-9 then max(0.0, min(1.0, mNaCl/m)) else 0.0;
  rho = WaterNaClMedium.density_pTw(T, 101325, w);
  cp = WaterNaClMedium.cp_Tw(T, w);
  V = m/max(rho, 1e-6);
  level = V/crossArea;

  mOutLimited = if level <= 0 and mOutCmd > 0 then 0 else mOutCmd;
  mInLimited = if level >= max_level and mIn > mOutLimited then mOutLimited else mIn;
  mOut = mOutLimited;

  der(m) = mInLimited - mOutLimited;
  der(mNaCl) = mInLimited*wIn - mOutLimited*w;
  m*cp*der(T) = mInLimited*WaterNaClMedium.cp_Tw(TIn, wIn)*(TIn - T) + Qcmd;

  w_NaCl = w;
  temperatureK = T;

  annotation(Icon(graphics={
    Rectangle(extent={{-60,-100},{60,60}}, lineColor={0,0,255}),
    Rectangle(extent={{-56,-96},{56,-20}}, fillColor={85,170,255}, fillPattern=FillPattern.Solid, lineColor={85,170,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
end BatchVessel;
