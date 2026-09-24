within;
model NaClBatchPlantSystem
  extends Modelica.Icons.Example;
  package Medium = Modelica.Media.Water.StandardWater;
  inner Modelica.Fluid.System system(
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    massDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial) annotation(Placement(transformation(extent={{-190,170},{-170,190}})));

  parameter Modelica.Units.SI.Time startPulseTime = 0.001;
  parameter Modelica.Units.SI.Time restartPulseTime = 2505;
  parameter Modelica.Units.SI.Time stopTime = 3000;
  parameter Integer reportingIntervalCount = 600;
  parameter Modelica.Units.SI.Time outputInterval = 5;
  parameter Modelica.Units.SI.MassFlowRate nominalValveMassFlow = 0.30;
  parameter Modelica.Units.SI.Power B5HeaterDuty = 20000;
  parameter Modelica.Units.SI.HeatFlowRate B6CoolingDuty = -6500;
  parameter Modelica.Units.SI.HeatFlowRate B7CoolingDuty = -4500;

  Modelica.Fluid.Sources.Boundary_pT sourceB1(redeclare package Medium = Medium, nPorts=1, p=2.5e6, T=system.T_ambient) annotation(Placement(transformation(extent={{-190,90},{-170,110}})));
  Modelica.Fluid.Sources.Boundary_pT sourceB2(redeclare package Medium = Medium, nPorts=1, p=2.5e6, T=system.T_ambient) annotation(Placement(transformation(extent={{-190,20},{-170,40}})));

  Modelica.Fluid.Vessels.OpenTank B1(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.30, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-150,80},{-110,120}})));
  Modelica.Fluid.Vessels.OpenTank B2(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.30, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.12, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-150,10},{-110,50}})));
  Modelica.Fluid.Vessels.OpenTank B3(redeclare package Medium = Medium, crossArea=0.05, height=0.45, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-60,45},{-20,85}})));
  Modelica.Fluid.Vessels.OpenTank B4(redeclare package Medium = Medium, crossArea=0.055, height=0.45, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{30,45},{70,85}})));
  Modelica.Fluid.Vessels.OpenTank B5(redeclare package Medium = Medium, crossArea=0.06, height=0.45, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.45, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{120,45},{160,85}})));
  Modelica.Fluid.Vessels.ClosedVolume K1(redeclare package Medium = Medium, V=0.01, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0)}) annotation(Placement(transformation(extent={{210,120},{250,160}})));
  Modelica.Fluid.Vessels.OpenTank B6(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.4, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{210,45},{250,85}})));
  Modelica.Fluid.Vessels.OpenTank B7(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.4, zeta_out=0, zeta_in=1),
               Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.05, height=0.0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{210,-35},{250,5}})));

  Modelica.Fluid.Valves.ValveDiscrete V8(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{-100,92},{-80,112}})));
  Modelica.Fluid.Valves.ValveDiscrete V9(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{-100,22},{-80,42}})));
  Modelica.Fluid.Valves.ValveDiscrete V11(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1) annotation(Placement(transformation(extent={{0,55},{20,75}})));
  Modelica.Fluid.Valves.ValveDiscrete V12(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1) annotation(Placement(transformation(extent={{90,55},{110,75}})));
  Modelica.Fluid.Valves.ValveDiscrete V15(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1) annotation(Placement(transformation(extent={{180,-5},{200,15}})));
  Modelica.Fluid.Valves.ValveDiscrete V20(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{140,110},{160,130}})));
  Modelica.Fluid.Valves.ValveDiscrete V24(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{100,110},{120,130}})));
  Modelica.Fluid.Valves.ValveDiscrete V25(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{60,110},{80,130}})));
  Modelica.Fluid.Valves.ValveDiscrete V1(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{20,110},{40,130}})));
  Modelica.Fluid.Valves.ValveDiscrete V3(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{-20,110},{0,130}})));
  Modelica.Fluid.Valves.ValveDiscrete V18(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{140,-85},{160,-65}})));
  Modelica.Fluid.Valves.ValveDiscrete V23(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{100,-85},{120,-65}})));
  Modelica.Fluid.Valves.ValveDiscrete V22(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{60,-85},{80,-65}})));
  Modelica.Fluid.Valves.ValveDiscrete V5(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{20,-85},{40,-65}})));
  Modelica.Fluid.Valves.ValveDiscrete V6(redeclare package Medium = Medium, m_flow_nominal=nominalValveMassFlow, dp_nominal=1e5) annotation(Placement(transformation(extent={{-20,-85},{0,-65}})));

  Modelica.Fluid.Sources.MassFlowSource_T condensateReturnSource(redeclare package Medium = Medium, use_m_flow_in=true, m_flow=0, T=system.T_ambient, nPorts=1) annotation(Placement(transformation(extent={{170,70},{190,90}})));
  Modelica.Fluid.Sources.MassFlowSource_T concentrateReturnSource(redeclare package Medium = Medium, use_m_flow_in=true, m_flow=0, T=system.T_ambient, nPorts=1) annotation(Placement(transformation(extent={{170,-10},{190,10}})));
  Modelica.Fluid.Sources.Boundary_pT condensateReturnBoundary(redeclare package Medium = Medium, nPorts=1, p=system.p_ambient, T=system.T_ambient) annotation(Placement(transformation(extent={{-70,110},{-50,130}})));
  Modelica.Fluid.Sources.Boundary_pT concentrateReturnBoundary(redeclare package Medium = Medium, nPorts=1, p=system.p_ambient, T=system.T_ambient) annotation(Placement(transformation(extent={{-70,-85},{-50,-65}})));
  Modelica.Fluid.Sources.Boundary_pT condenserBoundary(redeclare package Medium = Medium, nPorts=1, p=system.p_ambient, T=system.T_ambient) annotation(Placement(transformation(extent={{290,130},{310,150}})));

  Modelica.Fluid.Sensors.MassFlowRate fis801Sensor(redeclare package Medium = Medium) annotation(Placement(transformation(extent={{260,130},{280,150}})));

  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HeatB5 annotation(Placement(transformation(extent={{120,-130},{140,-110}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB6 annotation(Placement(transformation(extent={{260,55},{280,75}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB7 annotation(Placement(transformation(extent={{260,-25},{280,-5}})));
  Modelica.Blocks.Math.BooleanToReal heaterToReal(realTrue=B5HeaterDuty, realFalse=0) annotation(Placement(transformation(extent={{70,-130},{90,-110}})));
  Modelica.Blocks.Math.BooleanToReal b6CoolToReal(realTrue=B6CoolingDuty, realFalse=0) annotation(Placement(transformation(extent={{220,95},{240,115}})));
  Modelica.Blocks.Math.BooleanToReal b7CoolToReal(realTrue=B7CoolingDuty, realFalse=0) annotation(Placement(transformation(extent={{220,-65},{240,-45}})));
  Modelica.Blocks.Math.BooleanToReal p1FlowCmd(realTrue=0.30, realFalse=0) annotation(Placement(transformation(extent={{110,-40},{130,-20}})));
  Modelica.Blocks.Math.BooleanToReal p2FlowCmd(realTrue=0.30, realFalse=0) annotation(Placement(transformation(extent={{110,40},{130,60}})));
  Modelica.Blocks.Sources.BooleanTable startSchedule(table={startPulseTime, startPulseTime + 0.2, restartPulseTime, restartPulseTime + 0.2}, startValue=false) annotation(Placement(transformation(extent={{-190,200},{-170,220}})));
  Modelica.Blocks.Sources.BooleanConstant b3AvailableConst(k=true) annotation(Placement(transformation(extent={{-190,170},{-170,190}})));

  Modelica.Blocks.Sources.RealExpression lis301Expr(y=B3.level) annotation(Placement(transformation(extent={{-30,200},{-10,220}})));
  Modelica.Blocks.Sources.RealExpression qi302Expr(y=if B3.level > 0 then min(0.25, max(0, B3.level - 0.13)/max(B3.level, 1e-6)*0.25) else 0) annotation(Placement(transformation(extent={{10,200},{30,220}})));
  Modelica.Blocks.Sources.RealExpression lis501Expr(y=B5.level) annotation(Placement(transformation(extent={{50,200},{70,220}})));
  Modelica.Blocks.Sources.RealExpression qis502Expr(y=if B5.level > 0 and B5.level >= 0.18 then min(0.18, 0.08 + max(0, B5.level - 0.18)/max(B5.level, 1e-6)*0.10 + max(0, (system.T_ambient - 273.15 + 20) - (system.T_ambient - 273.15))/1000) else 0.08) annotation(Placement(transformation(extent={{90,200},{110,220}})));
  Modelica.Blocks.Sources.RealExpression tis602Expr(y=if controller.B6_cooler_on then 20 else 25) annotation(Placement(transformation(extent={{130,200},{150,220}})));
  Modelica.Blocks.Sources.RealExpression tis702Expr(y=if controller.B7_cooler_on then 25 else 30) annotation(Placement(transformation(extent={{170,200},{190,220}})));
  Modelica.Blocks.Sources.RealExpression lis601Expr(y=B6.level) annotation(Placement(transformation(extent={{210,200},{230,220}})));
  Modelica.Blocks.Sources.RealExpression lis701Expr(y=B7.level) annotation(Placement(transformation(extent={{250,200},{270,220}})));
  Modelica.Blocks.Sources.RealExpression fis801Expr(y=max(0, fis801Sensor.m_flow)) annotation(Placement(transformation(extent={{290,200},{310,220}})));

  NaClBatchController controller annotation(Placement(transformation(extent={{-20,-210},{80,-110}})));

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
  connect(sourceB1.ports[1], B1.ports[1]) annotation(Line(points={{-170,100},{-150,100}}, color={0,127,255}));
  connect(sourceB2.ports[1], B2.ports[1]) annotation(Line(points={{-170,30},{-150,30}}, color={0,127,255}));
  connect(B1.ports[2], V8.port_a) annotation(Line(points={{-130,84},{-130,102},{-100,102}}, color={0,127,255}));
  connect(V8.port_b, B3.ports[1]) annotation(Line(points={{-80,102},{-70,102},{-70,75},{-60,75}}, color={0,127,255}));
  connect(B2.ports[2], V9.port_a) annotation(Line(points={{-130,14},{-130,32},{-100,32}}, color={0,127,255}));
  connect(V9.port_b, B3.ports[2]) annotation(Line(points={{-80,32},{-70,32},{-70,55},{-60,55}}, color={0,127,255}));
  connect(B3.ports[3], V11.port_a) annotation(Line(points={{-40,49},{-40,65},{0,65}}, color={0,127,255}));
  connect(V11.port_b, B4.ports[1]) annotation(Line(points={{20,65},{30,65}}, color={0,127,255}));
  connect(B4.ports[2], V12.port_a) annotation(Line(points={{50,49},{50,65},{90,65}}, color={0,127,255}));
  connect(V12.port_b, B5.ports[1]) annotation(Line(points={{110,65},{120,65}}, color={0,127,255}));
  connect(B5.ports[2], K1.ports[1]) annotation(Line(points={{140,79},{140,140},{210,140}}, color={0,127,255}));
  connect(K1.ports[2], fis801Sensor.port_a) annotation(Line(points={{250,140},{260,140}}, color={0,127,255}));
  connect(fis801Sensor.port_b, condenserBoundary.ports[1]) annotation(Line(points={{280,140},{290,140}}, color={0,127,255}));
  connect(B5.ports[3], V15.port_a) annotation(Line(points={{140,49},{140,5},{180,5}}, color={0,127,255}));
  connect(V15.port_b, B7.ports[1]) annotation(Line(points={{200,5},{210,5}}, color={0,127,255}));
  connect(condensateReturnSource.ports[1], B6.ports[1]) annotation(Line(points={{190,80},{200,80},{200,75},{210,75}}, color={0,127,255}));
  connect(B6.ports[2], V20.port_a) annotation(Line(points={{230,49},{230,120},{140,120}}, color={0,127,255}));
  connect(V20.port_b, V24.port_a) annotation(Line(points={{160,120},{100,120}}, color={0,127,255}));
  connect(V24.port_b, V25.port_a) annotation(Line(points={{120,120},{60,120}}, color={0,127,255}));
  connect(V25.port_b, V1.port_a) annotation(Line(points={{80,120},{20,120}}, color={0,127,255}));
  connect(V1.port_b, V3.port_a) annotation(Line(points={{40,120},{-20,120}}, color={0,127,255}));
  connect(V3.port_b, condensateReturnBoundary.ports[1]) annotation(Line(points={{0,120},{-50,120}}, color={0,127,255}));
  connect(concentrateReturnSource.ports[1], B7.ports[2]) annotation(Line(points={{190,0},{200,0},{200,-11},{210,-11}}, color={0,127,255}));
  connect(B7.ports[2], V18.port_a) annotation(Line(points={{230,-31},{230,-75},{140,-75}}, color={0,127,255}));
  connect(V18.port_b, V23.port_a) annotation(Line(points={{160,-75},{100,-75}}, color={0,127,255}));
  connect(V23.port_b, V22.port_a) annotation(Line(points={{120,-75},{60,-75}}, color={0,127,255}));
  connect(V22.port_b, V5.port_a) annotation(Line(points={{80,-75},{20,-75}}, color={0,127,255}));
  connect(V5.port_b, V6.port_a) annotation(Line(points={{40,-75},{-20,-75}}, color={0,127,255}));
  connect(V6.port_b, concentrateReturnBoundary.ports[1]) annotation(Line(points={{0,-75},{-50,-75}}, color={0,127,255}));

  connect(B5.heatPort, HeatB5.port) annotation(Line(points={{140,85},{140,-110}}, color={191,0,0}));
  connect(B6.heatPort, CoolB6.port) annotation(Line(points={{250,85},{270,85},{270,75}}, color={191,0,0}));
  connect(B7.heatPort, CoolB7.port) annotation(Line(points={{250,5},{270,5},{270,-5}}, color={191,0,0}));

  connect(startSchedule.y, controller.startEnable) annotation(Line(points={{-169,210},{-80,210},{-80,-120},{-20,-120}}, color={255,0,255}));
  connect(b3AvailableConst.y, controller.B3_available) annotation(Line(points={{-169,180},{-90,180},{-90,-140},{-20,-140}}, color={255,0,255}));
  connect(lis301Expr.y, controller.LIS_301_m) annotation(Line(points={{-9,210},{0,210},{0,-150},{-20,-150}}, color={0,0,127}));
  connect(qi302Expr.y, controller.QI_302_kg_per_kg) annotation(Line(points={{31,210},{34,210},{34,-130},{-20,-130}}, color={0,0,127}));
  connect(lis501Expr.y, controller.LIS_501_m) annotation(Line(points={{71,210},{74,210},{74,-110},{-20,-110}}, color={0,0,127}));
  connect(qis502Expr.y, controller.QIS_502_kg_per_kg) annotation(Line(points={{111,210},{114,210},{114,-100},{-20,-100}}, color={0,0,127}));
  connect(tis602Expr.y, controller.TIS_602_degC) annotation(Line(points={{151,210},{154,210},{154,-90},{-20,-90}}, color={0,0,127}));
  connect(tis702Expr.y, controller.TIS_702_degC) annotation(Line(points={{191,210},{194,210},{194,-80},{-20,-80}}, color={0,0,127}));
  connect(fis801Expr.y, controller.FIS_801_kg_per_s) annotation(Line(points={{311,210},{314,210},{314,-70},{-20,-70}}, color={0,0,127}));
  connect(lis601Expr.y, controller.LIS_601_m) annotation(Line(points={{231,210},{234,210},{234,-60},{-20,-60}}, color={0,0,127}));
  connect(lis701Expr.y, controller.LIS_701_m) annotation(Line(points={{271,210},{274,210},{274,-50},{-20,-50}}, color={0,0,127}));

  connect(controller.T5_Heater, heaterToReal.u) annotation(Line(points={{80,-104},{90,-104},{90,-100},{60,-100},{60,-120},{70,-120}}, color={255,0,255}));
  connect(heaterToReal.y, HeatB5.Q_flow) annotation(Line(points={{91,-120},{120,-120}}, color={0,0,127}));
  connect(controller.B6_cooler_on, b6CoolToReal.u) annotation(Line(points={{80,-116},{200,-116},{200,105},{220,105}}, color={255,0,255}));
  connect(b6CoolToReal.y, CoolB6.Q_flow) annotation(Line(points={{241,105},{250,105},{250,65},{260,65}}, color={0,0,127}));
  connect(controller.B7_cooler_on, b7CoolToReal.u) annotation(Line(points={{80,-128},{200,-128},{200,-55},{220,-55}}, color={255,0,255}));
  connect(b7CoolToReal.y, CoolB7.Q_flow) annotation(Line(points={{241,-55},{250,-55},{250,-15},{260,-15}}, color={0,0,127}));
  connect(controller.P1_on, p1FlowCmd.u) annotation(Line(points={{80,-80},{100,-80},{100,-30},{110,-30}}, color={255,0,255}));
  connect(p1FlowCmd.y, concentrateReturnSource.m_flow_in) annotation(Line(points={{131,-30},{150,-30},{150,0},{170,0}}, color={0,0,127}));
  connect(controller.P2_on, p2FlowCmd.u) annotation(Line(points={{80,-92},{100,-92},{100,50},{110,50}}, color={255,0,255}));
  connect(p2FlowCmd.y, condensateReturnSource.m_flow_in) annotation(Line(points={{131,50},{150,50},{150,80},{170,80}}, color={0,0,127}));

  connect(controller.V8_open, V8.open) annotation(Line(points={{80,52},{90,52},{90,116},{-90,116},{-90,112}}, color={255,0,255}));
  connect(controller.V9_open, V9.open) annotation(Line(points={{80,40},{94,40},{94,46},{-90,46},{-90,42}}, color={255,0,255}));
  connect(controller.V11_open, V11.open) annotation(Line(points={{80,28},{98,28},{98,79},{10,79},{10,75}}, color={255,0,255}));
  connect(controller.V12_open, V12.open) annotation(Line(points={{80,16},{102,16},{102,79},{100,79},{100,75}}, color={255,0,255}));
  connect(controller.V15_open, V15.open) annotation(Line(points={{80,4},{106,4},{106,19},{190,19},{190,15}}, color={255,0,255}));
  connect(controller.V20_open, V20.open) annotation(Line(points={{80,-20},{118,-20},{118,134},{150,134},{150,130}}, color={255,0,255}));
  connect(controller.V24_open, V24.open) annotation(Line(points={{80,-56},{110,-56},{110,134},{110,130}}, color={255,0,255}));
  connect(controller.V25_open, V25.open) annotation(Line(points={{80,-68},{96,-68},{96,134},{70,134},{70,130}}, color={255,0,255}));
  connect(controller.V1_open, V1.open) annotation(Line(points={{80,100},{88,100},{88,134},{30,134},{30,130}}, color={255,0,255}));
  connect(controller.V3_open, V3.open) annotation(Line(points={{80,88},{84,88},{84,134},{-10,134},{-10,130}}, color={255,0,255}));
  connect(controller.V18_open, V18.open) annotation(Line(points={{80,-8},{118,-8},{118,-61},{150,-61},{150,-65}}, color={255,0,255}));
  connect(controller.V23_open, V23.open) annotation(Line(points={{80,-44},{110,-44},{110,-61},{110,-65}}, color={255,0,255}));
  connect(controller.V22_open, V22.open) annotation(Line(points={{80,-32},{96,-32},{96,-61},{70,-61},{70,-65}}, color={255,0,255}));
  connect(controller.V5_open, V5.open) annotation(Line(points={{80,76},{92,76},{92,-61},{30,-61},{30,-65}}, color={255,0,255}));
  connect(controller.V6_open, V6.open) annotation(Line(points={{80,64},{88,64},{88,-61},{-10,-61},{-10,-65}}, color={255,0,255}));

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
    Diagram(graphics={Text(extent={{-190,230},{-60,250}}, textString="NaCl batch plant baseline integration topology/control model")}),
    Icon(graphics={Text(extent={{-100,100},{100,140}}, textString="%name")}));
end NaClBatchPlantSystem;
