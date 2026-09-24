model SingleTankFillSystem
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.Area tank_cross_sectional_area_m2 = 0.5;
  parameter Modelica.Units.SI.Height tank_height_m = 1.0;
  parameter Modelica.Units.SI.Height initial_level_m = 0.0;
  parameter Modelica.Units.SI.Height fill_target_m = 0.8;
  parameter Modelica.Units.SI.VolumeFlowRate inlet_nominal_inflow_m3_s = 0.01;

  SingleSupply singleSupply
    annotation(Placement(transformation(extent={{-90,-10},{-50,30}})));
  ConstantInletValve inletValve(nominalInflow = inlet_nominal_inflow_m3_s)
    annotation(Placement(transformation(extent={{-20,-10},{20,30}})));
  TankLevel tank(
    crossArea = tank_cross_sectional_area_m2,
    tankHeight = tank_height_m,
    initialLevel = initial_level_m)
    annotation(Placement(transformation(extent={{40,-20},{80,20}})));

  Modelica.Blocks.Sources.BooleanExpression valveOpenLogic(y = tank_level_m < fill_target_m)
    annotation(Placement(transformation(extent={{-80,50},{-40,90}})));

  Real tank_level_m;
  Real valve_open_cmd;

equation
  connect(singleSupply.supplied_flow_m3_s, inletValve.supply_flow_m3_s) annotation(Line(points={{-49,10},{-20,10}}, color={0,0,127}));
  connect(valveOpenLogic.y, inletValve.openCmd) annotation(Line(points={{-38,70},{-30,70},{-30,18},{-20,18}}, color={255,0,255}));
  connect(inletValve.outflow_m3_s, tank.inflow_m3_s) annotation(Line(points={{21,0},{40,0}}, color={0,0,127}));

  tank_level_m = tank.tank_level_m;
  valve_open_cmd = inletValve.valve_open_cmd;

annotation(
  experiment(StartTime=0, StopTime=100, Tolerance=1e-6, Interval=0.1),
  Diagram(graphics={
    Text(extent={{-100,80},{100,100}}, textString="Single supply -> inlet valve -> tank")
  }));
end SingleTankFillSystem;
