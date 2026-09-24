model SimpleTank
  parameter Modelica.Units.SI.Area area;
  parameter Modelica.Units.SI.Height level_start=0;
  parameter Real w_start(unit="kg/kg")=0;
  parameter Modelica.Units.SI.Temperature T_start=293.15;
  parameter Modelica.Units.SI.Height levelMax;
  parameter Modelica.Units.SI.Height levelMin=0;
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput qOutCmd annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput wIn annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput TIn annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput Qcmd annotation(Placement(transformation(extent={{-10,100},{10,120}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput w annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.RealOutput T annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
protected 
  parameter Real rho=1000;
  parameter Real cp=4180;
  Real V(start=area*level_start);
  Real m(start=rho*area*level_start);
  Real mSalt(start=rho*area*level_start*w_start);
  Real U(start=rho*area*level_start*cp*T_start);
equation
  qOut = if level <= levelMin then 0 else qOutCmd;
  der(m) = qIn - qOut;
  der(mSalt) = qIn*wIn - qOut*w;
  der(U) = qIn*cp*TIn - qOut*cp*T + Qcmd;
  V = m/rho;
  level = min(levelMax, max(levelMin, V/area));
  w = if m > 1e-9 then mSalt/m else w_start;
  T = if m > 1e-9 then U/(m*cp) else T_start;
annotation(Icon(graphics={Rectangle(extent={{-80,-100},{80,100}}, lineColor={0,0,255}),Rectangle(extent={{-80,-100},{80,0}}, fillColor={85,170,255}, fillPattern=FillPattern.Solid, lineColor={85,170,255}),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end SimpleTank;
