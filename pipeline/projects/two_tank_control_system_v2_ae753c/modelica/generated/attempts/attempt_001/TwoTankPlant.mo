model TwoTankPlant
  parameter Modelica.Units.SI.Area A1 = 1.2;
  parameter Modelica.Units.SI.Area A2 = 1.4;
  parameter Modelica.Units.SI.Height tankHeight = 1.0;
  parameter Modelica.Units.SI.Height level1_start = 0.05;
  parameter Modelica.Units.SI.Height level2_start = 0.05;
  parameter Modelica.Units.SI.Height levelMin = 0.0;
  parameter Modelica.Units.SI.Height levelMax = 1.0;
  parameter Modelica.Units.SI.VolumeFlowRate qFill = 0.0060;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer = 0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain = 0.0050;

  Modelica.Blocks.Interfaces.BooleanInput valve1_open_cmd annotation(Placement(transformation(extent={{-120,50},{-100,70}}), iconTransformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.BooleanInput valve2_open_cmd annotation(Placement(transformation(extent={{-120,-10},{-100,10}}), iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.BooleanInput valve3_open_cmd annotation(Placement(transformation(extent={{-120,-70},{-100,-50}}), iconTransformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealOutput tank1_level_m annotation(Placement(transformation(extent={{100,50},{120,70}}), iconTransformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput tank2_level_m annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));

protected 
  Modelica.Units.SI.VolumeFlowRate q1In;
  Modelica.Units.SI.VolumeFlowRate q1Out;
  Modelica.Units.SI.VolumeFlowRate q2In;
  Modelica.Units.SI.VolumeFlowRate q2Out;
initial equation
  tank1_level_m = level1_start;
  tank2_level_m = level2_start;
equation
  q1In = if valve1_open_cmd and tank1_level_m < levelMax then qFill else 0;
  q1Out = if valve2_open_cmd and tank1_level_m > levelMin then qTransfer else 0;
  q2In = if valve2_open_cmd and tank2_level_m < levelMax then qTransfer else 0;
  q2Out = if valve3_open_cmd and tank2_level_m > levelMin then qDrain else 0;

  der(tank1_level_m) = q1In/A1 - q1Out/A1;
  der(tank2_level_m) = q2In/A2 - q2Out/A2;

  assert(tank1_level_m >= 0 and tank1_level_m <= 1.0, "tank1_level_m out of range");
  assert(tank2_level_m >= 0 and tank2_level_m <= 1.0, "tank2_level_m out of range");
  annotation(
    Icon(graphics={
      Rectangle(extent={{-90,-70},{-10,70}}, lineColor={0,0,255}),
      Rectangle(extent={{10,-70},{90,70}}, lineColor={0,0,255}),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-82,-86},{-18,-74}}, textString="TK-101"),
      Text(extent={{18,-86},{82,-74}}, textString="TK-102")}),
    Diagram(graphics={
      Rectangle(extent={{-90,-70},{-10,70}}, lineColor={0,0,255}),
      Rectangle(extent={{10,-70},{90,70}}, lineColor={0,0,255})}));
end TwoTankPlant;
