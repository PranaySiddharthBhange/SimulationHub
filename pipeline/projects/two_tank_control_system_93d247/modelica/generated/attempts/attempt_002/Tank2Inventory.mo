model Tank2Inventory
  parameter Modelica.Units.SI.Area crossSectionArea=1.4;
  parameter Modelica.Units.SI.Height initialLevel=0.05;
  parameter Modelica.Units.SI.Height minLevel=0.0;
  parameter Modelica.Units.SI.Height maxLevel=1.0;
  Modelica.Blocks.Interfaces.RealInput inflow_m3s annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput outflowRequest_m3s annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.RealOutput outflowActual_m3s annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
protected
  Modelica.Units.SI.Height level(start=initialLevel, fixed=true);
equation
  outflowActual_m3s = if level <= minLevel and outflowRequest_m3s > inflow_m3s then inflow_m3s else if level >= maxLevel and inflow_m3s > outflowRequest_m3s then outflowRequest_m3s else outflowRequest_m3s;
  der(level) = (inflow_m3s - outflowActual_m3s)/crossSectionArea;
  level_m = level;
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-100},{60,80}}, lineColor={0,0,255}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),Rectangle(extent={{-58,-100},{58,-20}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-90,88},{90,104}}, textString="TK-102 inventory")})
  );
end Tank2Inventory;
