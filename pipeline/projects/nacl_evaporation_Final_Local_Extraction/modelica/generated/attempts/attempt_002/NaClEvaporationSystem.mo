model NaClEvaporationSystem
  extends Modelica.Icons.Example;
  SimpleTank B3(area_m2=1, level_start_m=0, levelMax_m=0.45, wNaCl_start=0, temperature_start_degC=25) annotation(Placement(transformation(extent={{-80,40},{-40,80}})));
  SimpleTank B4(area_m2=1, level_start_m=0, levelMax_m=0.45, wNaCl_start=0, temperature_start_degC=25) annotation(Placement(transformation(extent={{-20,40},{20,80}})));
  SimpleTank B5(area_m2=0.060, level_start_m=0, levelMax_m=0.45, wNaCl_start=0.08, temperature_start_degC=25) annotation(Placement(transformation(extent={{40,40},{80,80}})));
  SimpleTank B6(area_m2=0.050, level_start_m=0, levelMax_m=0.40, wNaCl_start=0, temperature_start_degC=30) annotation(Placement(transformation(extent={{40,-20},{80,20}})));
  SimpleTank B7(area_m2=0.050, level_start_m=0, levelMax_m=0.40, wNaCl_start=0.18, temperature_start_degC=30) annotation(Placement(transformation(extent={{40,-80},{80,-40}})));
  NaClEvaporationController controller annotation(Placement(transformation(extent={{-10,-80},{30,20}})));
  Modelica.Blocks.Sources.Constant zero(k=0) annotation(Placement(transformation(extent={{-160,-80},{-140,-60}})));
  Modelica.Blocks.Sources.Constant ambient25(k=25) annotation(Placement(transformation(extent={{-160,-110},{-140,-90}})));
  Real V8_flow;
  Real V9_flow;
  Real V11_flow;
  Real V12_flow;
  Real V15_flow;
  Real P2_flow;
  Real P1_flow;
  Real evapRate;
  Real condenseRate;
  Real heaterTemperatureRise_degC_s;
  Real coolerB6TemperatureFall_degC_s;
  Real coolerB7TemperatureFall_degC_s;
  Real LIS_301;
  Real QI_302;
  Real LIS_501;
  Real QIS_502;
  Real TIS_602;
  Real TIS_702;
  Real FIS_801;
  Real LIS_701;
equation
  LIS_301 = B3.level_m;
  QI_302 = B3.wNaCl;
  LIS_501 = B5.level_m;
  QIS_502 = B5.wNaCl;
  TIS_602 = B6.temperature_degC;
  TIS_702 = B7.temperature_degC;
  LIS_701 = B7.level_m;
  FIS_801 = 0.2;

  controller.LIS_301 = LIS_301;
  controller.QI_302 = QI_302;
  controller.LIS_501 = LIS_501;
  controller.QIS_502 = QIS_502;
  controller.TIS_602 = TIS_602;
  controller.TIS_702 = TIS_702;
  controller.FIS_801 = FIS_801;
  controller.LIS_701 = LIS_701;

  V8_flow = if controller.V8 then 0.02 else 0;
  V9_flow = if controller.V9 then 0.005 else 0;
  V11_flow = if controller.V11 then 0.02 else 0;
  V12_flow = if controller.V12 then 0.02 else 0;
  V15_flow = if controller.V15 then 0.01 else 0;
  P2_flow = if controller.P2 then 0.01 else 0;
  P1_flow = if controller.P1 then 0.01 else 0;
  evapRate = if controller.B5_Heater then 0.001 else 0;
  condenseRate = evapRate;
  heaterTemperatureRise_degC_s = if controller.B5_Heater then 2 else 0;
  coolerB6TemperatureFall_degC_s = if controller.B6_Cooler then 5 else 0;
  coolerB7TemperatureFall_degC_s = if controller.B7_Cooler then 4 else 0;

  B3.inflow_m3_s = V8_flow + V9_flow;
  B3.inflow_wNaCl = if V8_flow + V9_flow > 0 then (V8_flow*0 + V9_flow*0.2)/(V8_flow + V9_flow) else 0;
  B3.inflow_T_degC = 25;
  B3.outflow_m3_s = V11_flow;

  B4.inflow_m3_s = V11_flow;
  B4.inflow_wNaCl = B3.wNaCl;
  B4.inflow_T_degC = B3.temperature_degC;
  B4.outflow_m3_s = V12_flow;

  B5.inflow_m3_s = V12_flow;
  B5.inflow_wNaCl = B4.wNaCl;
  B5.inflow_T_degC = B4.temperature_degC + heaterTemperatureRise_degC_s;
  B5.outflow_m3_s = V15_flow + evapRate;

  B6.inflow_m3_s = condenseRate;
  B6.inflow_wNaCl = 0;
  B6.inflow_T_degC = max(20, 30 - coolerB6TemperatureFall_degC_s);
  B6.outflow_m3_s = P2_flow;

  B7.inflow_m3_s = V15_flow;
  B7.inflow_wNaCl = B5.wNaCl;
  B7.inflow_T_degC = max(25, B5.temperature_degC - coolerB7TemperatureFall_degC_s);
  B7.outflow_m3_s = P1_flow;

  annotation(experiment(StartTime=0, StopTime=3000, Tolerance=1e-6, Interval=1),
             Diagram(graphics={Text(extent={{-140,100},{140,90}}, textString="NaCl evaporation batch system") }));
end NaClEvaporationSystem;
