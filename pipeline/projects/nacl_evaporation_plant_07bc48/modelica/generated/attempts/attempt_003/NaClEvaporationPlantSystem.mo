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
  parameter Modelica.Units.SI.PressureDifference dpPumpValve = 1e5;
  parameter Real B3_w_start = 0.0;
  parameter Real B5_w_start = 0.0;

  Modelica.Fluid.Sources.Boundary_pT sourceB1(redeclare package Medium = Medium, p=101325 + 1.8e5, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-200,120},{-180,140}})));
  Modelica.Fluid.Sources.Boundary_pT sourceB2(redeclare package Medium = Medium, p=101325 + 1.8e5, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-200,60},{-180,80}})));
  Modelica.Fluid.Vessels.OpenTank B1(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.5, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.6, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-160,110},{-120,150}})));
  Modelica.Fluid.Vessels.OpenTank B2(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.35, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.6, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-160,0},{-120,40}})));
  Modelica.Fluid.Vessels.OpenTank B3(redeclare package Medium = Medium, crossArea=0.05, height=0.45, level_start=0.01, nPorts=3, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-80,50},{-40,90}})));
  Modelica.Fluid.Vessels.OpenTank B4(redeclare package Medium = Medium, crossArea=0.055, height=0.45, level_start=0.01, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{10,50},{50,90}})));
  Modelica.Fluid.Vessels.OpenTank B5(redeclare package Medium = Medium, crossArea=0.06, height=0.45, level_start=0.01, nPorts=3, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{100,50},{140,90}})));
  Modelica.Fluid.Vessels.OpenTank B6(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.01, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.4, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{220,100},{260,140}})));
  Modelica.Fluid.Vessels.OpenTank B7(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.01, nPorts=2, portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.4, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{220,-10},{260,30}})));

  Modelica.Fluid.Valves.ValveDiscrete V8(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpSupply) annotation(Placement(transformation(extent={{-120,120},{-100,140}})));
  Modelica.Fluid.Valves.ValveDiscrete V9(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpSupply) annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Fluid.Valves.ValveDiscrete V11(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpGravityValve) annotation(Placement(transformation(extent={{-20,60},{0,80}})));
  Modelica.Fluid.Valves.ValveDiscrete V12(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpGravityValve) annotation(Placement(transformation(extent={{60,60},{80,80}})));
  Modelica.Fluid.Valves.ValveDiscrete V15(redeclare package Medium = Medium, m_flow_nominal=mFlowValve, dp_nominal=dpGravityValve) annotation(Placement(transformation(extent={{160,0},{180,20}})));

  Modelica.Fluid.Sensors.MassFlowRate B6ReturnFlow annotation(Placement(transformation(extent={{-20,160},{0,180}})));
  Modelica.Fluid.Sensors.MassFlowRate B7ReturnFlow annotation(Placement(transformation(extent={{-20,-90},{0,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V5(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{20,160},{40,180}})));
  Modelica.Fluid.Valves.ValveDiscrete V6(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{50,160},{70,180}})));
  Modelica.Fluid.Valves.ValveDiscrete V20(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{80,160},{100,180}})));
  Modelica.Fluid.Valves.ValveDiscrete V24(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{110,160},{130,180}})));
  Modelica.Fluid.Valves.ValveDiscrete V25(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{140,160},{160,180}})));
  Modelica.Fluid.Sources.MassFlowSource_T P2source(redeclare package Medium = Medium, use_m_flow_in=true, m_flow=0, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-80,160},{-60,180}})));

  Modelica.Fluid.Valves.ValveDiscrete V1(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{20,-90},{40,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V3(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{50,-90},{70,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V18(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{80,-90},{100,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V22(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{110,-90},{130,-70}})));
  Modelica.Fluid.Valves.ValveDiscrete V23(redeclare package Medium = Medium, m_flow_nominal=mFlowPump, dp_nominal=dpPumpValve) annotation(Placement(transformation(extent={{140,-90},{160,-70}})));
  Modelica.Fluid.Sources.MassFlowSource_T P1source(redeclare package Medium = Medium, use_m_flow_in=true, m_flow=0, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-80,-90},{-60,-70}})));

  Modelica.Blocks.Math.BooleanToReal P1mFlow(realTrue=mFlowPump, realFalse=0) annotation(Placement(transformation(extent={{-120,-160},{-100,-140}})));
  Modelica.Blocks.Math.BooleanToReal P2mFlow(realTrue=mFlowPump, realFalse=0) annotation(Placement(transformation(extent={{-120,-190},{-100,-170}})));

  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor B5thermal(C=200000, T(start=293.15, fixed=true)) annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor B6thermal(C=50000, T(start=353.15, fixed=true)) annotation(Placement(transformation(extent={{220,60},{240,80}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor B7thermal(C=50000, T(start=353.15, fixed=true)) annotation(Placement(transformation(extent={{220,-50},{240,-30}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HeatB5 annotation(Placement(transformation(extent={{60,-20},{80,0}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB6 annotation(Placement(transformation(extent={{180,60},{200,80}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow CoolB7 annotation(Placement(transformation(extent={{180,-50},{200,-30}})));
  Modelica.Blocks.Math.BooleanToReal HeaterCmd(realTrue=20000, realFalse=0) annotation(Placement(transformation(extent={{20,-20},{40,0}})));
  Modelica.Blocks.Math.BooleanToReal B6CoolCmd(realTrue=-6500, realFalse=0) annotation(Placement(transformation(extent={{140,60},{160,80}})));
  Modelica.Blocks.Math.BooleanToReal B7CoolCmd(realTrue=-4500, realFalse=0) annotation(Placement(transformation(extent={{140,-50},{160,-30}})));

  Modelica.Blocks.Sources.BooleanConstant startEnable(k=true) annotation(Placement(transformation(extent={{-220,-160},{-200,-140}})));
  Modelica.Blocks.Sources.BooleanConstant B3available(k=true) annotation(Placement(transformation(extent={{-220,-190},{-200,-170}})));
  Modelica.Blocks.Sources.Constant fis801(k=0.12) annotation(Placement(transformation(extent={{-220,-220},{-200,-200}})));

  Modelica.Blocks.Sources.RealExpression B3Level(y=B3.level) annotation(Placement(transformation(extent={{-170,-40},{-150,-20}})));
  Modelica.Blocks.Sources.RealExpression B5Level(y=B5.level) annotation(Placement(transformation(extent={{-170,-70},{-150,-50}})));
  Modelica.Blocks.Sources.RealExpression B6Level(y=B6.level) annotation(Placement(transformation(extent={{-170,-100},{-150,-80}})));
  Modelica.Blocks.Sources.RealExpression B7Level(y=B7.level) annotation(Placement(transformation(extent={{-170,-130},{-150,-110}})));
  Modelica.Blocks.Sources.RealExpression B3w(y=B3_w_NaCl) annotation(Placement(transformation(extent={{-130,-40},{-110,-20}})));
  Modelica.Blocks.Sources.RealExpression B5w(y=B5_w_NaCl) annotation(Placement(transformation(extent={{-130,-70},{-110,-50}})));
  Modelica.Blocks.Sources.RealExpression B6Temp(y=B6thermal.T - 273.15) annotation(Placement(transformation(extent={{-130,-100},{-110,-80}})));
  Modelica.Blocks.Sources.RealExpression B7Temp(y=B7thermal.T - 273.15) annotation(Placement(transformation(extent={{-130,-130},{-110,-110}})));

  NaClBatchController controller(scanPeriod=scanPeriod) annotation(Placement(transformation(extent={{-80,-250},{0,-130}})));

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
  connect(sourceB1.ports[1], V8.port_a) annotation(Line(points={{-180,130},{-120,130}}, color={0,127,255}));
  connect(V8.port_b, B3.ports[1]) annotation(Line(points={{-100,130},{-90,130},{-90,78},{-80,78}}, color={0,127,255}));
  connect(sourceB2.ports[1], V9.port_a) annotation(Line(points={{-180,70},{-120,70}}, color={0,127,255}));
  connect(V9.port_b, B3.ports[2]) annotation(Line(points={{-100,70},{-90,70},{-90,62},{-80,62}}, color={0,127,255}));
  connect(B3.ports[3], V11.port_a) annotation(Line(points={{-60,50},{-60,70},{-20,70}}, color={0,127,255}));
  connect(V11.port_b, B4.ports[1]) annotation(Line(points={{0,70},{10,70}}, color={0,127,255}));
  connect(B4.ports[2], V12.port_a) annotation(Line(points={{30,50},{30,70},{60,70}}, color={0,127,255}));
  connect(V12.port_b, B5.ports[1]) annotation(Line(points={{80,70},{100,70}}, color={0,127,255}));
  connect(B5.ports[2], B6.ports[1]) annotation(Line(points={{120,90},{120,130},{220,130}}, color={0,127,255}));
  connect(B5.ports[3], V15.port_a) annotation(Line(points={{120,50},{120,10},{160,10}}, color={0,127,255}));
  connect(V15.port_b, B7.ports[1]) annotation(Line(points={{180,10},{220,10}}, color={0,127,255}));

  connect(B6.ports[2], B6ReturnFlow.port_a) annotation(Line(points={{240,100},{240,170},{-20,170}}, color={0,127,255}));
  connect(B6ReturnFlow.port_b, V5.port_a) annotation(Line(points={{0,170},{20,170}}, color={0,127,255}));
  connect(V5.port_b, V6.port_a) annotation(Line(points={{40,170},{50,170}}, color={0,127,255}));
  connect(V6.port_b, V20.port_a) annotation(Line(points={{70,170},{80,170}}, color={0,127,255}));
  connect(V20.port_b, V24.port_a) annotation(Line(points={{100,170},{110,170}}, color={0,127,255}));
  connect(V24.port_b, V25.port_a) annotation(Line(points={{130,170},{140,170}}, color={0,127,255}));
  connect(V25.port_b, B1.ports[2]) annotation(Line(points={{160,170},{180,170},{180,140},{-140,140}}, color={0,127,255}));
  connect(P2source.ports[1], B6ReturnFlow.port_a) annotation(Line(points={{-60,170},{-20,170}}, color={0,127,255}));

  connect(B7.ports[2], B7ReturnFlow.port_a) annotation(Line(points={{240,-10},{240,-80},{-20,-80}}, color={0,127,255}));
  connect(B7ReturnFlow.port_b, V1.port_a) annotation(Line(points={{0,-80},{20,-80}}, color={0,127,255}));
  connect(V1.port_b, V3.port_a) annotation(Line(points={{40,-80},{50,-80}}, color={0,127,255}));
  connect(V3.port_b, V18.port_a) annotation(Line(points={{70,-80},{80,-80}}, color={0,127,255}));
  connect(V18.port_b, V22.port_a) annotation(Line(points={{100,-80},{110,-80}}, color={0,127,255}));
  connect(V22.port_b, V23.port_a) annotation(Line(points={{130,-80},{140,-80}}, color={0,127,255}));
  connect(V23.port_b, B2.ports[2]) annotation(Line(points={{160,-80},{180,-80},{180,30},{-140,30}}, color={0,127,255}));
  connect(P1source.ports[1], B7ReturnFlow.port_a) annotation(Line(points={{-60,-80},{-20,-80}}, color={0,127,255}));

  connect(P1mFlow.y, P1source.m_flow_in) annotation(Line(points={{-99,-150},{-70,-150},{-70,-92}}, color={0,0,127}));
  connect(P2mFlow.y, P2source.m_flow_in) annotation(Line(points={{-99,-180},{-70,-180},{-70,158}}, color={0,0,127}));
  connect(HeatB5.port, B5thermal.port) annotation(Line(points={{80,-10},{100,-10}}, color={191,0,0}));
  connect(CoolB6.port, B6thermal.port) annotation(Line(points={{200,70},{220,70}}, color={191,0,0}));
  connect(CoolB7.port, B7thermal.port) annotation(Line(points={{200,-40},{220,-40}}, color={191,0,0}));
  connect(HeaterCmd.y, HeatB5.Q_flow) annotation(Line(points={{41,-10},{60,-10}}, color={0,0,127}));
  connect(B6CoolCmd.y, CoolB6.Q_flow) annotation(Line(points={{161,70},{180,70}}, color={0,0,127}));
  connect(B7CoolCmd.y, CoolB7.Q_flow) annotation(Line(points={{161,-40},{180,-40}}, color={0,0,127}));

  connect(startEnable.y, controller.startEnable) annotation(Line(points={{-199,-150},{-120,-150},{-120,-140},{-80,-140}}, color={255,0,255}));
  connect(B3available.y, controller.B3_available) annotation(Line(points={{-199,-180},{-124,-180},{-124,-154},{-80,-154}}, color={255,0,255}));
  connect(B3Level.y, controller.LIS_301) annotation(Line(points={{-149,-30},{-110,-30},{-110,-168},{-80,-168}}, color={0,0,127}));
  connect(B3w.y, controller.QI_302) annotation(Line(points={{-109,-30},{-106,-30},{-106,-182},{-80,-182}}, color={0,0,127}));
  connect(B5Level.y, controller.LIS_501) annotation(Line(points={{-149,-60},{-112,-60},{-112,-196},{-80,-196}}, color={0,0,127}));
  connect(B5w.y, controller.QIS_502) annotation(Line(points={{-109,-60},{-104,-60},{-104,-210},{-80,-210}}, color={0,0,127}));
  connect(B6Temp.y, controller.TIS_602) annotation(Line(points={{-109,-90},{-100,-90},{-100,-224},{-80,-224}}, color={0,0,127}));
  connect(B7Temp.y, controller.TIS_702) annotation(Line(points={{-109,-120},{-96,-120},{-96,-238},{-80,-238}}, color={0,0,127}));
  connect(B6Level.y, controller.LIS_601) annotation(Line(points={{-149,-90},{-116,-90},{-116,-244},{-80,-244}}, color={0,0,127}));
  connect(B7Level.y, controller.LIS_701) annotation(Line(points={{-149,-120},{-120,-120},{-120,-256},{-80,-256}}, color={0,0,127}));
  connect(fis801.y, controller.FIS_801) annotation(Line(points={{-199,-210},{-130,-210},{-130,-270},{-80,-270}}, color={0,0,127}));

  connect(controller.P1_on, P1mFlow.u) annotation(Line(points={{0,-96},{10,-96},{10,-150},{-120,-150}}, color={255,0,255}));
  connect(controller.P2_on, P2mFlow.u) annotation(Line(points={{0,-110},{14,-110},{14,-180},{-120,-180}}, color={255,0,255}));
  connect(controller.heater_B5_on, HeaterCmd.u) annotation(Line(points={{0,-124},{10,-124},{10,-10},{20,-10}}, color={255,0,255}));
  connect(controller.cooler_B6_on, B6CoolCmd.u) annotation(Line(points={{0,-138},{130,-138},{130,70},{140,70}}, color={255,0,255}));
  connect(controller.cooler_B7_on, B7CoolCmd.u) annotation(Line(points={{0,-152},{134,-152},{134,-40},{140,-40}}, color={255,0,255}));
  connect(controller.V8, V8.open) annotation(Line(points={{0,58},{-130,58},{-130,124},{-120,124}}, color={255,0,255}));
  connect(controller.V9, V9.open) annotation(Line(points={{0,44},{-134,44},{-134,64},{-120,64}}, color={255,0,255}));
  connect(controller.V11, V11.open) annotation(Line(points={{0,30},{-30,30},{-30,64},{-20,64}}, color={255,0,255}));
  connect(controller.V12, V12.open) annotation(Line(points={{0,16},{50,16},{50,64},{60,64}}, color={255,0,255}));
  connect(controller.V15, V15.open) annotation(Line(points={{0,2},{150,2},{150,4},{160,4}}, color={255,0,255}));
  connect(controller.V5, V5.open) annotation(Line(points={{0,86},{10,86},{10,164},{20,164}}, color={255,0,255}));
  connect(controller.V6, V6.open) annotation(Line(points={{0,72},{44,72},{44,164},{50,164}}, color={255,0,255}));
  connect(controller.V20, V20.open) annotation(Line(points={{0,-26},{74,-26},{74,164},{80,164}}, color={255,0,255}));
  connect(controller.V24, V24.open) annotation(Line(points={{0,-68},{104,-68},{104,164},{110,164}}, color={255,0,255}));
  connect(controller.V25, V25.open) annotation(Line(points={{0,-82},{134,-82},{134,164},{140,164}}, color={255,0,255}));
  connect(controller.V1, V1.open) annotation(Line(points={{0,114},{10,114},{10,-76},{20,-76}}, color={255,0,255}));
  connect(controller.V3, V3.open) annotation(Line(points={{0,100},{44,100},{44,-76},{50,-76}}, color={255,0,255}));
  connect(controller.V18, V18.open) annotation(Line(points={{0,-12},{74,-12},{74,-76},{80,-76}}, color={255,0,255}));
  connect(controller.V22, V22.open) annotation(Line(points={{0,-40},{104,-40},{104,-76},{110,-76}}, color={255,0,255}));
  connect(controller.V23, V23.open) annotation(Line(points={{0,-54},{134,-54},{134,-76},{140,-76}}, color={255,0,255}));

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

  annotation(experiment(StartTime=0, StopTime=3000, Tolerance=1e-6, Interval=5), Diagram(coordinateSystem(extent={{-240,-280},{280,220}})));
end NaClEvaporationPlantSystem;
