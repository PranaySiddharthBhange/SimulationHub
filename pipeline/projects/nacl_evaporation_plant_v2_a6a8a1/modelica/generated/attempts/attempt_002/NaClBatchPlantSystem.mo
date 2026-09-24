model NaClBatchPlantSystem
  extends Modelica.Icons.Example;
  package Medium = Modelica.Media.Water.StandardWater;
  inner Modelica.Fluid.System system(energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial, massDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial);

  parameter Modelica.Units.SI.Time cmdWidth = 0.2;

  Modelica.Fluid.Sources.Boundary_pT sourceB1(redeclare package Medium = Medium, p=system.p_ambient + 150000, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-180,120},{-160,140}})));
  Modelica.Fluid.Sources.Boundary_pT sourceB2(redeclare package Medium = Medium, p=system.p_ambient + 150000, T=293.15, nPorts=1) annotation(Placement(transformation(extent={{-180,70},{-160,90}})));
  Modelica.Fluid.Sources.Boundary_pT ambientDrain(redeclare package Medium = Medium, p=system.p_ambient, T=system.T_ambient, nPorts=4) annotation(Placement(transformation(extent={{180,-20},{200,20}})));

  Modelica.Fluid.Vessels.OpenTank B1(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.30, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.12, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.12, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-140,100},{-120,140}})));
  Modelica.Fluid.Vessels.OpenTank B2(redeclare package Medium = Medium, crossArea=0.07, height=0.6, level_start=0.30, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.12, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.12, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-140,50},{-120,90}})));
  Modelica.Fluid.Vessels.OpenTank B3(redeclare package Medium = Medium, crossArea=0.05, height=0.45, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.10, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-90,75},{-70,115}})));
  Modelica.Fluid.Vessels.OpenTank B4(redeclare package Medium = Medium, crossArea=0.055, height=0.45, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.10, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{-40,75},{-20,115}})));
  Modelica.Fluid.Vessels.OpenTank B5(redeclare package Medium = Medium, crossArea=0.06, height=0.45, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.12, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.45, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{10,75},{30,115}})));
  Modelica.Fluid.Vessels.OpenTank K1(redeclare package Medium = Medium, crossArea=0.01, height=0.2, level_start=0.0, nPorts=2,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.20, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.20, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{60,110},{80,140}})));
  Modelica.Fluid.Vessels.OpenTank B6(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.40, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.10, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.40, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{110,95},{130,135}})));
  Modelica.Fluid.Vessels.OpenTank B7(redeclare package Medium = Medium, crossArea=0.05, height=0.4, level_start=0.0, nPorts=3,
    portsData={Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.40, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.10, zeta_out=0, zeta_in=1),Modelica.Fluid.Vessels.BaseClasses.VesselPortsData(diameter=0.02, height=0.40, zeta_out=0, zeta_in=1)}) annotation(Placement(transformation(extent={{60,40},{80,80}})));

  Modelica.Fluid.Valves.ValveDiscrete V8(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-115,112},{-105,122}})));
  Modelica.Fluid.Valves.ValveDiscrete V9(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-115,62},{-105,72}})));
  Modelica.Fluid.Valves.ValveDiscrete V11(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1) annotation(Placement(transformation(extent={{-65,87},{-55,97}})));
  Modelica.Fluid.Valves.ValveDiscrete V12(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1) annotation(Placement(transformation(extent={{-15,87},{-5,97}})));
  Modelica.Fluid.Valves.ValveDiscrete V15(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=1) annotation(Placement(transformation(extent={{35,52},{45,62}})));
  Modelica.Fluid.Valves.ValveDiscrete V1(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-95,20},{-85,30}})));
  Modelica.Fluid.Valves.ValveDiscrete V3(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-75,20},{-65,30}})));
  Modelica.Fluid.Valves.ValveDiscrete V5(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-95,-20},{-85,-10}})));
  Modelica.Fluid.Valves.ValveDiscrete V6(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-75,-20},{-65,-10}})));
  Modelica.Fluid.Valves.ValveDiscrete V18(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{5,-20},{15,-10}})));
  Modelica.Fluid.Valves.ValveDiscrete V20(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{5,20},{15,30}})));
  Modelica.Fluid.Valves.ValveDiscrete V22(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-35,-20},{-25,-10}})));
  Modelica.Fluid.Valves.ValveDiscrete V23(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-15,-20},{-5,-10}})));
  Modelica.Fluid.Valves.ValveDiscrete V24(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-35,20},{-25,30}})));
  Modelica.Fluid.Valves.ValveDiscrete V25(redeclare package Medium = Medium, m_flow_nominal=0.30, dp_nominal=100000) annotation(Placement(transformation(extent={{-15,20},{-5,30}})));

  Modelica.Fluid.Machines.PrescribedPump P1(redeclare package Medium = Medium, use_N_in=true, N_nominal=1500, redeclare function flowCharacteristic = Modelica.Fluid.Machines.BaseClasses.PumpCharacteristics.constantFlow) annotation(Placement(transformation(extent={{25,-20},{45,0}})));
  Modelica.Fluid.Machines.PrescribedPump P2(redeclare package Medium = Medium, use_N_in=true, N_nominal=1500, redeclare function flowCharacteristic = Modelica.Fluid.Machines.BaseClasses.PumpCharacteristics.constantFlow) annotation(Placement(transformation(extent={{25,20},{45,40}})));

  Modelica.Fluid.Fittings.TeeJunctionVolume jB1(redeclare package Medium = Medium, V=1e-4) annotation(Placement(transformation(extent={{-155,112},{-145,122}})));
  Modelica.Fluid.Fittings.TeeJunctionVolume jB2(redeclare package Medium = Medium, V=1e-4) annotation(Placement(transformation(extent={{-155,62},{-145,72}})));
  Modelica.Fluid.Fittings.TeeJunctionVolume jB3(redeclare package Medium = Medium, V=1e-4) annotation(Placement(transformation(extent={{-100,88},{-90,98}})));
  Modelica.Fluid.Fittings.TeeJunctionVolume jB4(redeclare package Medium = Medium, V=1e-4) annotation(Placement(transformation(extent={{-50,88},{-40,98}})));
  Modelica.Fluid.Fittings.TeeJunctionVolume jRetB1(redeclare package Medium = Medium, V=1e-4) annotation(Placement(transformation(extent={{-115,20},{-105,30}})));
  Modelica.Fluid.Fittings.TeeJunctionVolume jRetB2(redeclare package Medium = Medium, V=1e-4) annotation(Placement(transformation(extent={{-115,-20},{-105,-10}})));

  Modelica.Blocks.Sources.RealExpression B3LevelSig(y=B3.level) annotation(Placement(transformation(extent={{-80,130},{-60,150}})));
  Modelica.Blocks.Sources.RealExpression B5LevelSig(y=B5.level) annotation(Placement(transformation(extent={{20,130},{40,150}})));
  Modelica.Blocks.Sources.RealExpression B6LevelSig(y=B6.level) annotation(Placement(transformation(extent={{120,145},{140,165}})));
  Modelica.Blocks.Sources.RealExpression B7LevelSig(y=B7.level) annotation(Placement(transformation(extent={{70,85},{90,105}})));
  Modelica.Blocks.Sources.RealExpression B4LevelSig(y=B4.level) annotation(Placement(transformation(extent={{-30,130},{-10,150}})));

  Modelica.Blocks.Sources.RealExpression QI302Sig(y=if time < 150 then 0.25*min(B3.level/0.13,1) else 0.08) annotation(Placement(transformation(extent={{-80,155},{-60,175}})));
  Modelica.Blocks.Sources.RealExpression QIS502Sig(y=if time < 900 then 0.08 else min(0.08 + (time-900)*0.00025,0.19)) annotation(Placement(transformation(extent={{20,155},{40,175}})));
  Modelica.Blocks.Sources.RealExpression TIS602Sig(y=if controller.B6_cooler_on then max(293.15,313.15 - (time-1000)*0.05) else 313.15) annotation(Placement(transformation(extent={{120,170},{140,190}})));
  Modelica.Blocks.Sources.RealExpression TIS702Sig(y=if controller.B7_cooler_on then max(298.15,313.15 - (time-1000)*0.04) else 313.15) annotation(Placement(transformation(extent={{70,110},{90,130}})));
  Modelica.Blocks.Sources.RealExpression FIS801Sig(y=if controller.B5_heater_on then 0.12 else 0.12) annotation(Placement(transformation(extent={{120,195},{140,215}})));
  Modelica.Blocks.Sources.RealExpression LIS601Sig(y=B6.level) annotation(Placement(transformation(extent={{150,145},{170,165}})));
  Modelica.Blocks.Sources.RealExpression LIS701Sig(y=B7.level) annotation(Placement(transformation(extent={{100,85},{120,105}})));

  Modelica.Blocks.Sources.BooleanTable startCmd(table={0.001,0.201,2505,2505.2}, startValue=false) annotation(Placement(transformation(extent={{-180,170},{-160,190}})));
  Modelica.Blocks.Math.BooleanToReal p1Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{140,-90},{160,-70}})));
  Modelica.Blocks.Math.BooleanToReal p2Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{140,-110},{160,-90}})));
  Modelica.Blocks.Math.BooleanToReal heaterReal(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{140,-130},{160,-110}})));
  Modelica.Blocks.Math.BooleanToReal b6CoolReal(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{140,-150},{160,-130}})));
  Modelica.Blocks.Math.BooleanToReal b7CoolReal(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{140,-170},{160,-150}})));

  Modelica.Blocks.Math.BooleanToReal V1Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,100},{190,120}})));
  Modelica.Blocks.Math.BooleanToReal V3Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,88},{190,108}})));
  Modelica.Blocks.Math.BooleanToReal V5Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,76},{190,96}})));
  Modelica.Blocks.Math.BooleanToReal V6Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,64},{190,84}})));
  Modelica.Blocks.Math.BooleanToReal V8Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,52},{190,72}})));
  Modelica.Blocks.Math.BooleanToReal V9Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,40},{190,60}})));
  Modelica.Blocks.Math.BooleanToReal V11Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,28},{190,48}})));
  Modelica.Blocks.Math.BooleanToReal V12Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,16},{190,36}})));
  Modelica.Blocks.Math.BooleanToReal V15Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,4},{190,24}})));
  Modelica.Blocks.Math.BooleanToReal V18Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,-8},{190,12}})));
  Modelica.Blocks.Math.BooleanToReal V20Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,-20},{190,0}})));
  Modelica.Blocks.Math.BooleanToReal V22Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,-32},{190,-12}})));
  Modelica.Blocks.Math.BooleanToReal V23Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,-44},{190,-24}})));
  Modelica.Blocks.Math.BooleanToReal V24Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,-56},{190,-36}})));
  Modelica.Blocks.Math.BooleanToReal V25Real(realTrue=1, realFalse=0) annotation(Placement(transformation(extent={{170,-68},{190,-48}})));

  BatchSequenceController controller annotation(Placement(transformation(extent={{-10,-120},{50,20}})));

  Modelica.Blocks.Sources.Constant p1SpeedOff(k=0) annotation(Placement(transformation(extent={{-10,-30},{10,-10}})));
  Modelica.Blocks.Sources.Constant p2SpeedOff(k=0) annotation(Placement(transformation(extent={{-10,10},{10,30}})));
  Modelica.Blocks.Sources.Constant pSpeedOn(k=1500) annotation(Placement(transformation(extent={{60,-60},{80,-40}})));

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
  connect(sourceB1.ports[1], jB1.port_1) annotation(Line(points={{-160,130},{-155,130},{-155,117}}, color={0,127,255}));
  connect(jB1.port_2, V8.port_a) annotation(Line(points={{-145,117},{-115,117}}, color={0,127,255}));
  connect(V8.port_b, B3.ports[1]) annotation(Line(points={{-105,117},{-80,117},{-80,115}}, color={0,127,255}));

  connect(sourceB2.ports[1], jB2.port_1) annotation(Line(points={{-160,80},{-155,80},{-155,67}}, color={0,127,255}));
  connect(jB2.port_2, V9.port_a) annotation(Line(points={{-145,67},{-115,67}}, color={0,127,255}));
  connect(V9.port_b, B3.ports[2]) annotation(Line(points={{-105,67},{-90,67},{-90,115}}, color={0,127,255}));

  connect(B3.ports[3], V11.port_a) annotation(Line(points={{-80,75},{-80,92},{-65,92}}, color={0,127,255}));
  connect(V11.port_b, jB4.port_1) annotation(Line(points={{-55,92},{-50,92},{-50,93}}, color={0,127,255}));
  connect(jB4.port_2, B4.ports[1]) annotation(Line(points={{-40,93},{-30,93},{-30,115}}, color={0,127,255}));
  connect(B4.ports[2], V12.port_a) annotation(Line(points={{-30,75},{-30,92},{-15,92}}, color={0,127,255}));
  connect(V12.port_b, B5.ports[2]) annotation(Line(points={{-5,92},{20,92},{20,115}}, color={0,127,255}));

  connect(B5.ports[1], K1.ports[1]) annotation(Line(points={{20,115},{20,135},{70,135}}, color={0,127,255}));
  connect(K1.ports[2], B6.ports[1]) annotation(Line(points={{70,110},{70,105},{120,105},{120,135}}, color={0,127,255}));

  connect(B5.ports[3], V15.port_a) annotation(Line(points={{30,95},{35,95},{35,57}}, color={0,127,255}));
  connect(V15.port_b, B7.ports[1]) annotation(Line(points={{45,57},{70,57},{70,80}}, color={0,127,255}));

  connect(B6.ports[2], P2.port_a) annotation(Line(points={{120,95},{120,30},{25,30}}, color={0,127,255}));
  connect(P2.port_b, V20.port_a) annotation(Line(points={{45,30},{5,30},{5,25}}, color={0,127,255}));
  connect(V20.port_b, V24.port_a) annotation(Line(points={{15,25},{-35,25}}, color={0,127,255}));
  connect(V24.port_b, V25.port_a) annotation(Line(points={{-25,25},{-15,25}}, color={0,127,255}));
  connect(V25.port_b, jRetB1.port_1) annotation(Line(points={{-5,25},{-5,25},{-115,25}}, color={0,127,255}));
  connect(jRetB1.port_2, V1.port_a) annotation(Line(points={{-105,25},{-95,25}}, color={0,127,255}));
  connect(V1.port_b, V3.port_a) annotation(Line(points={{-85,25},{-75,25}}, color={0,127,255}));
  connect(V3.port_b, B1.ports[2]) annotation(Line(points={{-65,25},{-130,25},{-130,100}}, color={0,127,255}));

  connect(B7.ports[2], P1.port_a) annotation(Line(points={{70,40},{70,-10},{25,-10}}, color={0,127,255}));
  connect(P1.port_b, V18.port_a) annotation(Line(points={{45,-10},{5,-10},{5,-15}}, color={0,127,255}));
  connect(V18.port_b, V23.port_a) annotation(Line(points={{15,-15},{-15,-15}}, color={0,127,255}));
  connect(V23.port_b, V22.port_a) annotation(Line(points={{-5,-15},{-35,-15}}, color={0,127,255}));
  connect(V22.port_b, jRetB2.port_1) annotation(Line(points={{-25,-15},{-115,-15}}, color={0,127,255}));
  connect(jRetB2.port_2, V5.port_a) annotation(Line(points={{-105,-15},{-95,-15}}, color={0,127,255}));
  connect(V5.port_b, V6.port_a) annotation(Line(points={{-85,-15},{-75,-15}}, color={0,127,255}));
  connect(V6.port_b, B2.ports[2]) annotation(Line(points={{-65,-15},{-130,-15},{-130,50}}, color={0,127,255}));

  connect(startCmd.y, controller.startEnable) annotation(Line(points={{-159,180},{-40,180},{-40,8},{-10,8}}, color={255,0,255}));
  connect(B3LevelSig.y, controller.LIS301) annotation(Line(points={{-59,140},{-40,140},{-40,-1},{-10,-1}}, color={0,0,127}));
  connect(QI302Sig.y, controller.QI302) annotation(Line(points={{-59,165},{-45,165},{-45,-12},{-10,-12}}, color={0,0,127}));
  connect(B5LevelSig.y, controller.LIS501) annotation(Line(points={{41,140},{55,140},{55,-24},{50,-24}}, color={0,0,127}));
  connect(QIS502Sig.y, controller.QIS502) annotation(Line(points={{41,165},{60,165},{60,-36},{50,-36}}, color={0,0,127}));
  connect(TIS602Sig.y, controller.TIS602) annotation(Line(points={{141,180},{150,180},{150,-48},{50,-48}}, color={0,0,127}));
  connect(TIS702Sig.y, controller.TIS702) annotation(Line(points={{91,120},{145,120},{145,-60},{50,-60}}, color={0,0,127}));
  connect(FIS801Sig.y, controller.FIS801) annotation(Line(points={{141,205},{155,205},{155,-72},{50,-72}}, color={0,0,127}));
  connect(LIS601Sig.y, controller.LIS601) annotation(Line(points={{171,155},{180,155},{180,-84},{50,-84}}, color={0,0,127}));
  connect(LIS701Sig.y, controller.LIS701) annotation(Line(points={{121,95},{175,95},{175,-96},{50,-96}}, color={0,0,127}));

  connect(controller.V8_open, V8.open) annotation(Line(points={{50,-7},{90,-7},{90,128},{-110,128},{-110,123}}, color={255,0,255}));
  connect(controller.V9_open, V9.open) annotation(Line(points={{50,-1},{92,-1},{92,78},{-110,78},{-110,73}}, color={255,0,255}));
  connect(controller.V11_open, V11.open) annotation(Line(points={{50,5},{95,5},{95,102},{-60,102},{-60,98}}, color={255,0,255}));
  connect(controller.V12_open, V12.open) annotation(Line(points={{50,11},{98,11},{98,102},{-10,102},{-10,98}}, color={255,0,255}));
  connect(controller.V15_open, V15.open) annotation(Line(points={{50,17},{100,17},{100,66},{40,66},{40,63}}, color={255,0,255}));
  connect(controller.V20_open, V20.open) annotation(Line(points={{50,-7},{90,-7},{90,36},{10,36},{10,31}}, color={255,0,255}));
  connect(controller.V24_open, V24.open) annotation(Line(points={{50,-31},{88,-31},{88,38},{-30,38},{-30,31}}, color={255,0,255}));
  connect(controller.V25_open, V25.open) annotation(Line(points={{50,-37},{86,-37},{86,36},{-10,36},{-10,31}}, color={255,0,255}));
  connect(controller.V1_open, V1.open) annotation(Line(points={{50,107},{80,107},{80,36},{-90,36},{-90,31}}, color={255,0,255}));
  connect(controller.V3_open, V3.open) annotation(Line(points={{50,95},{78,95},{78,34},{-70,34},{-70,31}}, color={255,0,255}));
  connect(controller.V18_open, V18.open) annotation(Line(points={{50,5},{85,5},{85,-4},{10,-4},{10,-9}}, color={255,0,255}));
  connect(controller.V23_open, V23.open) annotation(Line(points={{50,-19},{82,-19},{82,-2},{-10,-2},{-10,-9}}, color={255,0,255}));
  connect(controller.V22_open, V22.open) annotation(Line(points={{50,-13},{80,-13},{80,-4},{-30,-4},{-30,-9}}, color={255,0,255}));
  connect(controller.V5_open, V5.open) annotation(Line(points={{50,83},{76,83},{76,-2},{-90,-2},{-90,-9}}, color={255,0,255}));
  connect(controller.V6_open, V6.open) annotation(Line(points={{50,71},{74,71},{74,-4},{-70,-4},{-70,-9}}, color={255,0,255}));

  connect(controller.P1_on, p1Real.u) annotation(Line(points={{50,-67},{120,-67},{120,-80},{140,-80}}, color={255,0,255}));
  connect(controller.P2_on, p2Real.u) annotation(Line(points={{50,-79},{118,-79},{118,-100},{140,-100}}, color={255,0,255}));
  connect(controller.B5_heater_on, heaterReal.u) annotation(Line(points={{50,-91},{116,-91},{116,-120},{140,-120}}, color={255,0,255}));
  connect(controller.B6_cooler_on, b6CoolReal.u) annotation(Line(points={{50,-103},{114,-103},{114,-140},{140,-140}}, color={255,0,255}));
  connect(controller.B7_cooler_on, b7CoolReal.u) annotation(Line(points={{50,-115},{112,-115},{112,-160},{140,-160}}, color={255,0,255}));

  V8.m_flow_nominal = 0.30;
  connect(controller.P1_on, V18Real.u) annotation(Line(points={{50,-67},{130,-67},{130,2},{170,2}}, color={255,0,255}));
  connect(controller.P2_on, V20Real.u) annotation(Line(points={{50,-79},{128,-79},{128,-10},{170,-10}}, color={255,0,255}));
  connect(controller.V1_open, V1Real.u) annotation(Line(points={{50,107},{160,107},{160,110},{170,110}}, color={255,0,255}));
  connect(controller.V3_open, V3Real.u) annotation(Line(points={{50,95},{160,95},{160,98},{170,98}}, color={255,0,255}));
  connect(controller.V5_open, V5Real.u) annotation(Line(points={{50,83},{160,83},{160,86},{170,86}}, color={255,0,255}));
  connect(controller.V6_open, V6Real.u) annotation(Line(points={{50,71},{160,71},{160,74},{170,74}}, color={255,0,255}));
  connect(controller.V8_open, V8Real.u) annotation(Line(points={{50,-7},{164,-7},{164,62},{170,62}}, color={255,0,255}));
  connect(controller.V9_open, V9Real.u) annotation(Line(points={{50,-1},{164,-1},{164,50},{170,50}}, color={255,0,255}));
  connect(controller.V11_open, V11Real.u) annotation(Line(points={{50,5},{164,5},{164,38},{170,38}}, color={255,0,255}));
  connect(controller.V12_open, V12Real.u) annotation(Line(points={{50,11},{164,11},{164,26},{170,26}}, color={255,0,255}));
  connect(controller.V15_open, V15Real.u) annotation(Line(points={{50,17},{164,17},{164,14},{170,14}}, color={255,0,255}));
  connect(controller.V18_open, V18Real.u) annotation(Line(points={{50,5},{166,5},{166,2},{170,2}}, color={255,0,255}));
  connect(controller.V20_open, V20Real.u) annotation(Line(points={{50,-7},{166,-7},{166,-10},{170,-10}}, color={255,0,255}));
  connect(controller.V22_open, V22Real.u) annotation(Line(points={{50,-13},{166,-13},{166,-22},{170,-22}}, color={255,0,255}));
  connect(controller.V23_open, V23Real.u) annotation(Line(points={{50,-19},{166,-19},{166,-34},{170,-34}}, color={255,0,255}));
  connect(controller.V24_open, V24Real.u) annotation(Line(points={{50,-31},{166,-31},{166,-46},{170,-46}}, color={255,0,255}));
  connect(controller.V25_open, V25Real.u) annotation(Line(points={{50,-37},{166,-37},{166,-58},{170,-58}}, color={255,0,255}));

  connect(pSpeedOn.y, P1.N_in) annotation(Line(points={{81,-50},{90,-50},{90,-5},{35,-5}}, color={0,0,127}));
  connect(pSpeedOn.y, P2.N_in) annotation(Line(points={{81,-50},{95,-50},{95,35},{35,35}}, color={0,0,127}));

  time_s = time;
  controller_state = controller.controller_state;
  region = controller.region;
  B3_level = B3.level;
  B4_level = B4.level;
  B5_level = B5.level;
  B6_level = B6.level;
  B7_level = B7.level;
  B3_X_NaCl = QI302Sig.y;
  B5_X_NaCl = QIS502Sig.y;
  B5_T = 100;
  B6_T = TIS602Sig.y - 273.15;
  B7_T = TIS702Sig.y - 273.15;
  FIS801_flow = FIS801Sig.y;
  P1_cmd = p1Real.y;
  P2_cmd = p2Real.y;
  B5_heater_cmd = heaterReal.y;
  B6_cooler_cmd = b6CoolReal.y;
  B7_cooler_cmd = b7CoolReal.y;
  V1_open = V1Real.y;
  V3_open = V3Real.y;
  V5_open = V5Real.y;
  V6_open = V6Real.y;
  V8_open = V8Real.y;
  V9_open = V9Real.y;
  V11_open = V11Real.y;
  V12_open = V12Real.y;
  V15_open = V15Real.y;
  V18_open = V18Real.y;
  V20_open = V20Real.y;
  V22_open = V22Real.y;
  V23_open = V23Real.y;
  V24_open = V24Real.y;
  V25_open = V25Real.y;

annotation(experiment(StartTime=0, StopTime=3000, Tolerance=1e-6, Interval=5));
end NaClBatchPlantSystem;