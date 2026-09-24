model TwoTankSequenceSystem
  extends Modelica.Icons.Example;
  TwoTankPlant plant annotation(Placement(transformation(extent={{-10,-20},{50,40}})));
  PLC101 controller annotation(Placement(transformation(extent={{-10,70},{50,150}})));
  Modelica.Blocks.Sources.BooleanTable startSchedule(table={20,20.2,280,280.2}, startValue=false) annotation(Placement(transformation(extent={{-100,110},{-80,130}})));
  Modelica.Blocks.Sources.BooleanTable stopSchedule(table={220,220.2,650,650.2}, startValue=false) annotation(Placement(transformation(extent={{-100,70},{-80,90}})));
  Modelica.Blocks.Sources.BooleanTable shutSchedule(table={700,700.2}, startValue=false) annotation(Placement(transformation(extent={{-100,30},{-80,50}})));
  Modelica.Blocks.Math.BooleanToReal valve1CmdReal(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{70,110},{90,130}})));
  Modelica.Blocks.Math.BooleanToReal valve2CmdReal(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{70,80},{90,100}})));
  Modelica.Blocks.Math.BooleanToReal valve3CmdReal(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{70,50},{90,70}})));
  Modelica.Blocks.Math.BooleanToReal u1Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{70,20},{90,40}})));
  Modelica.Blocks.Math.BooleanToReal u2Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{70,-10},{90,10}})));
  Modelica.Blocks.Math.BooleanToReal u3Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{70,-40},{90,-20}})));
  Real time_s;
  Real tank1_level_m;
  Real tank2_level_m;
  Real valve1_open_cmd;
  Real valve2_open_cmd;
  Real valve3_open_cmd;
  Real controller_state_id;
  Real wait_remaining_s;
equation
  connect(startSchedule.y, controller.startButton) annotation(Line(points={{-79,120},{-40,120},{-40,108},{-10,108}}, color={255,0,255}));
  connect(stopSchedule.y, controller.stopButton) annotation(Line(points={{-79,80},{-36,80},{-36,92},{-10,92}}, color={255,0,255}));
  connect(shutSchedule.y, controller.shutButton) annotation(Line(points={{-79,40},{-32,40},{-32,76},{-10,76}}, color={255,0,255}));
  connect(controller.level1, plant.tank1_level_m) annotation(Line(points={{-10,130},{-30,130},{-30,60},{60,60},{60,30},{50,30}}, color={0,0,127}));
  connect(controller.level2, plant.tank2_level_m) annotation(Line(points={{-10,114},{-34,114},{-34,0},{60,0},{60,0},{50,0}}, color={0,0,127}));
  connect(controller.valve1, valve1CmdReal.u) annotation(Line(points={{50,136},{60,136},{60,120},{70,120}}, color={255,0,255}));
  connect(controller.valve2, valve2CmdReal.u) annotation(Line(points={{50,120},{60,120},{60,90},{70,90}}, color={255,0,255}));
  connect(controller.valve3, valve3CmdReal.u) annotation(Line(points={{50,104},{60,104},{60,60},{70,60}}, color={255,0,255}));
  connect(controller.valve1, u1Real.u) annotation(Line(points={{50,136},{56,136},{56,30},{70,30}}, color={255,0,255}));
  connect(controller.valve2, u2Real.u) annotation(Line(points={{50,120},{54,120},{54,0},{70,0}}, color={255,0,255}));
  connect(controller.valve3, u3Real.u) annotation(Line(points={{50,104},{52,104},{52,-30},{70,-30}}, color={255,0,255}));
  connect(u1Real.y, plant.u1) annotation(Line(points={{91,30},{96,30},{96,60},{-40,60},{-40,25},{-10,25}}, color={0,0,127}));
  connect(u2Real.y, plant.u2) annotation(Line(points={{91,0},{94,0},{94,10},{-30,10},{-30,0},{-10,0}}, color={0,0,127}));
  connect(u3Real.y, plant.u3) annotation(Line(points={{91,-30},{96,-30},{96,-50},{-40,-50},{-40,-15},{-10,-15}}, color={0,0,127}));
  time_s = time;
  tank1_level_m = plant.tank1_level_m;
  tank2_level_m = plant.tank2_level_m;
  valve1_open_cmd = valve1CmdReal.y;
  valve2_open_cmd = valve2CmdReal.y;
  valve3_open_cmd = valve3CmdReal.y;
  controller_state_id = controller.controller_state_id;
  wait_remaining_s = controller.wait_remaining_s;
annotation(
  experiment(StartTime=0, StopTime=900, Tolerance=1e-6, Interval=0.9),
  Diagram(graphics={Text(extent={{-112,144},{-76,136}}, textString="START"),Text(extent={{-112,104},{-76,96}}, textString="STOP"),Text(extent={{-112,64},{-76,56}}, textString="SHUT")}));
end TwoTankSequenceSystem;
