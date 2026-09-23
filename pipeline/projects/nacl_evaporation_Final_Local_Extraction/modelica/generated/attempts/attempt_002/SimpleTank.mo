model SimpleTank
  extends Modelica.Blocks.Icons.Block;
  parameter Real area_m2;
  parameter Real level_start_m;
  parameter Real levelMax_m;
  parameter Real wNaCl_start;
  parameter Real temperature_start_degC;
  Modelica.Blocks.Interfaces.RealInput inflow_m3_s annotation(Placement(transformation(extent={{-120,50},{-80,90}})));
  Modelica.Blocks.Interfaces.RealInput inflow_wNaCl annotation(Placement(transformation(extent={{-120,0},{-80,40}})));
  Modelica.Blocks.Interfaces.RealInput inflow_T_degC annotation(Placement(transformation(extent={{-120,-50},{-80,-10}})));
  Modelica.Blocks.Interfaces.RealInput outflow_m3_s annotation(Placement(transformation(extent={{-120,-100},{-80,-60}})));
  Modelica.Blocks.Interfaces.RealOutput level_m annotation(Placement(transformation(extent={{80,50},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput wNaCl annotation(Placement(transformation(extent={{80,0},{120,40}})));
  Modelica.Blocks.Interfaces.RealOutput temperature_degC annotation(Placement(transformation(extent={{80,-50},{120,-10}})));
protected 
  Real volume_m3(start=area_m2*level_start_m, fixed=true);
  Real soluteInventory(start=area_m2*level_start_m*wNaCl_start, fixed=true);
  Real thermalInventory_degC_m3(start=area_m2*level_start_m*temperature_start_degC, fixed=true);
  Real actualOutflow_m3_s;
equation
  actualOutflow_m3_s = if noEvent(volume_m3 <= 0 and outflow_m3_s > 0) then 0 else if noEvent(volume_m3 >= area_m2*levelMax_m and inflow_m3_s < actualOutflow_m3_s) then inflow_m3_s else outflow_m3_s;
  der(volume_m3) = if noEvent(volume_m3 >= area_m2*levelMax_m and inflow_m3_s > actualOutflow_m3_s) then 0 else inflow_m3_s - actualOutflow_m3_s;
  der(soluteInventory) = inflow_m3_s*inflow_wNaCl - actualOutflow_m3_s*wNaCl;
  der(thermalInventory_degC_m3) = inflow_m3_s*inflow_T_degC - actualOutflow_m3_s*temperature_degC;
  level_m = volume_m3/area_m2;
  wNaCl = if noEvent(volume_m3 > 1e-9) then soluteInventory/volume_m3 else wNaCl_start;
  temperature_degC = if noEvent(volume_m3 > 1e-9) then thermalInventory_degC_m3/volume_m3 else temperature_start_degC;
  annotation(Icon(graphics={Rectangle(extent={{-80,80},{80,-80}}),Line(points={{-80,-20},{80,-20}}),Text(extent={{-60,10},{60,-10}}, textString="Tank") }));
end SimpleTank;
