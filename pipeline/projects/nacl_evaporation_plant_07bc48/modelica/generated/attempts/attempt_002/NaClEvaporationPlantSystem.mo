model NaClEvaporationPlantSystem
  extends Modelica.Icons.Example;
  package Medium = Modelica.Media.Water.ConstantPropertyLiquidWater;
  inner Modelica.Fluid.System system(
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    massDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    p_ambient=101325,
    T_ambient=293.15);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Modelica.Units.SI.Density rho = 1000;
  parameter Modelica.Units.SI.SpecificHeatCapacity cp = 4180;
  parameter Modelica.Units.SI.MassFlowRate mFlowValve = 0.30;
  parameter Modelica.Units.SI.MassFlowRate mFlowPump = 0.30;
  parameter Modelica.Units.SI.PressureDifference dpSupply = 1e5;
  parameter Modelica.Units.SI.PressureDifference dpGravityValve = 1;
  parameter Real B3_w_start = 0.0;
  parameter Real B5_w_start = 0.0;

  Modelica.Fluid.Sources.Boundary_pT sourceB1(redeclare package Medium = Medium, p=101325 + 1.8e5, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-180,120},{-160,140}})));
  Modelica.Fluid.Sources.Boundary_pT sourceB2(redeclare package Medium = Medium, p=101325 + 1.8e5, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-180,70},{-160,90}})));
  Modelica.Fluid.Vessels.OpenTank B3(redeclare package Medium = Medium, crossArea=0.05, height=0.45, level_start=0.01, nPorts=3, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-80,60},{-40,100}})));
  Modelica.Fluid.Vessels.OpenTank B4(redeclare package Medium = Medium, crossArea=0.055, height=0.45, level_start=0.01, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{20,60},{60,100}})));
  Modelica.Fluid.Vessels.OpenTank B5(redeclare package Medium = Medium, crossArea=0.06, height=0.45, level_start=0.01, nPorts=3, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{100,60},{140,100}})));
  Modelica.Fluid.Vessels.OpenTank B6(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.01, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.4, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{180,110},{220,150}})));
  Modelica.Fluid.Vessels.OpenTank B7(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.01, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.4, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{180,10},{220,50}})));
  Modelica.Fluid.Vessels.OpenTank B1(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.5, nPorts=1, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-140,110},{-100,150}})));
  Modelica.Fluid.Vessels.OpenTank B2(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.35, nPorts=1, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-140,10},{-100,50}})));

  Modelica.Fluid.Valves.ValveDiscrete V8(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpSupply) annotation(Placement(transformation(extent={{-130,120},{-110,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V9(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpSupply) annotation(Placement(transformation(extent={{-130,70},{-110,90}})));
  Modelica.Fluid.Valves.ValveDiscrete V11(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpGravityValve) annotation(Placement(transformation(extent={{-20,70},{0,90}})));
  Modelica.Fluid.Valves.ValveDiscrete V12(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpGravityValve) annotation(Placement(transformation(extent={{70,70},{90,90}})));
  Modelica.Fluid.Valves.ValveDiscrete V15(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpGravityValve) annotation(Placement(transformation(extent={{150,20},{170,40}})));
  Modelica.Fluid.Valves.ValveDiscrete V1(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
  Modelica.Fluid.Valves.ValveDiscrete V3(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{130,-70},{150,-50}})));
  Modelica.Fluid.Valves.ValveDiscrete V18(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{160,-70},{180,-50}})));
  Modelica.Fluid.Valves.ValveDiscrete V22(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{190,-70},{210,-50}})));
  Modelica.Fluid.Valves.ValveDiscrete V23(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{220,-70},{240,-50}})));
  Modelica.Fluid.Valves.ValveDiscrete V5(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{100,170},{120,190}})));
  Modelica.Fluid.Valves.ValveDiscrete V6(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{130,170},{150,190}})));
  Modelica.Fluid.Valves.ValveDiscrete V20(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{160,170},{180,190}})));
  Modelica.Fluid.Valves.ValveDiscrete V24(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{190,170},{210,190}})));
  Modelica.Fluid.Valves.ValveDiscrete V25(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=1.8e5) annotation(Placement(transformation(extent={{220,170},{240,190}})));

  Modelica.Fluid.Machines.PrescribedPump P1(redeclare package Medium = Medium, N_nominal=1500, use_N_in=true, redeclare function flowCharacteristic = Modelica.Fluid.Machines.BaseClasses.PumpCharacteristics.linearFlow(V_flow_nominal={0,0.0003}, head_nominal={18,0})) annotation(Placement(transformation(extent={{60,-70},{80,-50}})));
  Modelica.Fluid.Machines.PrescribedPump P2(redeclare package Medium = Medium, N_nominal=1500, use_N_in=true, redeclare function flowCharacteristic = Modelica.Fluid.Machines.BaseClasses.PumpCharacteristics.linearFlow(V_flow_nominal={0,0.0003}, head_nominal={18,0})) annotation(Placement(transformation(extent={{60,170},{80,190}})));
  Modelica.Blocks.Math.BooleanToReal P1speed(realTrue=1500, realFalse=0) annotation(Placement(transformation(extent={{20,-70},{40,-50}})));
  Modelica.Blocks.Math.BooleanToReal P2speed(realTrue=1500, realFalse=0) annotation(Placement(transformation(extent={{20,170},{40,190}})));

  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor B5thermal(C=200000, T(start=293.15, fixed=true)) annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor B6thermal(C=50000, T(start=353.15, fixed=true)) annotation(Placement(transformation(extent={{180,70},{200,90}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor B7thermal(C=50000, T(start=353.15, fixed=true)) annotation(Placement(transformation(extent={{180,-30},{200,-10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HeatB5 annotation(Placement(transformation(extent={{60,-10},{80,10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB6 annotation(Placement(transformation(extent={{140,70},{160,90}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB7 annotation(Placement(transformation(extent={{140,-30},{160,-10}})));
  Modelica.Blocks.Math.BooleanToReal HeaterCmd(realTrue=20000, realFalse=0) annotation(Placement(transformation(extent={{20,0},{40,20}})));
  Modelica.Blocks.Math.BooleanToReal B6CoolCmd(realTrue=-6500, realFalse=0) annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Math.BooleanToReal B7CoolCmd(realTrue=-4500, realFalse=0) annotation(Placement(transformation(extent={{100,-30},{120,-10}})));

  Modelica.Blocks.Sources.BooleanConstant startEnable(k=true) annotation(Placement(transformation(extent={{-180,-160},{-160,-140}})));
  Modelica.Blocks.Sources.BooleanConstant B3available(k=true) annotation(Placement(transformation(extent={{-180,-190},{-160,-170}})));
  Modelica.Blocks.Sources.Constant fis801(k=0.12) annotation(Placement(transformation(extent={{-180,-220},{-160,-200}})));

  Modelica.Blocks.Sources.RealExpression B3Level(y=B3.level) annotation(Placement(transformation(extent={{-120,-120},{-100,-100}})));
  Modelica.Blocks.Sources.RealExpression B5Level(y=B5.level) annotation(Placement(transformation(extent={{-120,-150},{-100,-130}})));
  Modelica.Blocks.Sources.RealExpression B6Level(y=B6.level) annotation(Placement(transformation(extent={{-120,-240},{-100,-220}})));
  Modelica.Blocks.Sources.RealExpression B7Level(y=B7.level) annotation(Placement(transformation(extent={{-120,-270},{-100,-250}})));
  Modelica.Blocks.Sources.RealExpression B3w(y=B3_w_NaCl) annotation(Placement(transformation(extent={{-80,-120},{-60,-100}})));
  Modelica.Blocks.Sources.RealExpression B5w(y=B5_w_NaCl) annotation(Placement(transformation(extent={{-80,-150},{-60,-130}})));
  Modelica.Blocks.Sources.RealExpression B6Temp(y=B6thermal.T - 273.15) annotation(Placement(transformation(extent={{-80,-180},{-60,-160}})));
  Modelica.Blocks.Sources.RealExpression B7Temp(y=B7thermal.T - 273.15) annotation(Placement(transformation(extent={{-80,-210},{-60,-190}})));

  NaClBatchController controller(scanPeriod=scanPeriod) annotation(Placement(transformation(extent={{-20,-220},{40,-120}})));

  Real time_s;
  Real controller_state;
  Real region;
  Real B3_level_m;
  Real B4_level_m;
  Real B5_level_m;
  Real B6_level_m;
  Real B7_level_m;
  Real B3_w_NaCl(start=B3_w_start, fixed=true);
  Real B5_w_NaCl(start=B5_w_start, fixed=true);
  Real B5_temp_C;
  Real B6_temp_C;
  Real B7_temp_C;
  Real FIS801_kg_s;
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
  connect(sourceB1.ports[1], V8.port_a) annotation(Line(points={{-160,130},{-130,130}}, color={0,127,255}));
  connect(V8.port_b, B3.ports[1]) annotation(Line(points={{-110,130},{-90,130},{-90,88},{-80,88}}, color={0,127,255}));
  connect(sourceB2.ports[1], V9.port_a) annotation(Line(points={{-160,80},{-130,80}}, color={0,127,255}));
  connect(V9.port_b, B3.ports[2]) annotation(Line(points={{-110,80},{-80,80}}, color={0,127,255}));
  connect(B3.ports[3], V11.port_a) annotation(Line(points={{-60,60},{-60,80},{-20,80}}, color={0,127,255}));
  connect(V11.port_b, B4.ports[1]) annotation(Line(points={{0,80},{20,80}}, color={0,127,255}));
  connect(B4.ports[2], V12.port_a) annotation(Line(points={{40,60},{40,80},{70,80}}, color={0,127,255}));
  connect(V12.port_b, B5.ports[1]) annotation(Line(points={{90,80},{100,80}}, color={0,127,255}));
  connect(B5.ports[2], B6.ports[1]) annotation(Line(points={{120,100},{120,140},{180,140}}, color={0,127,255}));
  connect(B5.ports[3], V15.port_a) annotation(Line(points={{120,60},{120,30},{150,30}}, color={0,127,255}));
  connect(V15.port_b, B7.ports[1]) annotation(Line(points={{170,30},{180,30}}, color={0,127,255}));
  connect(B6.ports[2], P2.port_a) annotation(Line(points={{200,110},{200,180},{60,180}}, color={0,127,255}));
  connect(P2.port_b, V5.port_a) annotation(Line(points={{80,180},{100,180}}, color={0,127,255}));
  connect(V5.port_b, V6.port_a) annotation(Line(points={{120,180},{130,180}}, color={0,127,255}));
  connect(V6.port_b, V20.port_a) annotation(Line(points={{150,180},{160,180}}, color={0,127,255}));
  connect(V20.port_b, V24.port_a) annotation(Line(points={{180,180},{190,180}}, color={0,127,255}));
  connect(V24.port_b, V25.port_a) annotation(Line(points={{210,180},{220,180}}, color={0,127,255}));
  connect(V25.port_b, B1.ports[1]) annotation(Line(points={{240,180},{260,180},{260,130},{-120,130}}, color={0,127,255}));
  connect(B7.ports[2], P1.port_a) annotation(Line(points={{200,10},{200,-60},{60,-60}}, color={0,127,255}));
  connect(P1.port_b, V1.port_a) annotation(Line(points={{80,-60},{100,-60}}, color={0,127,255}));
  connect(V1.port_b, V3.port_a) annotation(Line(points={{120,-60},{130,-60}}, color={0,127,255}));
  connect(V3.port_b, V18.port_a) annotation(Line(points={{150,-60},{160,-60}}, color={0,127,255}));
  connect(V18.port_b, V22.port_a) annotation(Line(points={{180,-60},{190,-60}}, color={0,127,255}));
  connect(V22.port_b, V23.port_a) annotation(Line(points={{210,-60},{220,-60}}, color={0,127,255}));
  connect(V23.port_b, B2.ports[1]) annotation(Line(points={{240,-60},{260,-60},{260,30},{-120,30}}, color={0,127,255}));

  connect(P1speed.y, P1.N_in) annotation(Line(points={{41,-60},{60,-60}}, color={0,0,127}));
  connect(P2speed.y, P2.N_in) annotation(Line(points={{41,180},{60,180}}, color={0,0,127}));
  connect(HeatB5.port, B5thermal.port) annotation(Line(points={{80,0},{100,0}}, color={191,0,0}));
  connect(CoolB6.port, B6thermal.port) annotation(Line(points={{160,80},{180,80}}, color={191,0,0}));
  connect(CoolB7.port, B7thermal.port) annotation(Line(points={{160,-20},{180,-20}}, color={191,0,0}));
  connect(HeaterCmd.y, HeatB5.Q_flow) annotation(Line(points={{41,10},{60,10}}, color={0,0,127}));
  connect(B6CoolCmd.y, CoolB6.Q_flow) annotation(Line(points={{121,80},{140,80}}, color={0,0,127}));
  connect(B7CoolCmd.y, CoolB7.Q_flow) annotation(Line(points={{121,-20},{140,-20}}, color={0,0,127}));

  connect(startEnable.y, controller.startEnable) annotation(Line(points={{-159,-150},{-40,-150},{-40,-130},{-20,-130}}, color={255,0,255}));
  connect(B3available.y, controller.B3_available) annotation(Line(points={{-159,-180},{-30,-180},{-30,-140},{-20,-140}}, color={255,0,255}));
  connect(B3Level.y, controller.LIS_301) annotation(Line(points={{-99,-110},{-50,-110},{-50,-150},{-20,-150}}, color={0,0,127}));
  connect(B3w.y, controller.QI_302) annotation(Line(points={{-59,-110},{-45,-110},{-45,-160},{-20,-160}}, color={0,0,127}));
  connect(B5Level.y, controller.LIS_501) annotation(Line(points={{-99,-140},{-40,-140},{-40,-170},{-20,-170}}, color={0,0,127}));
  connect(B5w.y, controller.QIS_502) annotation(Line(points={{-59,-140},{-35,-140},{-35,-180},{-20,-180}}, color={0,0,127}));
  connect(B6Temp.y, controller.TIS_602) annotation(Line(points={{-59,-170},{-30,-170},{-30,-190},{-20,-190}}, color={0,0,127}));
  connect(B7Temp.y, controller.TIS_702) annotation(Line(points={{-59,-200},{-25,-200},{-25,-200},{-20,-200}}, color={0,0,127}));
  connect(B6Level.y, controller.LIS_601) annotation(Line(points={{-99,-230},{-60,-230},{-60,-210},{-20,-210}}, color={0,0,127}));
  connect(B7Level.y, controller.LIS_701) annotation(Line(points={{-99,-260},{-70,-260},{-70,-220},{-20,-220}}, color={0,0,127}));
  connect(fis801.y, controller.FIS_801) annotation(Line(points={{-159,-210},{-80,-210},{-80,-230},{-20,-230}}, color={0,0,127}));

  connect(controller.P1_on, P1speed.u) annotation(Line(points={{40,-100},{10,-100},{10,-60},{20,-60}}, color={255,0,255}));
  connect(controller.P2_on, P2speed.u) annotation(Line(points={{40,-114},{10,-114},{10,180},{20,180}}, color={255,0,255}));
  connect(controller.heater_B5_on, HeaterCmd.u) annotation(Line(points={{40,-128},{0,-128},{0,10},{20,10}}, color={255,0,255}));
  connect(controller.cooler_B6_on, B6CoolCmd.u) annotation(Line(points={{40,-142},{90,-142},{90,80},{100,80}}, color={255,0,255}));
  connect(controller.cooler_B7_on, B7CoolCmd.u) annotation(Line(points={{40,-156},{95,-156},{95,-20},{100,-20}}, color={255,0,255}));
  connect(controller.V8, V8.open) annotation(Line(points={{40,54},{-140,54},{-140,124},{-130,124}}, color={255,0,255}));
  connect(controller.V9, V9.open) annotation(Line(points={{40,40},{-145,40},{-145,74},{-130,74}}, color={255,0,255}));
  connect(controller.V11, V11.open) annotation(Line(points={{40,26},{-30,26},{-30,74},{-20,74}}, color={255,0,255}));
  connect(controller.V12, V12.open) annotation(Line(points={{40,12},{50,12},{50,74},{70,74}}, color={255,0,255}));
  connect(controller.V15, V15.open) annotation(Line(points={{40,-2},{145,-2},{145,24},{150,24}}, color={255,0,255}));
  connect(controller.V1, V1.open) annotation(Line(points={{40,110},{90,110},{90,-56},{100,-56}}, color={255,0,255}));
  connect(controller.V3, V3.open) annotation(Line(points={{40,96},{95,96},{95,-58},{130,-58}}, color={255,0,255}));
  connect(controller.V18, V18.open) annotation(Line(points={{40,-16},{155,-16},{155,-58},{160,-58}}, color={255,0,255}));
  connect(controller.V22, V22.open) annotation(Line(points={{40,-44},{185,-44},{185,-58},{190,-58}}, color={255,0,255}));
  connect(controller.V23, V23.open) annotation(Line(points={{40,-58},{215,-58},{215,-58},{220,-58}}, color={255,0,255}));
  connect(controller.V5, V5.open) annotation(Line(points={{40,82},{90,82},{90,174},{100,174}}, color={255,0,255}));
  connect(controller.V6, V6.open) annotation(Line(points={{40,68},{95,68},{95,176},{130,176}}, color={255,0,255}));
  connect(controller.V20, V20.open) annotation(Line(points={{40,-30},{155,-30},{155,176},{160,176}}, color={255,0,255}));
  connect(controller.V24, V24.open) annotation(Line(points={{40,-72},{185,-72},{185,176},{190,176}}, color={255,0,255}));
  connect(controller.V25, V25.open) annotation(Line(points={{40,-86},{215,-86},{215,176},{220,176}}, color={255,0,255}));

  der(B3_w_NaCl) = if controller.V9 then 0.0005 else if controller.V11 and B3.level > 1e-4 then -0.0008*B3_w_NaCl else 0;
  der(B5_w_NaCl) = if controller.heater_B5_on then 0.0002 else if controller.V15 and B5.level > 1e-4 then -0.0001*max(B5_w_NaCl - 0.18, 0) else 0;

  time_s = time;
  controller_state = controller.controller_state;
  region = controller.region;
  B3_level_m = B3.level;
  B4_level_m = B4.level;
  B5_level_m = B5.level;
  B6_level_m = B6.level;
  B7_level_m = B7.level;
  B5_temp_C = B5thermal.T - 273.15;
  B6_temp_C = B6thermal.T - 273.15;
  B7_temp_C = B7thermal.T - 273.15;
  FIS801_kg_s = fis801.y;
  P1_cmd = if controller.P1_on then 1 else 0;
  P2_cmd = if controller.P2_on then 1 else 0;
  B5_heater_cmd = if controller.heater_B5_on then 1 else 0;
  B6_cooler_cmd = if controller.cooler_B6_on then 1 else 0;
  B7_cooler_cmd = if controller.cooler_B7_on then 1 else 0;
  V1_open = if controller.V1 then 1 else 0;
  V3_open = if controller.V3 then 1 else 0;
  V5_open = if controller.V5 then 1 else 0;
  V6_open = if controller.V6 then 1 else 0;
  V8_open = if controller.V8 then 1 else 0;
  V9_open = if controller.V9 then 1 else 0;
  V11_open = if controller.V11 then 1 else 0;
  V12_open = if controller.V12 then 1 else 0;
  V15_open = if controller.V15 then 1 else 0;
  V18_open = if controller.V18 then 1 else 0;
  V20_open = if controller.V20 then 1 else 0;
  V22_open = if controller.V22 then 1 else 0;
  V23_open = if controller.V23 then 1 else 0;
  V24_open = if controller.V24 then 1 else 0;
  V25_open = if controller.V25 then 1 else 0;

  annotation(experiment(StartTime=0, StopTime=3000, Tolerance=1e-6, Interval=5), Diagram(coordinateSystem(extent={{-220,-280},{280,220}})));
end NaClEvaporationPlantSystem;
