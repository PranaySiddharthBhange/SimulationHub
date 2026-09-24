within ;
block NaClBranchController
  type MainMode = enumeration(Initial, Step1, Step2, Step3, Step4, Step5, Step6, JoinWait);
  type BranchAMode = enumeration(A_Idle, Step12, Step13, A_Complete);
  type BranchBMode = enumeration(B_Idle, Step7, Step8, Step9, Step10_11, B_Complete);

  parameter Modelica.Units.SI.Time restartTime_s = 2500;

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301_m annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput QI_302_kgkg annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501_m annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502_kgkg annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602_degC annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702_degC annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801_kg_s annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601_m annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701_m annotation(Placement(transformation(extent={{-120,-110},{-100,-90}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1_open annotation(Placement(transformation(extent={{100,90},{120,110}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3_open annotation(Placement(transformation(extent={{100,78},{120,98}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5_open annotation(Placement(transformation(extent={{100,66},{120,86}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6_open annotation(Placement(transformation(extent={{100,54},{120,74}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8_open annotation(Placement(transformation(extent={{100,42},{120,62}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9_open annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11_open annotation(Placement(transformation(extent={{100,18},{120,38}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12_open annotation(Placement(transformation(extent={{100,6},{120,26}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15_open annotation(Placement(transformation(extent={{100,-6},{120,14}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18_open annotation(Placement(transformation(extent={{100,-18},{120,2}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20_open annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22_open annotation(Placement(transformation(extent={{100,-42},{120,-22}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23_open annotation(Placement(transformation(extent={{100,-54},{120,-34}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24_open annotation(Placement(transformation(extent={{100,-66},{120,-46}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25_open annotation(Placement(transformation(extent={{100,-78},{120,-58}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1_on annotation(Placement(transformation(extent={{100,-90},{120,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2_on annotation(Placement(transformation(extent={{100,-102},{120,-82}})));
  Modelica.Blocks.Interfaces.BooleanOutput T5_Heater annotation(Placement(transformation(extent={{100,-114},{120,-94}})));
  Modelica.Blocks.Interfaces.BooleanOutput B6_cooler_on annotation(Placement(transformation(extent={{100,-126},{120,-106}})));
  Modelica.Blocks.Interfaces.BooleanOutput B7_cooler_on annotation(Placement(transformation(extent={{100,-138},{120,-118}})));

  output Integer controller_state;
  output Integer region;
  output Boolean branch_A_complete;
  output Boolean branch_B_complete;

protected 
  discrete MainMode mainMode(start=MainMode.Initial, fixed=true);
  discrete BranchAMode branchAMode(start=BranchAMode.A_Idle, fixed=true);
  discrete BranchBMode branchBMode(start=BranchBMode.B_Idle, fixed=true);
algorithm 
  when {edge(startEnable), pre(mainMode) == MainMode.Step1 and LIS_301_m >= 0.13,
        pre(mainMode) == MainMode.Step2 and QI_302_kgkg >= 0.080,
        pre(mainMode) == MainMode.Step3 and LIS_301_m < 0.01,
        pre(mainMode) == MainMode.Step4 and LIS_501_m < 0.01 and not V15_open,
        pre(mainMode) == MainMode.Step5 and LIS_501_m >= 0.18,
        pre(mainMode) == MainMode.Step6 and QIS_502_kgkg >= 0.180,
        pre(mainMode) == MainMode.JoinWait and branch_A_complete and branch_B_complete and time > restartTime_s,
        pre(branchAMode) == BranchAMode.A_Idle and QIS_502_kgkg >= 0.180,
        pre(branchAMode) == BranchAMode.Step12 and TIS_602_degC <= 20,
        pre(branchAMode) == BranchAMode.Step13 and LIS_601_m <= 0.02,
        pre(branchBMode) == BranchBMode.B_Idle and QIS_502_kgkg >= 0.180,
        pre(branchBMode) == BranchBMode.Step7 and LIS_701_m < 0.01,
        pre(branchBMode) == BranchBMode.Step8 and LIS_501_m < 0.01,
        pre(branchBMode) == BranchBMode.Step9 and TIS_702_degC <= 25,
        pre(branchBMode) == BranchBMode.Step10_11 and LIS_701_m <= 0.02} then
    if edge(startEnable) and pre(mainMode) == MainMode.Initial and B3_available then
      mainMode := MainMode.Step1;
      branchAMode := BranchAMode.A_Idle;
      branchBMode := BranchBMode.B_Idle;
    elseif pre(mainMode) == MainMode.Step1 and LIS_301_m >= 0.13 then
      mainMode := MainMode.Step2;
    elseif pre(mainMode) == MainMode.Step2 and QI_302_kgkg >= 0.080 then
      mainMode := MainMode.Step3;
    elseif pre(mainMode) == MainMode.Step3 and LIS_301_m < 0.01 then
      mainMode := MainMode.Step4;
    elseif pre(mainMode) == MainMode.Step4 and LIS_501_m < 0.01 and not V15_open then
      mainMode := MainMode.Step5;
    elseif pre(mainMode) == MainMode.Step5 and LIS_501_m >= 0.18 then
      mainMode := MainMode.Step6;
    elseif pre(mainMode) == MainMode.Step6 and QIS_502_kgkg >= 0.180 then
      mainMode := MainMode.JoinWait;
    elseif pre(mainMode) == MainMode.JoinWait and branch_A_complete and branch_B_complete and time > restartTime_s then
      mainMode := MainMode.Initial;
      branchAMode := BranchAMode.A_Idle;
      branchBMode := BranchBMode.B_Idle;
    elseif pre(branchAMode) == BranchAMode.A_Idle and QIS_502_kgkg >= 0.180 then
      branchAMode := BranchAMode.Step12;
    elseif pre(branchAMode) == BranchAMode.Step12 and TIS_602_degC <= 20 then
      branchAMode := BranchAMode.Step13;
    elseif pre(branchAMode) == BranchAMode.Step13 and LIS_601_m <= 0.02 then
      branchAMode := BranchAMode.A_Complete;
    elseif pre(branchBMode) == BranchBMode.B_Idle and QIS_502_kgkg >= 0.180 then
      branchBMode := BranchBMode.Step7;
    elseif pre(branchBMode) == BranchBMode.Step7 and LIS_701_m < 0.01 then
      branchBMode := BranchBMode.Step8;
    elseif pre(branchBMode) == BranchBMode.Step8 and LIS_501_m < 0.01 then
      branchBMode := BranchBMode.Step9;
    elseif pre(branchBMode) == BranchBMode.Step9 and TIS_702_degC <= 25 then
      branchBMode := BranchBMode.Step10_11;
    elseif pre(branchBMode) == BranchBMode.Step10_11 and LIS_701_m <= 0.02 then
      branchBMode := BranchBMode.B_Complete;
    end if;
  end when;
equation 
  branch_A_complete = branchAMode == BranchAMode.A_Complete;
  branch_B_complete = branchBMode == BranchBMode.B_Complete;

  V1_open = branchAMode == BranchAMode.Step13;
  V3_open = branchAMode == BranchAMode.Step13;
  V5_open = branchBMode == BranchBMode.Step10_11;
  V6_open = branchBMode == BranchBMode.Step10_11;
  V8_open = mainMode == MainMode.Step1;
  V9_open = mainMode == MainMode.Step2;
  V11_open = mainMode == MainMode.Step3;
  V12_open = mainMode == MainMode.Step5;
  V15_open = branchBMode == BranchBMode.Step8;
  V18_open = branchBMode == BranchBMode.Step10_11;
  V20_open = branchAMode == BranchAMode.Step13;
  V22_open = branchBMode == BranchBMode.Step10_11;
  V23_open = branchBMode == BranchBMode.Step10_11;
  V24_open = branchAMode == BranchAMode.Step13;
  V25_open = branchAMode == BranchAMode.Step13;

  P1_on = branchBMode == BranchBMode.Step10_11 and LIS_701_m > 0.02;
  P2_on = branchAMode == BranchAMode.Step13 and LIS_601_m > 0.02;
  T5_Heater = mainMode == MainMode.Step6 and LIS_501_m >= 0.05 and FIS_801_kg_s >= 0.10;
  B6_cooler_on = branchAMode == BranchAMode.Step12;
  B7_cooler_on = branchBMode == BranchBMode.Step9;

  controller_state = if mainMode == MainMode.Initial then 0 elseif mainMode == MainMode.Step1 then 1 elseif mainMode == MainMode.Step2 then 2 elseif mainMode == MainMode.Step3 then 3 elseif mainMode == MainMode.Step4 then 4 elseif mainMode == MainMode.Step5 then 5 elseif mainMode == MainMode.Step6 then 6 else 7;
  region = if branchAMode == BranchAMode.Step12 or branchAMode == BranchAMode.Step13 or branchAMode == BranchAMode.A_Complete then 1 elseif branchBMode == BranchBMode.Step7 or branchBMode == BranchBMode.Step8 or branchBMode == BranchBMode.Step9 or branchBMode == BranchBMode.Step10_11 or branchBMode == BranchBMode.B_Complete then 2 else 0;

  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}),Text(extent={{-90,70},{90,30}}, textString="Controller"),Text(extent={{-100,100},{100,140}}, textString="%name")}), Diagram(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255})}));
end NaClBranchController;
