model TwoTankSystem
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.Area area_A = 0.5;
  parameter Modelica.Units.SI.Area area_B = 0.5;
  parameter Modelica.Units.SI.Height height_A = 1.0;
  parameter Modelica.Units.SI.Height height_B = 1.0;
  parameter Modelica.Units.SI.Height levelA_start = 0.80;
  parameter Modelica.Units.SI.Height levelB_start = 0.00;
  parameter Real k(unit="m2/s") = 0.025;
  parameter Modelica.Units.SI.Time valve_open_time_s = 5.0;

  ConnectingValve connectingValve(openTime_s = valve_open_time_s) annotation(Placement(transformation(extent={{-10,50},{30,90}})));

  Modelica.Units.SI.Height level_A_m(start=levelA_start, fixed=true, nominal=1.0);
  Modelica.Units.SI.Height level_B_m(start=levelB_start, fixed=true, nominal=1.0);
  Real q_m3s(unit="m3/s", nominal=0.02);
  Real valve_open_cmd;
protected 
  Boolean valveOpen;
equation
  valveOpen = time >= valve_open_time_s;
  valve_open_cmd = if valveOpen then 1 else 0;
  q_m3s = if valveOpen then max(0, k*(level_A_m - level_B_m)) else 0;
  der(level_A_m) = -q_m3s/area_A;
  der(level_B_m) = q_m3s/area_B;

  assert(level_A_m >= 0 and level_A_m <= height_A, "level_A_m out of bounds");
  assert(level_B_m >= 0 and level_B_m <= height_B, "level_B_m out of bounds");

annotation(
  Diagram(graphics={
    Rectangle(extent={{-100,20},{-60,-60}}, lineColor={0,0,255}),
    Rectangle(extent={{60,-20},{100,-100}}, lineColor={0,0,255}),
    Line(points={{-60,-20},{60,-60}}, color={0,127,255}),
    Text(extent={{-110,30},{-50,50}}, textString="Tank A"),
    Text(extent={{50,-10},{110,10}}, textString="Tank B")
  }),
  experiment(StartTime=0, StopTime=150, Tolerance=0.001, Interval=0.1)
);
end TwoTankSystem;