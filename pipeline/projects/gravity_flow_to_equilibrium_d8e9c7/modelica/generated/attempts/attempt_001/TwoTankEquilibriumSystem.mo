model TwoTankEquilibriumSystem
  extends Modelica.Icons.Example;

  UpperLowerTankPair tanks annotation(Placement(transformation(extent={{-20,-20},{20,20}})));
  ConnectingValveFlow connectingFlow(k=0.025) annotation(Placement(transformation(extent={{20,40},{60,80}})));
  ValveOpenSchedule valveSchedule(valveOpenTime_s=5.0) annotation(Placement(transformation(extent={{-80,40},{-40,80}})));
  Modelica.Blocks.Math.BooleanToReal valveCmdReal(realTrue=1.0, realFalse=0.0) annotation(Placement(transformation(extent={{-20,40},{0,60}})));

  Real level_A_m;
  Real level_B_m;
  Real valve_open_cmd;
  Real q_m3s;
equation
  connect(valveSchedule.valveOpen, connectingFlow.valveOpen) annotation(Line(points={{-39,60},{20,60}}, color={255,0,255}));
  connect(valveSchedule.valveOpen, valveCmdReal.u) annotation(Line(points={{-39,60},{-22,60},{-22,50},{-20,50}}, color={255,0,255}));
  connect(tanks.level_A_m, connectingFlow.level_A_m) annotation(Line(points={{21,10},{80,10},{80,60},{20,60}}, color={0,0,127}));
  connect(tanks.level_B_m, connectingFlow.level_B_m) annotation(Line(points={{21,-10},{90,-10},{90,40},{10,40},{10,40},{20,40}}, color={0,0,127}));
  connect(connectingFlow.q_m3s, tanks.q_m3s) annotation(Line(points={{61,60},{70,60},{70,0},{-30,0},{-30,0},{-20,0}}, color={0,0,127}));

  level_A_m = tanks.level_A_m;
  level_B_m = tanks.level_B_m;
  valve_open_cmd = valveCmdReal.y;
  q_m3s = connectingFlow.q_m3s;
annotation(
  experiment(StartTime=0, StopTime=150, Tolerance=0.001, Interval=0.1),
  Diagram(graphics={Text(extent={{-100,96},{100,114}}, textString="Two Tanks, One Above The Other — Gravity Flow To Equilibrium")})
);
end TwoTankEquilibriumSystem;
