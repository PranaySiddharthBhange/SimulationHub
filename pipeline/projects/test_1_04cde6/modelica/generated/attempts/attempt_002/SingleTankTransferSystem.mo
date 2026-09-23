model SingleTankTransferSystem
  extends Modelica.Icons.Example;
  parameter Modelica.Units.SI.Area tankArea = 1 "Assumed tank cross-sectional area for both tanks";
  parameter Modelica.Units.SI.Height tankHighLevel = 1 "Assumed high switch threshold";
  parameter Modelica.Units.SI.Height tankLowLevel = 0.1 "Assumed low switch threshold";
  parameter Modelica.Units.SI.Height tank1Level_start = 0 "Assumed initial Tank 1 level";
  parameter Modelica.Units.SI.Height tank2Level_start = 0 "Assumed initial Tank 2 level";
  parameter Modelica.Units.SI.VolumeFlowRate inletNominalFlow = 0.02 "Assumed inlet fill flow";
  parameter Modelica.Units.SI.VolumeFlowRate transferNominalFlow = 0.02 "Assumed transfer flow";
  parameter Modelica.Units.SI.VolumeFlowRate drainNominalFlow = 0.02 "Assumed drain flow";
  parameter Modelica.Units.SI.Time pulseWidth = 1 "Assumed operator command pulse width";

  Modelica.Blocks.Sources.BooleanTable START_cmd(table={10,10 + pulseWidth,200,200 + pulseWidth}) annotation(Placement(transformation(extent={{-180,100},{-160,120}})));
  Modelica.Blocks.Sources.BooleanTable STOP_cmd(table={80,80 + pulseWidth}) annotation(Placement(transformation(extent={{-180,60},{-160,80}})));
  Modelica.Blocks.Sources.BooleanTable SHUT_cmd(table={500,500 + pulseWidth}) annotation(Placement(transformation(extent={{-180,20},{-160,40}})));

  TransferController controller annotation(Placement(transformation(extent={{-30,20},{30,100}})));
  ValveFlowCommand inletValve(nominalFlow=inletNominalFlow) annotation(Placement(transformation(extent={{-130,20},{-90,60}})));
  ValveFlowCommand transferValve(nominalFlow=transferNominalFlow) annotation(Placement(transformation(extent={{-10,-10},{30,30}})));
  ValveFlowCommand drainValve(nominalFlow=drainNominalFlow) annotation(Placement(transformation(extent={{110,-80},{150,-40}})));
  TankLevelUnit tank1(crossArea=tankArea, levelHigh=tankHighLevel, levelLow=tankLowLevel, level_start=tank1Level_start) annotation(Placement(transformation(extent={{-70,-100},{-30,-20}})));
  TankLevelUnit tank2(crossArea=tankArea, levelHigh=tankHighLevel, levelLow=tankLowLevel, level_start=tank2Level_start) annotation(Placement(transformation(extent={{50,-100},{90,-20}})));

  Real tank1_level;
  Real tank2_level;
  Boolean inlet_valve_command;
  Boolean transfer_valve_command;
  Boolean drain_valve_command;
  Boolean inlet_inhibited;
  Integer sequence_state;
equation
  tank1_level = tank1.level;
  tank2_level = tank2.level;
  inlet_valve_command = controller.inletOpen;
  transfer_valve_command = controller.transferOpen;
  drain_valve_command = controller.drainOpen;
  inlet_inhibited = controller.inletInhibited;
  sequence_state = controller.sequenceState;

  connect(START_cmd.y, controller.startButton) annotation(Line(points={{-159,110},{-110,110},{-110,84},{-30,84}}, color={255,0,255}));
  connect(STOP_cmd.y, controller.stopButton) annotation(Line(points={{-159,70},{-120,70},{-120,34},{-30,34}}, color={255,0,255}));
  connect(SHUT_cmd.y, controller.shutButton) annotation(Line(points={{-159,30},{-130,30},{-130,-16},{-30,-16}}, color={255,0,255}));

  connect(controller.inletOpen, inletValve.openCmd) annotation(Line(points={{30,70},{40,70},{40,40},{-130,40}}, color={255,0,255}));
  connect(controller.transferOpen, transferValve.openCmd) annotation(Line(points={{30,20},{40,20},{40,10},{-10,10}}, color={255,0,255}));
  connect(controller.drainOpen, drainValve.openCmd) annotation(Line(points={{30,-30},{60,-30},{60,-60},{110,-60}}, color={255,0,255}));

  connect(inletValve.qCmd, tank1.qIn) annotation(Line(points={{-89,40},{-80,40},{-80,-10},{-84,-10},{-84,-52},{-70,-52}}, color={0,0,127}));
  connect(transferValve.qCmd, tank1.qOutCmd) annotation(Line(points={{31,10},{40,10},{40,-120},{-90,-120},{-90,-68},{-70,-68}}, color={0,0,127}));
  connect(transferValve.qCmd, tank2.qIn) annotation(Line(points={{31,10},{40,10},{40,-6},{20,-6},{20,-52},{50,-52}}, color={0,0,127}));
  connect(drainValve.qCmd, tank2.qOutCmd) annotation(Line(points={{151,-60},{160,-60},{160,-120},{20,-120},{20,-68},{50,-68}}, color={0,0,127}));

  connect(tank1.highReached, controller.highLevelTank1) annotation(Line(points={{-30,-48},{-20,-48},{-20,-68},{-30,-68}}, color={255,0,255}));
  connect(tank1.lowReached, controller.lowLevelSharedTank1) annotation(Line(points={{-30,-10},{-12,-10},{-12,-100},{-30,-100}}, color={255,0,255}));
  connect(tank2.lowReached, controller.lowLevelSharedTank2) annotation(Line(points={{90,-10},{100,-10},{100,-130},{-30,-130}}, color={255,0,255}));
annotation(
  experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1),
  Diagram(graphics={Text(extent={{-188,136},{170,152}}, textString="Single-tank transfer sequence with assumed signal-flow valve routing")})
);
end SingleTankTransferSystem;
