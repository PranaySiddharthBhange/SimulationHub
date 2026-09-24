model EvaporatorCondenser
  parameter Modelica.Units.SI.Area area = 0.06;
  parameter Modelica.Units.SI.Height level_start = 0.01;
  parameter Real w_start = 0;
  parameter Modelica.Units.SI.Temperature T_start = 293.15;
  parameter Modelica.Units.SI.Power heaterDuty = 20000;
  parameter Real rho = 1000;
  parameter Real cp = 4180;
  parameter Real evapGain = 1.9e-5;

  Modelica.Blocks.Interfaces.RealInput inflow_kg_s annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput inflow_w annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput inflow_T_K annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.BooleanInput heaterOn annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput condenserFlow_kg_s annotation(Placement(transformation(extent={{-120,-100},{-100,-80}})));
  Modelica.Blocks.Interfaces.RealInput concentrateOutCmd_kg_s annotation(Placement(transformation(extent={{0,-120},{20,-100}})));

  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,35},{120,55}})));
  Modelica.Blocks.Interfaces.RealOutput temp_K annotation(Placement(transformation(extent={{100,0},{120,20}})));
  Modelica.Blocks.Interfaces.RealOutput condensate_kg_s annotation(Placement(transformation(extent={{100,-35},{120,-15}})));
  Modelica.Blocks.Interfaces.RealOutput condensate_T_K annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
  Modelica.Blocks.Interfaces.RealOutput concentrateOut_kg_s annotation(Placement(transformation(extent={{100,-105},{120,-85}})));

  Modelica.Units.SI.Mass m(start=area*level_start*rho, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=area*level_start*rho*w_start, fixed=true);
  Modelica.Units.SI.Temperature T(start=T_start, fixed=true);
  Boolean heaterPermissive;
  Modelica.Units.SI.MassFlowRate evap_kg_s;
  Modelica.Units.SI.MassFlowRate outflow_kg_s;
equation
  level_m = m/(rho*area);
  w_NaCl = if m > 1e-9 then mSalt/m else 0;
  temp_K = T;
  heaterPermissive = heaterOn and level_m >= 0.05 and condenserFlow_kg_s >= 0.10;
  evap_kg_s = if heaterPermissive and w_NaCl < 0.18 then heaterDuty*evapGain else 0;
  outflow_kg_s = if level_m <= 0.01 and concentrateOutCmd_kg_s > 0 then 0 else concentrateOutCmd_kg_s;
  condensate_kg_s = evap_kg_s;
  condensate_T_K = T;
  concentrateOut_kg_s = outflow_kg_s;
  der(m) = inflow_kg_s - evap_kg_s - outflow_kg_s;
  der(mSalt) = inflow_kg_s*inflow_w - outflow_kg_s*w_NaCl;
  der(T) = if m > 1e-6 then (inflow_kg_s*cp*(inflow_T_K - T) + (if heaterPermissive then heaterDuty else 0) - evap_kg_s*2.2e6)/(m*cp) else 0;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-70,-100},{70,50}}, lineColor={255,0,0}, fillColor={255,235,235}, fillPattern=FillPattern.Solid),
      Ellipse(extent={{-40,50},{40,90}}, lineColor={0,0,255}, fillColor={235,235,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name")
    })
  );
end EvaporatorCondenser;
