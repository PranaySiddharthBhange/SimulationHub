within;
block NaClBatchController
  import Modelica.Units.SI;

  type MainState = enumeration(
      Initial,
      Step1_Charge_B1_to_B3,
      Step2_Charge_B2_to_B3,
      Step3_Transfer_B3_to_B4,
      Step4_Wait_B5_Idle,
      Step5_Transfer_B4_to_B5,
      Step6_Evaporate_B5,
      JoinWait);
  type BranchAState = enumeration(A_Idle, Step12_Cool_B6, Step13_Return_B6_to_B1, A_Complete);
  type BranchBState = enumeration(B_Idle, Step7_Wait_Branch_B_Ready, Step8_Transfer_B5_to_B7, Step9_Cool_B7, Step10_11_Return_B7_to_B2, B_Complete);

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,90},{-100,110}}), iconTransformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,70},{-100,90}}), iconTransformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301_m annotation(Placement(transformation(extent={{-120,50},{-100,70}}), iconTransformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput QI_302_kg_per_kg annotation(Placement(transformation(extent={{-120,30},{-100,50}}), iconTransformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501_m annotation(Placement(transformation(extent={{-120,10},{-100,30}}), iconTransformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502_kg_per_kg annotation(Placement(transformation(extent={{-120,-10},{-100,10}}), iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602_degC annotation(Placement(transformation(extent={{-120,-30},{-100,-10}}), iconTransformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702_degC annotation(Placement(transformation(extent={{-120,-50},{-100,-30}}), iconTransformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801_kg_per_s annotation(Placement(transformation(extent={{-120,-70},{-100,-50}}), iconTransformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601_m annotation(Placement(transformation(extent={{-120,-90},{-100,-70}}), iconTransformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701_m annotation(Placement(transformation(extent={{-120,-110},{-100,-90}}), iconTransformation(extent={{-120,-110},{-100,-90}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1_open annotation(Placement(transformation(extent={{100,90},{120,110}}), iconTransformation(extent={{100,90},{120,110}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3_open annotation(Placement(transformation(extent={{100,78},{120,98}}), iconTransformation(extent={{100,78},{120,98}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5_open annotation(Placement(transformation(extent={{100,66},{120,86}}), iconTransformation(extent={{100,66},{120,86}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6_open annotation(Placement(transformation(extent={{100,54},{120,74}}), iconTransformation(extent={{100,54},{120,74}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8_open annotation(Placement(transformation(extent={{100,42},{120,62}}), iconTransformation(extent={{100,42},{120,62}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9_open annotation(Placement(transformation(extent={{100,30},{120,50}}), iconTransformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11_open annotation(Placement(transformation(extent={{100,18},{120,38}}), iconTransformation(extent={{100,18},{120,38}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12_open annotation(Placement(transformation(extent={{100,6},{120,26}}), iconTransformation(extent={{100,6},{120,26}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15_open annotation(Placement(transformation(extent={{100,-6},{120,14}}), iconTransformation(extent={{100,-6},{120,14}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18_open annotation(Placement(transformation(extent={{100,-18},{120,2}}), iconTransformation(extent={{100,-18},{120,2}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20_open annotation(Placement(transformation(extent={{100,-30},{120,-10}}), iconTransformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22_open annotation(Placement(transformation(extent={{100,-42},{120,-22}}), iconTransformation(extent={{100,-42},{120,-22}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23_open annotation(Placement(transformation(extent={{100,-54},{120,-34}}), iconTransformation(extent={{100,-54},{120,-34}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24_open annotation(Placement(transformation(extent={{100,-66},{120,-46}}), iconTransformation(extent={{100,-66},{120,-46}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25_open annotation(Placement(transformation(extent={{100,-78},{120,-58}}), iconTransformation(extent={{100,-78},{120,-58}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1_on annotation(Placement(transformation(extent={{100,-90},{120,-70}}), iconTransformation(extent={{100,-90},{120,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2_on annotation(Placement(transformation(extent={{100,-102},{120,-82}}), iconTransformation(extent={{100,-102},{120,-82}})));
  Modelica.Blocks.Interfaces.BooleanOutput T5_Heater annotation(Placement(transformation(extent={{100,-114},{120,-94}}), iconTransformation(extent={{100,-114},{120,-94}})));
  Modelica.Blocks.Interfaces.BooleanOutput B6_cooler_on annotation(Placement(transformation(extent={{100,-126},{120,-106}}), iconTransformation(extent={{100,-126},{120,-106}})));
  Modelica.Blocks.Interfaces.BooleanOutput B7_cooler_on annotation(Placement(transformation(extent={{100,-138},{120,-118}}), iconTransformation(extent={{100,-138},{120,-118}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state annotation(Placement(transformation(extent={{100,-150},{120,-130}}), iconTransformation(extent={{100,-150},{120,-130}})));
  Modelica.Blocks.Interfaces.IntegerOutput region annotation(Placement(transformation(extent={{100,-162},{120,-142}}), iconTransformation(extent={{100,-162},{120,-142}})));

protected 
  discrete MainState mainState(start=MainState.Initial, fixed=true);
  discrete BranchAState branchAState(start=BranchAState.A_Idle, fixed=true);
  discrete BranchBState branchBState(start=BranchBState.B_Idle, fixed=true);
  Boolean startPulse;
  Boolean branchStartCond;
  Boolean branchAComplete;
  Boolean branchBComplete;
  Boolean heaterPermissive;

equation 
  startPulse = edge(startEnable);
  branchStartCond = QIS_502_kg_per_kg >= 0.180;
  branchAComplete = branchAState == BranchAState.A_Complete;
  branchBComplete = branchBState == BranchBState.B_Complete;
  heaterPermissive = LIS_501_m >= 0.05 and FIS_801_kg_per_s >= 0.10;

  V8_open = mainState == MainState.Step1_Charge_B1_to_B3;
  V9_open = mainState == MainState.Step2_Charge_B2_to_B3;
  V11_open = mainState == MainState.Step3_Transfer_B3_to_B4;
  V12_open = mainState == MainState.Step5_Transfer_B4_to_B5;
  T5_Heater = mainState == MainState.Step6_Evaporate_B5 and heaterPermissive;

  B6_cooler_on = branchAState == BranchAState.Step12_Cool_B6;
  P2_on = branchAState == BranchAState.Step13_Return_B6_to_B1 and LIS_601_m > 0.02;
  V20_open = branchAState == BranchAState.Step13_Return_B6_to_B1;
  V24_open = branchAState == BranchAState.Step13_Return_B6_to_B1;
  V25_open = branchAState == BranchAState.Step13_Return_B6_to_B1;
  V1_open = branchAState == BranchAState.Step13_Return_B6_to_B1;
  V3_open = branchAState == BranchAState.Step13_Return_B6_to_B1;

  V15_open = branchBState == BranchBState.Step8_Transfer_B5_to_B7;
  B7_cooler_on = branchBState == BranchBState.Step9_Cool_B7;
  P1_on = branchBState == BranchBState.Step10_11_Return_B7_to_B2 and LIS_701_m > 0.02;
  V18_open = branchBState == BranchBState.Step10_11_Return_B7_to_B2;
  V23_open = branchBState == BranchBState.Step10_11_Return_B7_to_B2;
  V22_open = branchBState == BranchBState.Step10_11_Return_B7_to_B2;
  V5_open = branchBState == BranchBState.Step10_11_Return_B7_to_B2;
  V6_open = branchBState == BranchBState.Step10_11_Return_B7_to_B2;

  controller_state = Integer(mainState);
  region = if mainState == MainState.JoinWait then 3 else if mainState == MainState.Step6_Evaporate_B5 then 2 else 1;

algorithm 
  when {startPulse,
        pre(mainState) == MainState.Step1_Charge_B1_to_B3 and LIS_301_m >= 0.13,
        pre(mainState) == MainState.Step2_Charge_B2_to_B3 and QI_302_kg_per_kg >= 0.080,
        pre(mainState) == MainState.Step3_Transfer_B3_to_B4 and LIS_301_m < 0.01,
        pre(mainState) == MainState.Step4_Wait_B5_Idle and LIS_501_m < 0.01 and not pre(V15_open),
        pre(mainState) == MainState.Step5_Transfer_B4_to_B5 and LIS_501_m >= 0.18,
        pre(mainState) == MainState.Step6_Evaporate_B5 and QIS_502_kg_per_kg >= 0.180,
        pre(mainState) == MainState.JoinWait and branchAComplete and branchBComplete and time > 2500} then
    if startPulse and pre(mainState) == MainState.Initial and B3_available then
      mainState := MainState.Step1_Charge_B1_to_B3;
    elseif pre(mainState) == MainState.Step1_Charge_B1_to_B3 and LIS_301_m >= 0.13 then
      mainState := MainState.Step2_Charge_B2_to_B3;
    elseif pre(mainState) == MainState.Step2_Charge_B2_to_B3 and QI_302_kg_per_kg >= 0.080 then
      mainState := MainState.Step3_Transfer_B3_to_B4;
    elseif pre(mainState) == MainState.Step3_Transfer_B3_to_B4 and LIS_301_m < 0.01 then
      mainState := MainState.Step4_Wait_B5_Idle;
    elseif pre(mainState) == MainState.Step4_Wait_B5_Idle and LIS_501_m < 0.01 and not pre(V15_open) then
      mainState := MainState.Step5_Transfer_B4_to_B5;
    elseif pre(mainState) == MainState.Step5_Transfer_B4_to_B5 and LIS_501_m >= 0.18 then
      mainState := MainState.Step6_Evaporate_B5;
    elseif pre(mainState) == MainState.Step6_Evaporate_B5 and QIS_502_kg_per_kg >= 0.180 then
      mainState := MainState.JoinWait;
    elseif pre(mainState) == MainState.JoinWait and branchAComplete and branchBComplete and time > 2500 then
      mainState := MainState.Initial;
      branchAState := BranchAState.A_Idle;
      branchBState := BranchBState.B_Idle;
    end if;
  end when;

  when {pre(branchAState) == BranchAState.A_Idle and branchStartCond,
        pre(branchAState) == BranchAState.Step12_Cool_B6 and TIS_602_degC <= 20,
        pre(branchAState) == BranchAState.Step13_Return_B6_to_B1 and LIS_601_m <= 0.02} then
    if pre(branchAState) == BranchAState.A_Idle and branchStartCond then
      branchAState := BranchAState.Step12_Cool_B6;
    elseif pre(branchAState) == BranchAState.Step12_Cool_B6 and TIS_602_degC <= 20 then
      branchAState := BranchAState.Step13_Return_B6_to_B1;
    elseif pre(branchAState) == BranchAState.Step13_Return_B6_to_B1 and LIS_601_m <= 0.02 then
      branchAState := BranchAState.A_Complete;
    end if;
  end when;

  when {pre(branchBState) == BranchBState.B_Idle and branchStartCond,
        pre(branchBState) == BranchBState.Step7_Wait_Branch_B_Ready and LIS_701_m < 0.01,
        pre(branchBState) == BranchBState.Step8_Transfer_B5_to_B7 and LIS_501_m < 0.01,
        pre(branchBState) == BranchBState.Step9_Cool_B7 and TIS_702_degC <= 25,
        pre(branchBState) == BranchBState.Step10_11_Return_B7_to_B2 and LIS_701_m <= 0.02} then
    if pre(branchBState) == BranchBState.B_Idle and branchStartCond then
      branchBState := BranchBState.Step7_Wait_Branch_B_Ready;
    elseif pre(branchBState) == BranchBState.Step7_Wait_Branch_B_Ready and LIS_701_m < 0.01 then
      branchBState := BranchBState.Step8_Transfer_B5_to_B7;
    elseif pre(branchBState) == BranchBState.Step8_Transfer_B5_to_B7 and LIS_501_m < 0.01 then
      branchBState := BranchBState.Step9_Cool_B7;
    elseif pre(branchBState) == BranchBState.Step9_Cool_B7 and TIS_702_degC <= 25 then
      branchBState := BranchBState.Step10_11_Return_B7_to_B2;
    elseif pre(branchBState) == BranchBState.Step10_11_Return_B7_to_B2 and LIS_701_m <= 0.02 then
      branchBState := BranchBState.B_Complete;
    end if;
  end when;

  annotation(
    Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),
                   Text(extent={{-90,60},{90,90}}, textString="Controller"),
                   Text(extent={{-94,30},{-20,46}}, textString="inputs"),
                   Text(extent={{18,30},{92,46}}, textString="commands"),
                   Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255})}));
end NaClBatchController;
