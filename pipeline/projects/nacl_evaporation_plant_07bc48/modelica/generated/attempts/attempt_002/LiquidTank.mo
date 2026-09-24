model LiquidTank
  parameter Modelica.Units.SI.Area area = 0.05;
  parameter Modelica.Units.SI.Height level_start = 0.01;
  parameter Real w_start = 0;
  parameter Modelica.Units.SI.Temperature T_start = 293.15;
  parameter Modelica.Units.SI.Height levelMin = 0.01;

  Modelica.Blocks.Interfaces.RealInput inflow_kg_s annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput inflow_w annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput inflow_T_K annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput outflow_cmd_kg_s annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput heat_W annotation(Placement(transformation(extent={{0,100},{20,120}})));

  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.RealOutput w_NaCl annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput temp_K annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput actualOut_kg_s annotation(Placement(transformation(extent={{100,-60},{120,-40}})));

  parameter Real rho = 1000 "Assumption: incompressible baseline density";
  parameter Real cp = 4180 "Assumption: incompressible baseline heat capacity";
  Modelica.Units.SI.Mass m(start=area*level_start*rho, fixed=true);
  Modelica.Units.SI.Mass mSalt(start=area*level_start*rho*w_start, fixed=true);
  Modelica.Units.SI.Temperature T(start=T_start, fixed=true);
  Modelica.Units.SI.MassFlowRate outflow_kg_s;
equation
  level_m = m/(rho*area);
  w_NaCl = if m > 1e-9 then mSalt/m else 0;
  temp_K = T;
  outflow_kg_s = if level_m <= levelMin and outflow_cmd_kg_s > 0 then 0 else outflow_cmd_kg_s;
  actualOut_kg_s = outflow_kg_s;
  der(m) = inflow_kg_s - outflow_kg_s;
  der(mSalt) = inflow_kg_s*inflow_w - outflow_kg_s*w_NaCl;
  der(T) = if m > 1e-6 then (inflow_kg_s*cp*(inflow_T_K - T) + heat_W)/(m*cp) else 0;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-70,-100},{70,60}}, lineColor={0,0,255}, fillColor={235,235,255}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{-60,-100},{60,-20}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name")
    })
  );
end LiquidTank;
