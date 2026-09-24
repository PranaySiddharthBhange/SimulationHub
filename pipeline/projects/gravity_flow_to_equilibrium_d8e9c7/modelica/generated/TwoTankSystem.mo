model TwoTankSystem
  extends Modelica.Icons.Example;

  OpenTankLevel tankA(crossArea=0.5, height=1.0, level_start=0.80) annotation(Placement(transformation(extent={{-20,40},{20,80}})));
  OpenTankLevel tankB(crossArea=0.5, height=1.0, level_start=0.00) annotation(Placement(transformation(extent={{-20,-80},{20,-40}})));
  ConnectingValveFlow connectingFlow(k=0.025) annotation(Placement(transformation(extent={{60,-10},{100,30}})));
  ValveCommand valveCommand(openTime=5.0) annotation(Placement(transformation(extent={{-80,-10},{-40,30}})));
  Modelica.Blocks.Sources.RealExpression zeroFlow(y=0) annotation(Placement(transformation(extent={{-80,60},{-40,80}})));

  Real level_A_m;
  Real level_B_m;
  Real valve_open_cmd;
  Real q_m3s;
equation
  connect(zeroFlow.y, tankA.qIn_m3s) annotation(Line(points={{-39,70},{-30,70},{-30,66},{-20,66}}, color={0,0,127}));
  connect(zeroFlow.y, tankB.qOut_m3s) annotation(Line(points={{-39,70},{-30,70},{-30,-66},{-20,-66}}, color={0,0,127}));
  connect(connectingFlow.q_m3s, tankA.qOut_m3s) annotation(Line(points={{101,10},{110,10},{110,20},{-30,20},{-30,54},{-20,54}}, color={0,0,127}));
  connect(connectingFlow.q_m3s, tankB.qIn_m3s) annotation(Line(points={{101,10},{110,10},{110,-20},{-30,-20},{-30,-54},{-20,-54}}, color={0,0,127}));
  connect(tankA.level_m, connectingFlow.level_A_m) annotation(Line(points={{21,60},{40,60},{40,22},{60,22}}, color={0,0,127}));
  connect(tankB.level_m, connectingFlow.level_B_m) annotation(Line(points={{21,-60},{40,-60},{40,6},{60,6}}, color={0,0,127}));
  connect(valveCommand.openCmd, connectingFlow.openCmd) annotation(Line(points={{-39,10},{10,10},{10,-2},{60,-2}}, color={255,0,255}));

  level_A_m = tankA.level_m;
  level_B_m = tankB.level_m;
  q_m3s = connectingFlow.q_m3s;
  valve_open_cmd = if valveCommand.openCmd then 1 else 0;

  annotation(experiment(StartTime=0, StopTime=150, Tolerance=0.001, Interval=0.1),
    Diagram(graphics={Text(extent={{-100,90},{100,110}}, textString="Two tanks, upper drains to lower after 5 s") }));
end TwoTankSystem;