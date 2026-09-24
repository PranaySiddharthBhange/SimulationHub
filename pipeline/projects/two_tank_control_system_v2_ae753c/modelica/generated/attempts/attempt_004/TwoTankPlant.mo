model TwoTankPlant
  parameter Modelica.Units.SI.Area A1 = 1.2;
  parameter Modelica.Units.SI.Area A2 = 1.4;
  parameter Modelica.Units.SI.Height tankHeight = 1.0;
  parameter Modelica.Units.SI.Height tank1LevelStart = 0.05;
  parameter Modelica.Units.SI.Height tank2LevelStart = 0.05;
  parameter Modelica.Units.SI.Height tank1Low = 0.05;
  parameter Modelica.Units.SI.Height tank2Low = 0.05;
  parameter Modelica.Units.SI.Height levelFloor = 0.0;
  parameter Modelica.Units.SI.Height levelCeiling = 1.0;
  parameter Modelica.Units.SI.VolumeFlowRate qFill = 0.0060;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer = 0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain = 0.0050;

  Modelica.Blocks.Interfaces.BooleanInput valve1_open_cmd annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.BooleanInput valve2_open_cmd annotation(Placement(transformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.BooleanInput valve3_open_cmd annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealOutput tank1_level_m annotation(Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput tank2_level_m annotation(Placement(transformation(extent={{100,-20},{120,0}})));

protected 
  Modelica.Units.SI.Height tank1_level(start=tank1LevelStart, fixed=true, nominal=1.0);
  Modelica.Units.SI.Height tank2_level(start=tank2LevelStart, fixed=true, nominal=1.0);
  Modelica.Units.SI.VolumeFlowRate q1In;
  Modelica.Units.SI.VolumeFlowRate q1Out;
  Modelica.Units.SI.VolumeFlowRate q2In;
  Modelica.Units.SI.VolumeFlowRate q2Out;
equation 
  q1In = if valve1_open_cmd and tank1_level < levelCeiling then qFill else 0;
  q1Out = if valve2_open_cmd and tank1_level > levelFloor then qTransfer else 0;
  q2In = if valve2_open_cmd and tank1_level > levelFloor and tank2_level < levelCeiling then qTransfer else 0;
  q2Out = if valve3_open_cmd and tank2_level > levelFloor then qDrain else 0;

  der(tank1_level) = q1In/A1 - q1Out/A1;
  der(tank2_level) = q2In/A2 - q2Out/A2;

  tank1_level_m = tank1_level;
  tank2_level_m = tank2_level;

  assert(tank1_level >= -1e-6 and tank1_level <= tankHeight + 1e-6, "TK-101 level out of range");
  assert(tank2_level >= -1e-6 and tank2_level <= tankHeight + 1e-6, "TK-102 level out of range");
end TwoTankPlant;
