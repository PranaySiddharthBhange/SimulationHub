model EvaporatorCondenser
  parameter Modelica.Units.SI.Area area = 0.06;
  parameter Modelica.Units.SI.Height level_start = 0.01;
  parameter Real w_start = 0;
  parameter Modelica.Units.SI.Temperature T_start = 293.15;
  parameter Modelica.Units.SI.Power heaterDuty = 20000;
  parameter Real rho = 1000;
  parameter Real cp = 4180;
  parameter Real evapGain = 1.9e-5 "kg/s/W assumed for executable evaporation";

  Modelica.Blocks.Interfaces.RealInput inlet_kg_s annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput inlet_w annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput inlet_T_K annotation(Placement(transformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.BooleanInput heaterOn annotation(Placement(transformation(extent={{-120,-40},{-100,-20}})));
  Modelica.Blocks.Interfaces.RealInput condenserFlow_kg_s annotation(Placement(transformation(extent={{-120,-80},{-100,-60}})));
  Modelica.Blocks.Interfaces.RealInput concOutCmd_kg_s annotation(Placement(transformation(extent={{-120,-120},{-100,-100}})));

  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput temp_K annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.RealOutput condensate_kg_s annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput condensate_T_K annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
  Modelica.Blocks.Interfaces.RealOutput concentrateOut_kg_s annotation(Placement(transformation(extent={{100,-80},{120,-60}})));

  Modelica.Units.SI.Mass m(start=area*level_start*rho, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=area*level_start*rho*w_start, fixed=true);
  Modelica.Units.SI.Temperature T(start=T_start, fixed=true);
  Boolean heaterPermissive;
  Real evap_kg_s;
  Real outConc;
equation
  level_m = m/(rho*area);
  w_NaCl = if m > 1e-6 then max(0, min(0.3, mSalt/m)) else 0;
  temp_K = T;
  heaterPermissive = heaterOn and level_m >= 0.05 and condenserFlow_kg_s >= 0.10;
  evap_kg_s = if heaterPermissive and w_NaCl < 0.18 then heaterDuty*evapGain else 0;
  outConc = if level_m <= 0.01 and concOutCmd_kg_s > 0 then 0 else concOutCmd_kg_s;
  condensate_kg_s = evap_kg_s;
  condensate_T_K = T;
  concentrateOut_kg_s = outConc;
  der(m) = inlet_kg_s - evap_kg_s - outConc;
  der(mSalt) = inlet_kg_s*inlet_w - outConc*w_NaCl;
  der(T) = if m > 1e-3 then ((if heaterPermissive then heaterDuty else 0) - evap_kg_s*2.2e6 + inlet_kg_s*cp*(inlet_T_K - T))/(m*cp) else 0;
  annotation(
    Icon(graphics={Rectangle(extent={{-70,-100},{70,50}}, lineColor={255,0,0}, fillColor={255,230,230}, fillPattern=FillPattern.Solid),Ellipse(extent={{-40,50},{40,90}}, lineColor={0,0,255}),Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-94,74},{94,90}}, textString="Combined B5/K1")})
  );
end EvaporatorCondenser;
