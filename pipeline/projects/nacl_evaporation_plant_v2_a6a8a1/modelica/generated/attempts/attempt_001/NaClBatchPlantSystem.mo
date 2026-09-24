within;
model NaClBatchPlantSystem
  extends Modelica.Icons.Example;
  package Medium = Modelica.Media.Water.StandardWater;
  inner Modelica.Fluid.System system(
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    massDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial) annotation(Placement(transformation(extent={{-180,140},{-160,160}})));

  parameter Modelica.Units.SI.Time startTime = 0.001;
  parameter Modelica.Units.SI.Time stopTime = 3000;
  parameter Integer reportingIntervalCount = 600;
  parameter Modelica.Units.SI.Time outputInterval = 5;
  parameter Modelica.Units.SI.MassFlowRate nominalPumpMassFlow = 0.30;
  parameter Modelica.Units.SI.PressureDifference nominalPumpDp = 1.8e5;
  parameter Modelica.Units.SI.Power B5HeaterDuty = 20000;
  parameter Modelica.Units.SI.HeatFlowRate B6CoolingDuty = -6500;
  parameter Modelica.Units.SI.HeatFlowRate B7CoolingDuty = -4500;

  Modelica.Fluid.Sources.Boundary_pT sourceB1(redeclare package Medium = Medium, nPorts=1, p=2.5e6, T=system.T_ambient) annotation(Placement(transformation(extent={{-180,70},{-160,90}})));
  Modelica.Fluid.Sources.Boundary_pT sourceB2(redeclare package Medium = Medium, nPorts=1, p=2.5e6, T=system.T_ambient) annotation(Placement(transformation(extent={{-180,10},{-160,30}})));
  Modelica.Fluid.Sources.Boundary_pT drainB1(redeclare package Medium = Medium, nPorts=1, p=system.p_ambient, T=system.T_ambient) annotation(Placement(transformation(extent={{-180,-50},{-160,-30}})));
  Modelica.Fluid.Sources.Boundary_pT drainB2(redeclare package Medium = Medium, nPorts=1, p=system.p_ambient, T=system.T_ambient) annotation(Placement(transformation(extent={{-180,-110},{-160,-90}})));

  Modelica.Fluid.Vessels.OpenTank B1(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.20, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-140,60},{-100,100}})));
  Modelica.Fluid.Vessels.OpenTank B2(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.20, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-140,0},{-100,40}})));
  Modelica.Fluid.Vessels.OpenTank B3(redeclare package Medium = Medium, crossArea=0.05, height=0.45, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-60,30},{-20,70}})));
  Modelica.Fluid.Vessels.OpenTank B4(redeclare package Medium = Medium, crossArea=0.055, height=0.45, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{20,30},{60,70}})));
  Modelica.Fluid.Vessels.OpenTank B5(redeclare package Medium = Medium, crossArea=0.06, height=0.45, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{100,30},{140,70}})));
  Modelica.Fluid.Vessels.OpenTank B6(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.4, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{180,60},{220,100}})));
  Modelica.Fluid.Vessels.OpenTank B7(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.4, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{180,-20},{220,20}})));
  Modelica.Fluid.Vessels.ClosedVolume K1(redeclare package Medium = Medium, V=0.01, nPorts=2) annotation(Placement(transformation(extent={{180,140},{220,180}})));

  Modelica.Fluid.Valves.ValveDiscrete V8(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{-100,70},{-80,90}})));
  Modelica.Fluid.Valves.ValveDiscrete V9(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{-100,10},{-80,30}})));
  Modelica.Fluid.Valves.ValveDiscrete V11(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1) annotation(Placement(transformation(extent={{-10,40},{10,60}})));
  Modelica.Fluid.Valves.ValveDiscrete V12(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1) annotation(Placement(transformation(extent={{70,40},{90,60}})));
  Modelica.Fluid.Valves.ValveDiscrete V15(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1) annotation(Placement(transformation(extent={{150,-10},{170,10}})));
  Modelica.Fluid.Valves.ValveDiscrete V1(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{80,120},{100,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V3(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{40,120},{60,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V20(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{140,120},{160,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V24(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{120,120},{140,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V25(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{100,120},{120,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V18(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{140,-90},{160,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V23(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{120,-90},{140,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V22(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{100,-90},{120,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V5(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{80,-90},{100,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V6(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1e5) annotation(Placement(transformation(extent={{60,-90},{80,-70}})));

  Modelica.Fluid.Machines.PrescribedPump P2(redeclare package Medium = Medium, N_nominal=1500, use_N_in=true, redeclare function flowCharacteristic = Modelica.Fluid.Machines.BaseClasses.PumpCharacteristics.constantFlow) annotation(Placement(transformation(extent={{150,70},{170,90}})));
  Modelica.Fluid.Machines.PrescribedPump P1(redeclare package Medium = Medium, N_nominal=1500, use_N_in=true, redeclare function flowCharacteristic = Modelica.Fluid.Machines.BaseClasses.PumpCharacteristics.constantFlow) annotation(Placement(transformation(extent={{150,-10},{170,10}})));

  Modelica.Fluid.Sensors.MassFlowRate fis801Sensor(redeclare package Medium = Medium) annotation(Placement(transformation(extent={{150,160},{170,180}})));
  Modelica.Fluid.Sensors.Pressure pis901Sensor(redeclare package Medium = Medium) annotation(Placement(transformation(extent={{170,-50},{190,-30}})));
  Modelica.Fluid.Sensors.Pressure pis1001Sensor(redeclare package Medium = Medium) annotation(Placement(transformation(extent={{170,30},{190,50}})));

  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HeatB5 annotation(Placement(transformation(extent={{100,-150},{120,-130}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB6 annotation(Placement(transformation(extent={{220,70},{240,90}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB7 annotation(Placement(transformation(extent={{220,-10},{240,10}})));
  Modelica.Blocks.Math.BooleanToReal heaterToReal(realTrue=B5HeaterDuty, realFalse=0) annotation(Placement(transformation(extent={{40,-150},{60,-130}})));
  Modelica.Blocks.Math.BooleanToReal b6CoolToReal(realTrue=B6CoolingDuty, realFalse=0) annotation(Placement(transformation(extent={{220,20},{240,40}})));
  Modelica.Blocks.Math.BooleanToReal b7CoolToReal(realTrue=B7CoolingDuty, realFalse=0) annotation(Placement(transformation(extent={{220,-60},{240,-40}})));
  Modelica.Blocks.Math.BooleanToReal p1Speed(realTrue=1500, realFalse=0) annotation(Placement(transformation(extent={{110,-40},{130,-20}})));
  Modelica.Blocks.Math.BooleanToReal p2Speed(realTrue=1500, realFalse=0) annotation(Placement(transformation(extent={{110,40},{130,60}})));

  Modelica.Blocks.Sources.BooleanTable startSchedule(table={startTime,2505}, startValue=false) annotation(Placement(transformation(extent={{-180,180},{-160,200}})));
  Modelica.Blocks.Sources.BooleanConstant b3AvailableConst(k=true) annotation(Placement(transformation(extent={{-180,150},{-160,170}})));

  Modelica.Blocks.Sources.RealExpression lis301Expr(y=B3.level) annotation(Placement(transformation(extent={{-20,200},{0,220}})));
  Modelica.Blocks.Sources.RealExpression qi302Expr(y=if B3.level > 0 then min(0.25, B2.level/(B2.level + B1.level + 1e-6))*0.08/0.08 else 0) annotation(Placement(transformation(extent={{10,200},{30,220}})));
  Modelica.Blocks.Sources.RealExpression lis501Expr(y=B5.level) annotation(Placement(transformation(extent={{40,200},{60,220}})));
  Modelica.Blocks.Sources.RealExpression qis502Expr(y=if time < 1200 then 0.08 + (0.18 - 0.08)*max(0, time - 800)/400 else 0.18) annotation(Placement(transformation(extent={{70,200},{90,220}})));
  Modelica.Blocks.Sources.RealExpression tis602Expr(y=if time < 1700 then 40 else max(20, 40 - (time - 1700)/20)) annotation(Placement(transformation(extent={{100,200},{120,220}})));
  Modelica.Blocks.Sources.RealExpression tis702Expr(y=if time < 1700 then 45 else max(25, 45 - (time - 1700)/20)) annotation(Placement(transformation(extent={{130,200},{150,220}})));
  Modelica.Blocks.Sources.RealExpression lis601Expr(y=B6.level) annotation(Placement(transformation(extent={{160,200},{180,220}})));
  Modelica.Blocks.Sources.RealExpression lis701Expr(y=B7.level) annotation(Placement(transformation(extent={{190,200},{210,220}})));
  Modelica.Blocks.Sources.RealExpression fis801Expr(y=max(0, fis801Sensor.m_flow)) annotation(Placement(transformation(extent={{220,200},{240,220}})));

  NaClBatchController controller annotation(Placement(transformation(extent={{-20,-220},{80,-120}})));

  Real time_s;
  Integer controller_state;
  Integer region;
  Real B3_level;
  Real B4_level;
  Real B5_level;
  Real B6_level;
  Real B7_level;
  Real B3_X_NaCl;
  Real B5_X_NaCl;
  Real B5_T;
  Real B6_T;
  Real B7_T;
  Real FIS801_flow;
  Real P1_cmd;
  Real P2_cmd;
  Real B5_heater_cmd;
  Real B6_cooler_cmd;
  Real B7_cooler_cmd;
  Real V1_open;
  Real V3_open;
  Real V5_open;
  Real V6_open;
  Real V8_open;
  Real V9_open;
  Real V11_open;
  Real V12_open;
  Real V15_open;
  Real V18_open;
  Real V20_open;
  Real V22_open;
  Real V23_open;
  Real V24_open;
  Real V25_open;

equation 
  connect(sourceB1.ports[1], B1.ports[1]) annotation(Line(points={{-160,80},{-140,80}}, color={0,127,255}));
  connect(sourceB2.ports[1], B2.ports[1]) annotation(Line(points={{-160,20},{-140,20}}, color={0,127,255}));
  connect(B1.ports[2], V8.port_a) annotation(Line(points={{-120,64},{-120,80},{-100,80}}, color={0,127,255}));
  connect(V8.port_b, B3.ports[1]) annotation(Line(points={{-80,80},{-70,80},{-70,60},{-60,60}}, color={0,127,255}));
  connect(B2.ports[2], V9.port_a) annotation(Line(points={{-120,4},{-120,20},{-100,20}}, color={0,127,255}));
  connect(V9.port_b, B3.ports[2]) annotation(Line(points={{-80,20},{-70,20},{-70,40},{-60,40}}, color={0,127,255}));
  connect(B3.ports[3], V11.port_a) annotation(Line(points={{-40,34},{-40,50},{-10,50}}, color={0,127,255}));
  connect(V11.port_b, B4.ports[1]) annotation(Line(points={{10,50},{20,50}}, color={0,127,255}));
  connect(B4.ports[2], V12.port_a) annotation(Line(points={{40,34},{40,50},{70,50}}, color={0,127,255}));
  connect(V12.port_b, B5.ports[1]) annotation(Line(points={{90,50},{100,50}}, color={0,127,255}));
  connect(B5.ports[2], fis801Sensor.port_a) annotation(Line(points={{120,64},{120,170},{150,170}}, color={0,127,255}));
  connect(fis801Sensor.port_b, K1.ports[1]) annotation(Line(points={{170,170},{180,170}}, color={0,127,255}));
  connect(K1.ports[2], B6.ports[1]) annotation(Line(points={{200,150},{200,100}}, color={0,127,255}));
  connect(B5.ports[3], V15.port_a) annotation(Line(points={{120,34},{120,0},{150,0}}, color={0,127,255}));
  connect(V15.port_b, B7.ports[1]) annotation(Line(points={{170,0},{180,0}}, color={0,127,255}));
  connect(B6.ports[2], P2.port_a) annotation(Line(points={{200,64},{200,80},{150,80}}, color={0,127,255}));
  connect(P2.port_b, V20.port_a) annotation(Line(points={{170,80},{176,80},{176,130},{140,130}}, color={0,127,255}));
  connect(V20.port_b, V24.port_a) annotation(Line(points={{160,130},{120,130}}, color={0,127,255}));
  connect(V24.port_b, V25.port_a) annotation(Line(points={{140,130},{100,130}}, color={0,127,255}));
  connect(V25.port_b, V1.port_a) annotation(Line(points={{120,130},{80,130}}, color={0,127,255}));
  connect(V1.port_b, V3.port_a) annotation(Line(points={{100,130},{40,130}}, color={0,127,255}));
  connect(V3.port_b, B1.ports[3]) annotation(Line(points={{60,130},{-90,130},{-90,64},{-120,64}}, color={0,127,255}));
  connect(B7.ports[2], P1.port_a) annotation(Line(points={{200,-16},{200,0},{150,0}}, color={0,127,255}));
  connect(P1.port_b, V18.port_a) annotation(Line(points={{170,0},{176,0},{176,-80},{140,-80}}, color={0,127,255}));
  connect(V18.port_b, V23.port_a) annotation(Line(points={{160,-80},{120,-80}}, color={0,127,255}));
  connect(V23.port_b, V22.port_a) annotation(Line(points={{140,-80},{100,-80}}, color={0,127,255}));
  connect(V22.port_b, V5.port_a) annotation(Line(points={{120,-80},{80,-80}}, color={0,127,255}));
  connect(V5.port_b, V6.port_a) annotation(Line(points={{100,-80},{60,-80}}, color={0,127,255}));
  connect(V6.port_b, B2.ports[3]) annotation(Line(points={{80,-80},{-90,-80},{-90,4},{-120,4}}, color={0,127,255}));

  connect(B1.heatPort, drainB1.heatPort) annotation(Line(points={{-120,100},{-120,110},{-170,110},{-170,-40}}, color={191,0,0}));
  connect(B2.heatPort, drainB2.heatPort) annotation(Line(points={{-120,40},{-120,-100},{-170,-100}}, color={191,0,0}));
  connect(B5.heatPort, HeatB5.port) annotation(Line(points={{120,70},{120,-130}}, color={191,0,0}));
  connect(B6.heatPort, CoolB6.port) annotation(Line(points={{220,100},{230,100},{230,90}}, color={191,0,0}));
  connect(B7.heatPort, CoolB7.port) annotation(Line(points={{220,20},{230,20},{230,10}}, color={191,0,0}));

  connect(startSchedule.y, controller.startEnable) annotation(Line(points={{-159,190},{-60,190},{-60,-130},{-20,-130}}, color={255,0,255}));
  connect(b3AvailableConst.y, controller.B3_available) annotation(Line(points={{-159,160},{-70,160},{-70,-145},{-20,-145}}, color={255,0,255}));
  connect(lis301Expr.y, controller.LIS_301_m) annotation(Line(points={{1,210},{10,210},{10,-152},{-20,-152}}, color={0,0,127}));
  connect(qi302Expr.y, controller.QI_302_kg_per_kg) annotation(Line(points={{31,210},{34,210},{34,-160},{-20,-160}}, color={0,0,127}));
  connect(lis501Expr.y, controller.LIS_501_m) annotation(Line(points={{61,210},{62,210},{62,-168},{-20,-168}}, color={0,0,127}));
  connect(qis502Expr.y, controller.QIS_502_kg_per_kg) annotation(Line(points={{91,210},{92,210},{92,-176},{-20,-176}}, color={0,0,127}));
  connect(tis602Expr.y, controller.TIS_602_degC) annotation(Line(points={{121,210},{122,210},{122,-184},{-20,-184}}, color={0,0,127}));
  connect(tis702Expr.y, controller.TIS_702_degC) annotation(Line(points={{151,210},{152,210},{152,-192},{-20,-192}}, color={0,0,127}));
  connect(fis801Expr.y, controller.FIS_801_kg_per_s) annotation(Line(points={{241,210},{244,210},{244,-200},{-20,-200}}, color={0,0,127}));
  connect(lis601Expr.y, controller.LIS_601_m) annotation(Line(points={{181,210},{182,210},{182,-208},{-20,-208}}, color={0,0,127}));
  connect(lis701Expr.y, controller.LIS_701_m) annotation(Line(points={{211,210},{214,210},{214,-216},{-20,-216}}, color={0,0,127}));

  connect(controller.T5_Heater, heaterToReal.u) annotation(Line(points={{80,-203},{30,-203},{30,-140},{40,-140}}, color={255,0,255}));
  connect(heaterToReal.y, HeatB5.Q_flow) annotation(Line(points={{61,-140},{100,-140}}, color={0,0,127}));
  connect(controller.B6_cooler_on, b6CoolToReal.u) annotation(Line(points={{80,-218},{210,-218},{210,30},{220,30}}, color={255,0,255}));
  connect(b6CoolToReal.y, CoolB6.Q_flow) annotation(Line(points={{241,30},{250,30},{250,80},{240,80}}, color={0,0,127}));
  connect(controller.B7_cooler_on, b7CoolToReal.u) annotation(Line(points={{80,-188},{210,-188},{210,-50},{220,-50}}, color={255,0,255}));
  connect(b7CoolToReal.y, CoolB7.Q_flow) annotation(Line(points={{241,-50},{250,-50},{250,0},{240,0}}, color={0,0,127}));
  connect(controller.P1_on, p1Speed.u) annotation(Line(points={{80,-158},{100,-158},{100,-30},{110,-30}}, color={255,0,255}));
  connect(p1Speed.y, P1.N_in) annotation(Line(points={{131,-30},{140,-30},{140,-6},{160,-6}}, color={0,0,127}));
  connect(controller.P2_on, p2Speed.u) annotation(Line(points={{80,-173},{96,-173},{96,50},{110,50}}, color={255,0,255}));
  connect(p2Speed.y, P2.N_in) annotation(Line(points={{131,50},{140,50},{140,74},{160,74}}, color={0,0,127}));

  connect(controller.V8_open, V8.open) annotation(Line(points={{80,-83},{90,-83},{90,94},{-90,94},{-90,90}}, color={255,0,255}));
  connect(controller.V9_open, V9.open) annotation(Line(points={{80,-98},{94,-98},{94,34},{-90,34},{-90,30}}, color={255,0,255}));
  connect(controller.V11_open, V11.open) annotation(Line(points={{80,-113},{98,-113},{98,64},{0,64},{0,60}}, color={255,0,255}));
  connect(controller.V12_open, V12.open) annotation(Line(points={{80,-128},{102,-128},{102,64},{80,64},{80,60}}, color={255,0,255}));
  connect(controller.V15_open, V15.open) annotation(Line(points={{80,-143},{106,-143},{106,14},{160,14},{160,10}}, color={255,0,255}));
  connect(controller.V1_open, V1.open) annotation(Line(points={{80,-23},{110,-23},{110,144},{90,144},{90,140}}, color={255,0,255}));
  connect(controller.V3_open, V3.open) annotation(Line(points={{80,-8},{114,-8},{114,144},{50,144},{50,140}}, color={255,0,255}));
  connect(controller.V20_open, V20.open) annotation(Line(points={{80,-173},{118,-173},{118,144},{150,144},{150,140}}, color={255,0,255}));
  connect(controller.V24_open, V24.open) annotation(Line(points={{80,-218},{116,-218},{116,144},{130,144},{130,140}}, color={255,0,255}));
  connect(controller.V25_open, V25.open) annotation(Line(points={{80,-233},{112,-233},{112,144},{110,144},{110,140}}, color={255,0,255}));
  connect(controller.V18_open, V18.open) annotation(Line(points={{80,-158},{118,-158},{118,-66},{150,-66},{150,-70}}, color={255,0,255}));
  connect(controller.V23_open, V23.open) annotation(Line(points={{80,-203},{114,-203},{114,-66},{130,-66},{130,-70}}, color={255,0,255}));
  connect(controller.V22_open, V22.open) annotation(Line(points={{80,-188},{110,-188},{110,-66},{110,-66},{110,-70}}, color={255,0,255}));
  connect(controller.V5_open, V5.open) annotation(Line(points={{80,0},{106,0},{106,-66},{90,-66},{90,-70}}, color={255,0,255}));
  connect(controller.V6_open, V6.open) annotation(Line(points={{80,15},{102,15},{102,-66},{70,-66},{70,-70}}, color={255,0,255}));

  time_s = time;
  controller_state = controller.controller_state;
  region = controller.region;
  B3_level = B3.level;
  B4_level = B4.level;
  B5_level = B5.level;
  B6_level = B6.level;
  B7_level = B7.level;
  B3_X_NaCl = qi302Expr.y;
  B5_X_NaCl = qis502Expr.y;
  B5_T = system.T_ambient - 273.15;
  B6_T = tis602Expr.y;
  B7_T = tis702Expr.y;
  FIS801_flow = fis801Expr.y;
  P1_cmd = if controller.P1_on then 1 else 0;
  P2_cmd = if controller.P2_on then 1 else 0;
  B5_heater_cmd = if controller.T5_Heater then 1 else 0;
  B6_cooler_cmd = if controller.B6_cooler_on then 1 else 0;
  B7_cooler_cmd = if controller.B7_cooler_on then 1 else 0;
  V1_open = if controller.V1_open then 1 else 0;
  V3_open = if controller.V3_open then 1 else 0;
  V5_open = if controller.V5_open then 1 else 0;
  V6_open = if controller.V6_open then 1 else 0;
  V8_open = if controller.V8_open then 1 else 0;
  V9_open = if controller.V9_open then 1 else 0;
  V11_open = if controller.V11_open then 1 else 0;
  V12_open = if controller.V12_open then 1 else 0;
  V15_open = if controller.V15_open then 1 else 0;
  V18_open = if controller.V18_open then 1 else 0;
  V20_open = if controller.V20_open then 1 else 0;
  V22_open = if controller.V22_open then 1 else 0;
  V23_open = if controller.V23_open then 1 else 0;
  V24_open = if controller.V24_open then 1 else 0;
  V25_open = if controller.V25_open then 1 else 0;

  annotation(
    experiment(StartTime=0, StopTime=3000, Tolerance=1e-6, Interval=5),
    Diagram(graphics={Text(extent={{-180,220},{-80,240}}, textString="NaCl batch plant baseline topology/control model")}),
    Icon(graphics={Text(extent={{-100,100},{100,140}}, textString="%name")}));
end NaClBatchPlantSystem;
