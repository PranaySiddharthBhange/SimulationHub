model TwoTankSystem
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Modelica.Units.SI.Time cmdWidth = 2*scanPeriod;

  PLC101 PLC_101(scanPeriod=scanPeriod, T1_high=0.80, T1_low=0.05, T2_low=0.05, waitAfterFill=10, waitAfterTransfer=12, waitAfterDrain=8)
    annotation(Placement(transformation(extent={{20,20},{60,80}})));
  TwoTankPlant plant(A1=1.2, A2=1.4, tankHeight=1.0, tank1LevelStart=0.05, tank2LevelStart=0.05, tank1Low=0.05, tank2Low=0.05, qFill=0.0060, qTransfer=0.0045, qDrain=0.0050)
    annotation(Placement(transformation(extent={{-20,-20},{40,20}})));

  Modelica.Blocks.Sources.BooleanTable PB_START(table={20,20 + cmdWidth,280,280 + cmdWidth}, startValue=false)
    annotation(Placement(transformation(extent={{-100,60},{-80,80}})));
  Modelica.Blocks.Sources.BooleanTable PB_STOP(table={220,220 + cmdWidth,650,650 + cmdWidth}, startValue=false)
    annotation(Placement(transformation(extent={{-100,20},{-80,40}})));
  Modelica.Blocks.Sources.BooleanTable PB_SHUT(table={700,700 + cmdWidth}, startValue=false)
    annotation(Placement(transformation(extent={{-100,-20},{-80,0}})));
  Modelica.Blocks.Math.BooleanToReal startReal(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{-60,60},{-40,80}})));
  Modelica.Blocks.Math.BooleanToReal stopReal(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{-60,20},{-40,40}})));
  Modelica.Blocks.Math.BooleanToReal shutReal(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{-60,-20},{-40,0}})));
  Modelica.Blocks.Math.BooleanToReal valve1Real(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{80,60},{100,80}})));
  Modelica.Blocks.Math.BooleanToReal valve2Real(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{80,20},{100,40}})));
  Modelica.Blocks.Math.BooleanToReal valve3Real(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{80,-20},{100,0}})));

  Real time_s;
  Real tank1_level_m;
  Real tank2_level_m;
  Real valve1_open_cmd;
  Real valve2_open_cmd;
  Real valve3_open_cmd;
  Integer controller_state_code;
  Real wait_remaining_s;
  Real cmd_start;
  Real cmd_stop;
  Real cmd_shut;
equation 
  time_s = time;
  tank1_level_m = plant.tank1_level_m;
  tank2_level_m = plant.tank2_level_m;
  controller_state_code = PLC_101.controller_state_code;
  wait_remaining_s = PLC_101.wait_remaining_s;
  cmd_start = startReal.y;
  cmd_stop = stopReal.y;
  cmd_shut = shutReal.y;
  valve1_open_cmd = valve1Real.y;
  valve2_open_cmd = valve2Real.y;
  valve3_open_cmd = valve3Real.y;

  connect(PB_START.y, PLC_101.startButton) annotation(Line(points={{-79,70},{-20,70},{-20,-10},{20,-10}}, color={255,0,255}));
  connect(PB_STOP.y, PLC_101.stopButton) annotation(Line(points={{-79,30},{-10,30},{-10,-30},{20,-30}}, color={255,0,255}));
  connect(PB_SHUT.y, PLC_101.shutButton) annotation(Line(points={{-79,-10},{0,-10},{0,-50},{20,-50}}, color={255,0,255}));
  connect(PB_START.y, startReal.u) annotation(Line(points={{-79,70},{-70,70},{-70,70},{-62,70}}, color={255,0,255}));
  connect(PB_STOP.y, stopReal.u) annotation(Line(points={{-79,30},{-70,30},{-70,30},{-62,30}}, color={255,0,255}));
  connect(PB_SHUT.y, shutReal.u) annotation(Line(points={{-79,-10},{-70,-10},{-70,-10},{-62,-10}}, color={255,0,255}));

  connect(plant.tank1_level_m, PLC_101.level1) annotation(Line(points={{41,10},{70,10},{70,70},{20,70}}, color={0,0,127}));
  connect(plant.tank2_level_m, PLC_101.level2) annotation(Line(points={{41,-10},{68,-10},{68,30},{20,30}}, color={0,0,127}));

  connect(PLC_101.valve1_open_cmd, plant.valve1_open_cmd) annotation(Line(points={{61,70},{70,70},{70,10},{-20,10}}, color={255,0,255}));
  connect(PLC_101.valve2_open_cmd, plant.valve2_open_cmd) annotation(Line(points={{61,30},{72,30},{72,0},{-20,0}}, color={255,0,255}));
  connect(PLC_101.valve3_open_cmd, plant.valve3_open_cmd) annotation(Line(points={{61,-10},{74,-10},{74,-10},{-20,-10}}, color={255,0,255}));

  connect(PLC_101.valve1_open_cmd, valve1Real.u) annotation(Line(points={{61,70},{70,70},{70,70},{78,70}}, color={255,0,255}));
  connect(PLC_101.valve2_open_cmd, valve2Real.u) annotation(Line(points={{61,30},{70,30},{70,30},{78,30}}, color={255,0,255}));
  connect(PLC_101.valve3_open_cmd, valve3Real.u) annotation(Line(points={{61,-10},{70,-10},{70,-10},{78,-10}}, color={255,0,255}));

  annotation(experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.1));
end TwoTankSystem;
