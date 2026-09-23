model SingleTankTransferSystem
  extends Modelica.Icons.Example;

  OnOffFlowValve inletValve(nominalFlow=0.001) annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  OnOffFlowValve transferValve(nominalFlow=0.001) annotation(Placement(transformation(extent={{-20,50},{0,70}})));
  OnOffFlowValve drainValve(nominalFlow=0.001) annotation(Placement(transformation(extent={{80,50},{100,70}})));
  TankUnit tank1(level_start=0, capacity=1) annotation(Placement(transformation(extent={{-80,20},{-40,60}})));
  TankUnit tank2(level_start=0, capacity=1) annotation(Placement(transformation(extent={{20,20},{60,60}})));
  SingleTankTransferController controller annotation(Placement(transformation(extent={{-10,-100},{50,-20}})));

  Modelica.Blocks.Sources.BooleanTable startCmd(table={1,1.1,200,200.1}) annotation(Placement(transformation(extent={{-160,-20},{-140,0}})));
  Modelica.Blocks.Sources.BooleanTable stopCmd(table={80,80.1}) annotation(Placement(transformation(extent={{-160,-50},{-140,-30}})));
  Modelica.Blocks.Sources.BooleanTable shutCmd(table={500,500.1}) annotation(Placement(transformation(extent={{-160,-80},{-140,-60}})));
  Modelica.Blocks.Sources.BooleanExpression highLevelSwitch(y=tank1.level >= tank1.capacity) annotation(Placement(transformation(extent={{-160,90},{-140,110}})));
  Modelica.Blocks.Sources.BooleanExpression lowLevelSwitchTank1(y=tank1.level <= 0) annotation(Placement(transformation(extent={{-160,60},{-140,80}})));
  Modelica.Blocks.Sources.BooleanExpression lowLevelSwitchTank2(y=tank2.level <= 0) annotation(Placement(transformation(extent={{120,60},{140,80}})));
  Modelica.Blocks.Sources.RealExpression tank2Outflow(y=0) annotation(Placement(transformation(extent={{120,20},{140,40}})));

  Real tank1_level;
  Real tank2_level;
  Boolean inlet_valve_command;
  Boolean transfer_valve_command;
  Boolean drain_valve_command;
  Boolean inlet_inhibited;
equation
  connect(startCmd.y, controller.startButton) annotation(Line(points={{-139,-10},{-100,-10},{-100,-12},{-10,-12}}, color={255,0,255}));
  connect(stopCmd.y, controller.stopButton) annotation(Line(points={{-139,-40},{-90,-40},{-90,-28},{-10,-28}}, color={255,0,255}));
  connect(shutCmd.y, controller.shutButton) annotation(Line(points={{-139,-70},{-80,-70},{-80,-44},{-10,-44}}, color={255,0,255}));
  connect(highLevelSwitch.y, controller.highLevelReached) annotation(Line(points={{-139,100},{-110,100},{-110,-52},{-10,-52}}, color={255,0,255}));
  connect(lowLevelSwitchTank1.y, controller.lowLevelReachedTank1) annotation(Line(points={{-139,70},{-120,70},{-120,-68},{-10,-68}}, color={255,0,255}));
  connect(lowLevelSwitchTank2.y, controller.lowLevelReachedTank2) annotation(Line(points={{141,70},{150,70},{150,-84},{-10,-84}}, color={255,0,255}));

  connect(controller.inletOpen, inletValve.openCmd) annotation(Line(points={{50,8},{60,8},{60,60},{-120,60}}, color={255,0,255}));
  connect(controller.transferOpen, transferValve.openCmd) annotation(Line(points={{50,-4},{56,-4},{56,60},{-20,60}}, color={255,0,255}));
  connect(controller.drainOpen, drainValve.openCmd) annotation(Line(points={{50,-16},{66,-16},{66,60},{80,60}}, color={255,0,255}));

  connect(inletValve.volumeFlow, tank1.inflow) annotation(Line(points={{-99,60},{-90,60},{-90,50},{-80,50}}, color={0,0,127}));
  connect(transferValve.volumeFlow, tank1.outflowDemand) annotation(Line(points={{1,60},{10,60},{10,30},{-80,30}}, color={0,0,127}));
  connect(transferValve.volumeFlow, tank2.inflow) annotation(Line(points={{1,60},{10,60},{10,50},{20,50}}, color={0,0,127}));
  connect(drainValve.volumeFlow, tank2.outflowDemand) annotation(Line(points={{101,60},{110,60},{110,30},{20,30}}, color={0,0,127}));
  connect(tank2Outflow.y, tank2.outflowDemand) annotation(Line(points={{141,30},{146,30},{146,10},{10,10},{10,30},{20,30}}, color={0,0,127}));

  tank1_level = tank1.level;
  tank2_level = tank2.level;
  inlet_valve_command = controller.inletOpen;
  transfer_valve_command = controller.transferOpen;
  drain_valve_command = controller.drainOpen;
  inlet_inhibited = controller.inletInhibited;
  annotation(experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1), Diagram(coordinateSystem(extent={{-180,-120},{180,120}})));
end SingleTankTransferSystem;
