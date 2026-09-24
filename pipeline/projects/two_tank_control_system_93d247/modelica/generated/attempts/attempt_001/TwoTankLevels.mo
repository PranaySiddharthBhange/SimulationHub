model TwoTankLevels
  parameter Modelica.Units.SI.Area A1 = 1.2;
  parameter Modelica.Units.SI.Area A2 = 1.4;
  parameter Modelica.Units.SI.Height tankHeight1 = 1.0;
  parameter Modelica.Units.SI.Height tankHeight2 = 1.0;
  parameter Modelica.Units.SI.VolumeFlowRate qFill = 0.006;
  parameter Modelica.Units.SI.VolumeFlowRate qTransfer = 0.0045;
  parameter Modelica.Units.SI.VolumeFlowRate qDrain = 0.0050;
  parameter Modelica.Units.SI.Height level1_start = 0.05;
  parameter Modelica.Units.SI.Height level2_start = 0.05;

  Modelica.Blocks.Interfaces.BooleanInput valve1Cmd annotation (Placement(transformation(extent={{-120,60},{-100,80}}), iconTransformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.BooleanInput valve2Cmd annotation (Placement(transformation(extent={{-120,0},{-100,20}}), iconTransformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.BooleanInput valve3Cmd annotation (Placement(transformation(extent={{-120,-60},{-100,-40}}), iconTransformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealOutput tank1_level_m annotation (Placement(transformation(extent={{100,40},{120,60}}), iconTransformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput tank2_level_m annotation (Placement(transformation(extent={{100,-40},{120,-20}}), iconTransformation(extent={{100,-40},{120,-20}})));

protected 
  Modelica.Units.SI.Height level1(start=level1_start, fixed=true);
  Modelica.Units.SI.Height level2(start=level2_start, fixed=true);
  Modelica.Units.SI.VolumeFlowRate inflow1;
  Modelica.Units.SI.VolumeFlowRate outflow1;
  Modelica.Units.SI.VolumeFlowRate inflow2;
  Modelica.Units.SI.VolumeFlowRate outflow2;

equation 
  inflow1 = if valve1Cmd and level1 < tankHeight1 then qFill else 0;
  outflow1 = if valve2Cmd and level1 > 0 then qTransfer else 0;
  inflow2 = if valve2Cmd and level2 < tankHeight2 and level1 > 0 then qTransfer else 0;
  outflow2 = if valve3Cmd and level2 > 0 then qDrain else 0;

  der(level1) = (inflow1 - outflow1)/A1;
  der(level2) = (inflow2 - outflow2)/A2;

  tank1_level_m = level1;
  tank2_level_m = level2;

  annotation (Icon(graphics={Rectangle(extent={{-100,60},{-20,-60}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Rectangle(extent={{20,60},{100,-60}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),Rectangle(extent={{-96,-60},{-24,-20}}, lineColor={0,0,255}, fillColor={85,170,255}, fillPattern=FillPattern.Solid),Rectangle(extent={{24,-60},{96,-30}}, lineColor={0,0,255}, fillColor={85,170,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-92,68},{-28,90}}, textString="TK-101"),Text(extent={{28,68},{92,90}}, textString="TK-102")}), Diagram(graphics={Rectangle(extent={{-100,60},{-20,-60}}, lineColor={0,0,255}),Rectangle(extent={{20,60},{100,-60}}, lineColor={0,0,255})}));
end TwoTankLevels;
