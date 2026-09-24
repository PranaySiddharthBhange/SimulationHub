model NaClBatchPlantSystem
  extends Modelica.Icons.Example;
  parameter Modelica.Units.SI.Time scanPeriod = 1;
  parameter Modelica.Units.SI.Density rho = 1000 "Assumption: baseline incompressible density because WaterNaCl medium implementation evidence is insufficient for executable medium package";
  parameter Modelica.Units.SI.SpecificHeatCapacity cp = 4180 "Assumption: baseline heat capacity for executable thermal balance";
  parameter Modelica.Units.SI.VolumeFlowRate qV8 = 5.0e-5;
  parameter Modelica.Units.SI.VolumeFlowRate qV9 = 2.0e-5;
  parameter Modelica.Units.SI.VolumeFlowRate qV11 = 4.0e-5;
  parameter Modelica.Units.SI.VolumeFlowRate qV12 = 4.0e-5;
  parameter Modelica.Units.SI.VolumeFlowRate qV15 = 1.5e-5;
  parameter Modelica.Units.SI.MassFlowRate mP1 = 0.30;
  parameter Modelica.Units.SI.MassFlowRate mP2 = 0.30;
  parameter Modelica.Units.SI.Time cmdWidth = 2*scanPeriod;
  parameter Modelica.Units.SI.Temperature TcoolingWater = 293.15 "Assumption: condenser cooling-water temperature not stated; aligned with ambient";
  parameter Modelica.Units.SI.SpecificEnthalpy hVap = 2.26e6 "Assumption: latent heat surrogate for executable condensate generation";

  NaClBatchController controller(scanPeriod=scanPeriod) annotation(Placement(transformation(extent={{-10,120},{30,160}})));

  Modelica.Blocks.Sources.BooleanTable startSrc(table={1,1 + cmdWidth}, startValue=false) annotation(Placement(transformation(extent={{-180,150},{-160,170}})));
  Modelica.Blocks.Sources.BooleanTable availSrc(table={0}, startValue=true) annotation(Placement(transformation(extent={{-180,120},{-160,140}})));

  Real B1_level(start=0.5, fixed=true);
  Real B2_level(start=0.35, fixed=true);
  Real B3_level(start=0.01, fixed=true);
  Real B4_level(start=0.01, fixed=true);
  Real B5_level(start=0.01, fixed=true);
  Real B6_level(start=0.01, fixed=true);
  Real B7_level(start=0.01, fixed=true);
  Real B3_saltMass(start=0.0, fixed=true);
  Real B4_saltMass(start=0.0, fixed=true);
  Real B5_saltMass(start=0.0, fixed=true);
  Real B5_temp(start=293.15, fixed=true);
  Real B6_temp(start=293.15, fixed=true);
  Real B7_temp(start=293.15, fixed=true);

  Real q8;
  Real q9;
  Real q11;
  Real q12;
  Real q15;
  Real qP1;
  Real qP2;
  Real mEvap;
  Real mCond;
  Real QB5;
  Real QB6;
  Real QB7;
  Real mB3;
  Real mB4;
  Real mB5;
  Real mB6;
  Real mB7;
  Real wB4;
  Real wB5;
  Real condenserHeatRemoval;
  Real condenserDeltaT;
  Real coolingWaterCp;

  Modelica.Blocks.Sources.RealExpression lis301(y=B3_level) annotation(Placement(transformation(extent={{-100,70},{-80,90}})));
  Modelica.Blocks.Sources.RealExpression qi302(y=B3_w_NaCl) annotation(Placement(transformation(extent={{-100,40},{-80,60}})));
  Modelica.Blocks.Sources.RealExpression lis501(y=B5_level) annotation(Placement(transformation(extent={{-100,10},{-80,30}})));
  Modelica.Blocks.Sources.RealExpression qis502(y=B5_w_NaCl) annotation(Placement(transformation(extent={{-100,-20},{-80,0}})));
  Modelica.Blocks.Sources.RealExpression tis602(y=B6_temp - 273.15) annotation(Placement(transformation(extent={{-100,-50},{-80,-30}})));
  Modelica.Blocks.Sources.RealExpression tis702(y=B7_temp - 273.15) annotation(Placement(transformation(extent={{-100,-80},{-80,-60}})));
  Modelica.Blocks.Sources.RealExpression fis801(y=FIS801_kg_s) annotation(Placement(transformation(extent={{-100,-110},{-80,-90}})));
  Modelica.Blocks.Sources.RealExpression lis601(y=B6_level) annotation(Placement(transformation(extent={{-100,-140},{-80,-120}})));
  Modelica.Blocks.Sources.RealExpression lis701(y=B7_level) annotation(Placement(transformation(extent={{-100,-170},{-80,-150}})));

  Real time_s;
  Integer controller_state;
  Integer region;
  Real B3_level_m;
  Real B4_level_m;
  Real B5_level_m;
  Real B6_level_m;
  Real B7_level_m;
  Real B3_w_NaCl;
  Real B5_w_NaCl;
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
  q8 = if controller.V8 and B1_level > 0 then min(qV8, B1_level*0.07) else 0;
  q9 = if controller.V9 and B2_level > 0 then min(qV9, B2_level*0.07) else 0;
  q11 = if controller.V11 and B3_level > 0.01 then qV11 else 0;
  q12 = if controller.V12 and B4_level > 0 then qV12 else 0;
  q15 = if controller.V15 and B5_level > 0.01 then qV15 else 0;
  qP1 = if controller.P1 and B7_level > 0.02 then mP1/rho else 0;
  qP2 = if controller.P2 and B6_level > 0.02 then mP2/rho else 0;

  QB5 = if controller.heaterB5 then 20000 else 0;
  QB6 = if controller.coolerB6 then -6500 else 0;
  QB7 = if controller.coolerB7 then -4500 else 0;

  mEvap = if controller.heaterB5 and B5_level > 0.05 then min(max(QB5/hVap, 0), rho*q12 + max(mB5 - rho*0.06*0.01, 0)) else 0;
  mCond = mEvap;

  der(B1_level) = (-q8 + qP2)/0.07;
  der(B2_level) = (-q9 + qP1)/0.07;
  der(B3_level) = (q8 + q9 - q11)/0.05;
  der(B4_level) = (q11 - q12)/0.055;
  der(B5_level) = (q12 - q15 - mEvap/rho)/0.06;
  der(B6_level) = (mCond/rho - qP2)/0.05;
  der(B7_level) = (q15 - qP1)/0.05;

  mB3 = max(rho*0.05*B3_level, 1e-6);
  mB4 = max(rho*0.055*B4_level, 1e-6);
  mB5 = max(rho*0.06*B5_level, 1e-6);
  mB6 = max(rho*0.05*B6_level, 1e-6);
  mB7 = max(rho*0.05*B7_level, 1e-6);
  wB4 = B4_saltMass/mB4;
  wB5 = B5_saltMass/mB5;

  der(B3_saltMass) = rho*q9*0.25 - rho*q11*B3_w_NaCl;
  der(B4_saltMass) = rho*q11*B3_w_NaCl - rho*q12*wB4;
  der(B5_saltMass) = rho*q12*wB4 - rho*q15*wB5;

  B3_w_NaCl = B3_saltMass/mB3;
  B5_w_NaCl = wB5;

  der(B5_temp) = QB5/(max(mB5,1e-6)*cp);
  der(B6_temp) = ((mCond*cp*(B5_temp - B6_temp)) + QB6)/(max(mB6,1e-6)*cp);
  der(B7_temp) = QB7/(max(mB7,1e-6)*cp);

  condenserDeltaT = max(B5_temp - TcoolingWater, 0);
  coolingWaterCp = cp;
  condenserHeatRemoval = mCond*hVap + mCond*coolingWaterCp*condenserDeltaT;
  FIS801_kg_s = if controller.heaterB5 then max(0.10, condenserHeatRemoval/(coolingWaterCp*max(condenserDeltaT, 1))) else 0.10;

  connect(startSrc.y, controller.startEnable) annotation(Line(points={{-159,160},{-40,160},{-40,150},{-10,150}}, color={255,0,255}));
  connect(availSrc.y, controller.B3_available) annotation(Line(points={{-159,130},{-50,130},{-50,140},{-10,140}}, color={255,0,255}));
  connect(lis301.y, controller.LIS_301) annotation(Line(points={{-79,80},{-50,80},{-50,134},{-10,134}}, color={0,0,127}));
  connect(qi302.y, controller.QI_302) annotation(Line(points={{-79,50},{-54,50},{-54,124},{-10,124}}, color={0,0,127}));
  connect(lis501.y, controller.LIS_501) annotation(Line(points={{-79,20},{-58,20},{-58,114},{-10,114}}, color={0,0,127}));
  connect(qis502.y, controller.QIS_502) annotation(Line(points={{-79,-10},{-62,-10},{-62,104},{-10,104}}, color={0,0,127}));
  connect(tis602.y, controller.TIS_602) annotation(Line(points={{-79,-40},{-66,-40},{-66,94},{-10,94}}, color={0,0,127}));
  connect(tis702.y, controller.TIS_702) annotation(Line(points={{-79,-70},{-70,-70},{-70,84},{-10,84}}, color={0,0,127}));
  connect(fis801.y, controller.FIS_801) annotation(Line(points={{-79,-100},{-74,-100},{-74,74},{-10,74}}, color={0,0,127}));
  connect(lis601.y, controller.LIS_601) annotation(Line(points={{-79,-130},{-78,-130},{-78,64},{-10,64}}, color={0,0,127}));
  connect(lis701.y, controller.LIS_701) annotation(Line(points={{-79,-160},{-82,-160},{-82,54},{-10,54}}, color={0,0,127}));

  time_s = time;
  controller_state = controller.controller_state;
  region = controller.region;
  B3_level_m = B3_level;
  B4_level_m = B4_level;
  B5_level_m = B5_level;
  B6_level_m = B6_level;
  B7_level_m = B7_level;
  B5_temp_C = B5_temp - 273.15;
  B6_temp_C = B6_temp - 273.15;
  B7_temp_C = B7_temp - 273.15;
  P1_cmd = if controller.P1 then 1 else 0;
  P2_cmd = if controller.P2 then 1 else 0;
  B5_heater_cmd = if controller.heaterB5 then 1 else 0;
  B6_cooler_cmd = if controller.coolerB6 then 1 else 0;
  B7_cooler_cmd = if controller.coolerB7 then 1 else 0;
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
annotation(
  experiment(StartTime=0, StopTime=3000, Tolerance=1e-6, Interval=5),
  Diagram(graphics={Rectangle(extent={{-180,20},{-140,60}}, lineColor={0,127,255}),Text(extent={{-178,62},{-142,76}}, textString="B1"),Rectangle(extent={{-180,-20},{-140,20}}, lineColor={0,127,255}),Text(extent={{-178,22},{-142,36}}, textString="B2"),Rectangle(extent={{-100,0},{-60,40}}, lineColor={0,127,255}),Text(extent={{-98,42},{-62,56}}, textString="B3"),Rectangle(extent={{-20,0},{20,40}}, lineColor={0,127,255}),Text(extent={{-18,42},{18,56}}, textString="B4"),Rectangle(extent={{60,0},{100,40}}, lineColor={0,127,255}),Text(extent={{62,42},{98,56}}, textString="B5"),Rectangle(extent={{140,40},{180,80}}, lineColor={0,127,255}),Text(extent={{142,82},{178,96}}, textString="B6"),Rectangle(extent={{140,-40},{180,0}}, lineColor={0,127,255}),Text(extent={{142,2},{178,16}}, textString="B7"),Text(extent={{108,18},{132,32}}, textString="K1")}),
  Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end NaClBatchPlantSystem;
