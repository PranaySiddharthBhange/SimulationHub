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

  TransferController controller annotation(Placement(transformation(extent={{-40,20},{20,100}})));
  ValveCommandSource inletValve(nominalFlow=inletNominalFlow) annotation(Placement(transformation(extent={{-120,20},{-80,60}})));
  ValveCommandSource transferValve(nominalFlow=transferNominalFlow) annotation(Placement(transformation(extent={{0,-20},{40,20}})));
  ValveCommandSource drainValve(nominalFlow=drainNominalFlow) annotation(Placement(transformation(extent={{100,-80},{140,-40}})));
  TransferTank tank1(crossArea=tankArea, levelHigh=tankHighLevel, levelLow=tankLowLevel, level_start=tank1Level_start) annotation(Placement(transformation(extent={{-60,-100},{-20,-20}})));
  TransferTank tank2(crossArea=tankArea, levelHigh=tankHighLevel, levelLow=tankLowLevel, level_start=tank2Level_start) annotation(Placement(transformation(extent={{40,-100},{80,-20}})));

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

  connect(START_cmd.y, controller.startButton) annotation(Line(points={{-159,110},{-100,110},{-100,84},{-40,84}}, color={255,0,255}));
  connect(STOP_cmd.y, controller.stopButton) annotation(Line(points={{-159,70},{-110,70},{-110,34},{-40,34}}, color={255,0,255}));
  connect(SHUT_cmd.y, controller.shutButton) annotation(Line(points={{-159,30},{-120,30},{-120,-16},{-40,-16}}, color={255,0,255}));

  connect(controller.inletOpen, inletValve.openCmd) annotation(Line(points={{20,70},{40,70},{40,40},{-120,40}}, color={255,0,255}));
  connect(controller.transferOpen, transferValve.openCmd) annotation(Line(points={{20,20},{50,20},{50,0},{0,0}}, color={255,0,255}));
  connect(controller.drainOpen, drainValve.openCmd) annotation(Line(points={{20,-30},{60,-30},{60,-60},{100,-60}}, color={255,0,255}));

  connect(inletValve.qCmd, tank1.qIn) annotation(Line(points={{-79,40},{-70,40},{-70,-4},{-90,-4},{-90,-52},{-60,-52}}, color={0,0,127}));
  connect(transferValve.qCmd, tank1.qOutCmd) annotation(Line(points={{41,0},{50,0},{50,-120},{-90,-120},{-90,-68},{-60,-68}}, color={0,0,127}));
  connect(tank1.qOutActual, tank2.qIn) annotation(Line(points={{-20,-76},{20,-76},{20,-52},{40,-52}}, color={0,0,127}));
  connect(drainValve.qCmd, tank2.qOutCmd) annotation(Line(points={{141,-60},{150,-60},{150,-120},{10,-120},{10,-68},{40,-68}}, color={0,0,127}));

  connect(tank1.highReached, controller.highLevelTank1) annotation(Line(points={{-20,-48},{-10,-48},{-10,-68},{-40,-68}}, color={255,0,255}));
  connect(tank1.lowReached, controller.lowLevelTank1) annotation(Line(points={{-20,-60},{0,-60},{0,-100},{-40,-100}}, color={255,0,255}));
  connect(tank2.lowReached, controller.lowLevelTank2) annotation(Line(points={{80,-60},{90,-60},{90,-130},{-40,-130}}, color={255,0,255}));
annotation(
  experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1),
  Diagram(graphics={Text(extent={{-188,136},{168,152}}, textString="Single-tank transfer sequence interpretation with assumed signal-flow routing")})
);
end SingleTankTransferSystem;
