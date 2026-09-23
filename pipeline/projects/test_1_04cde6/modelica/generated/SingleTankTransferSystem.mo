model SingleTankTransferSystem
  extends Modelica.Icons.Example;
  parameter Modelica.Units.SI.Area tankArea = 1 "Assumed tank cross-sectional area for both tanks";
  parameter Modelica.Units.SI.Height tankHighLevel = 1 "Assumed Tank 1 high switch threshold";
  parameter Modelica.Units.SI.Height tankLowLevel = 0.1 "Assumed shared low switch threshold when sensing either tank";
  parameter Modelica.Units.SI.Height tank1Level_start = 0 "Assumed initial Tank 1 level";
  parameter Modelica.Units.SI.Height tank2Level_start = 0 "Assumed initial Tank 2 level";
  parameter Modelica.Units.SI.VolumeFlowRate inletNominalFlow = 0.02 "Assumed inlet fill flow";
  parameter Modelica.Units.SI.VolumeFlowRate transferNominalFlow = 0.02 "Assumed transfer flow";
  parameter Modelica.Units.SI.VolumeFlowRate drainNominalFlow = 0.02 "Assumed drain flow";

  Modelica.Blocks.Sources.BooleanTable START_cmd(table={10,11,200,201}) annotation(Placement(transformation(extent={{-180,100},{-160,120}})));
  Modelica.Blocks.Sources.BooleanTable STOP_cmd(table={80,81}) annotation(Placement(transformation(extent={{-180,60},{-160,80}})));
  Modelica.Blocks.Sources.BooleanTable SHUT_cmd(table={500,501}) annotation(Placement(transformation(extent={{-180,20},{-160,40}})));

  TransferController controller annotation(Placement(transformation(extent={{-10,20},{50,100}})));
  ValveFlowCommand inletValve(nominalFlow=inletNominalFlow) annotation(Placement(transformation(extent={{-130,20},{-90,60}})));
  ValveFlowCommand transferValve(nominalFlow=transferNominalFlow) annotation(Placement(transformation(extent={{-20,-10},{20,30}})));
  ValveFlowCommand drainValve(nominalFlow=drainNominalFlow) annotation(Placement(transformation(extent={{100,-80},{140,-40}})));
  Tank1Unit tank1(crossArea=tankArea, levelHigh=tankHighLevel, levelLow=tankLowLevel, level_start=tank1Level_start) annotation(Placement(transformation(extent={{-70,-100},{-30,-20}})));
  Tank2Unit tank2(crossArea=tankArea, levelLow=tankLowLevel, level_start=tank2Level_start) annotation(Placement(transformation(extent={{40,-100},{80,-20}})));

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

  connect(START_cmd.y, controller.startButton) annotation(Line(points={{-159,110},{-120,110},{-120,84},{-10,84}}, color={255,0,255}));
  connect(STOP_cmd.y, controller.stopButton) annotation(Line(points={{-159,70},{-120,70},{-120,44},{-10,44}}, color={255,0,255}));
  connect(SHUT_cmd.y, controller.shutButton) annotation(Line(points={{-159,30},{-120,30},{-120,4},{-10,4}}, color={255,0,255}));

  connect(controller.inletOpen, inletValve.openCmd) annotation(Line(points={{50,80},{60,80},{60,40},{-130,40}}, color={255,0,255}));
  connect(controller.transferOpen, transferValve.openCmd) annotation(Line(points={{50,40},{60,40},{60,10},{20,10}}, color={255,0,255}));
  connect(controller.drainOpen, drainValve.openCmd) annotation(Line(points={{50,0},{60,0},{60,-60},{100,-60}}, color={255,0,255}));

  connect(inletValve.qCmd, tank1.qIn) annotation(Line(points={{-89,40},{-80,40},{-80,-52},{-70,-52}}, color={0,0,127}));
  connect(transferValve.qCmd, tank1.qOutCmd) annotation(Line(points={{21,10},{30,10},{30,-120},{-90,-120},{-90,-68},{-70,-68}}, color={0,0,127}));
  connect(transferValve.qCmd, tank2.qIn) annotation(Line(points={{21,10},{30,10},{30,-52},{40,-52}}, color={0,0,127}));
  connect(drainValve.qCmd, tank2.qOutCmd) annotation(Line(points={{141,-60},{150,-60},{150,-120},{20,-120},{20,-68},{40,-68}}, color={0,0,127}));

  connect(tank1.highReached, controller.highLevelTank1) annotation(Line(points={{-30,20},{-20,20},{-20,-40},{-10,-40}}, color={255,0,255}));
  connect(tank1.lowReached, controller.lowLevelSharedTank1) annotation(Line(points={{-30,-30},{-18,-30},{-18,-80},{-10,-80}}, color={255,0,255}));
  connect(tank2.lowReached, controller.lowLevelSharedTank2) annotation(Line(points={{80,-10},{90,-10},{90,-120},{-10,-120}}, color={255,0,255}));
annotation(
  experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1),
  Diagram(graphics={Text(extent={{-188,136},{170,152}}, textString="Single-tank transfer sequence with separate tank sensor interfaces to match used signals only")})
);
end SingleTankTransferSystem;
