within ;
block NaClController
  type MainState = enumeration(Initial, Step1, Step2, Step3, Step4, Step5, Step6, JoinWait);
  type BranchAState = enumeration(A_Idle, Step12, Step13, A_Complete);
  type BranchBState = enumeration(B_Idle, Step7, Step8, Step9, Step10_11, B_Complete);

  parameter Modelica.Units.SI.Time restartTime_s = 2500;

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,80},{-100,100}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301_m annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput QI_302_kgkg annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501_m annotation(Placement(transformation(extent={{-120,-40},{-100,-20}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502_kgkg annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602_degC annotation(Placement(transformation(extent={{-120,-100},{-100,-80}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702_degC annotation(Placement(transformation(extent={{-120,-130},{-100,-110}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801_kgs annotation(Placement(transformation(extent={{-20,120},{0,140}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601_m annotation(Placement(transformation(extent={{20,120},{40,140}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701_m annotation(Placement(transformation(extent={{60,120},{80,140}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1_open annotation(Placement(transformation(extent={{100,110},{120,130}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3_open annotation(Placement(transformation(extent={{100,95},{120,115}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5_open annotation(Placement(transformation(extent={{100,80},{120,100}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6_open annotation(Placement(transformation(extent={{100,65},{120,85}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8_open annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9_open annotation(Placement(transformation(extent={{100,35},{120,55}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11_open annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12_open annotation(Placement(transformation(extent={{100,5},{120,25}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15_open annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18_open annotation(Placement(transformation(extent={{100,-25},{120,-5}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20_open annotation(Placement(transformation(extent={{100,-40},{120,-20}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22_open annotation(Placement(transformation(extent={{100,-55},{120,-35}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23_open annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24_open annotation(Placement(transformation(extent={{100,-85},{120,-65}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25_open annotation(Placement(transformation(extent={{100,-100},{120,-80}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1_on annotation(Placement(transformation(extent={{100,-115},{120,-95}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2_on annotation(Placement(transformation(extent={{100,-130},{120,-110}})));
  Modelica.Blocks.Interfaces.BooleanOutput T5_Heater annotation(Placement(transformation(extent={{100,-145},{120,-125}})));
  Modelica.Blocks.Interfaces.BooleanOutput B6_cooler_on annotation(Placement(transformation(extent={{100,-160},{120,-140}})));
  Modelica.Blocks.Interfaces.BooleanOutput B7_cooler_on annotation(Placement(transformation(extent={{100,-175},{120,-155}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state annotation(Placement(transformation(extent={{100,-190},{120,-170}})));
  Modelica.Blocks.Interfaces.IntegerOutput region annotation(Placement(transformation(extent={{100,-205},{120,-185}})));

protected 
  discrete MainState mainState(start=MainState.Initial, fixed=true);
  discrete BranchAState branchAState(start=BranchAState.A_Idle, fixed=true);
  discrete BranchBState branchBState(start=BranchBState.B_Idle, fixed=true);
  Boolean startPulse;
  Boolean heaterPermissive;
  Boolean p1Permissive;
  Boolean p2Permissive;
  Boolean branchAComplete;
  Boolean branchBComplete;

equation 
  startPulse = edge(startEnable);
  heaterPermissive = LIS_501_m >= 0.05 and FIS_801_kgs >= 0.10;
  p1Permissive = LIS_701_m > 0.02;
  p2Permissive = LIS_601_m > 0.02;
  branchAComplete = branchAState == BranchAState.A_Complete;
  branchBComplete = branchBState == BranchBState.B_Complete;

  V1_open = branchAState == BranchAState.Step13;
  V3_open = branchAState == BranchAState.Step13;
  V5_open = branchBState == BranchBState.Step10_11;
  V6_open = branchBState == BranchBState.Step10_11;
  V8_open = mainState == MainState.Step1;
  V9_open = mainState == MainState.Step2;
  V11_open = mainState == MainState.Step3;
  V12_open = mainState == MainState.Step5;
  V15_open = branchBState == BranchBState.Step8;
  V18_open = branchBState == BranchBState.Step10_11;
  V20_open = branchAState == BranchAState.Step13;
  V22_open = branchBState == BranchBState.Step10_11;
  V23_open = branchBState == BranchBState.Step10_11;
  V24_open = branchAState == BranchAState.Step13;
  V25_open = branchAState == BranchAState.Step13;
  P1_on = branchBState == BranchBState.Step10_11 and p1Permissive;
  P2_on = branchAState == BranchAState.Step13 and p2Permissive;
  T5_Heater = mainState == MainState.Step6 and heaterPermissive;
  B6_cooler_on = branchAState == BranchAState.Step12;
  B7_cooler_on = branchBState == BranchBState.Step9;
  controller_state = Integer(mainState);
  region = if mainState == MainState.JoinWait then 3 else if Integer(branchAState) > 1 and Integer(branchBState) > 1 then 2 else 1;

algorithm 
  when {startPulse,
        pre(mainState) == MainState.Step1 and LIS_301_m >= 0.13,
        pre(mainState) == MainState.Step2 and QI_302_kgkg >= 0.080,
        pre(mainState) == MainState.Step3 and LIS_301_m < 0.01,
        pre(mainState) == MainState.Step4 and LIS_501_m < 0.01 and not pre(V15_open),
        pre(mainState) == MainState.Step5 and LIS_501_m >= 0.18,
        pre(mainState) == MainState.Step6 and QIS_502_kgkg >= 0.180,
        pre(mainState) == MainState.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > restartTime_s,
        pre(branchAState) == BranchAState.Step12 and TIS_602_degC <= 20,
        pre(branchAState) == BranchAState.Step13 and LIS_601_m <= 0.02,
        pre(branchBState) == BranchBState.Step7 and LIS_701_m < 0.01,
        pre(branchBState) == BranchBState.Step8 and LIS_501_m < 0.01,
        pre(branchBState) == BranchBState.Step9 and TIS_702_degC <= 25,
        pre(branchBState) == BranchBState.Step10_11 and LIS_701_m <= 0.02} then
    if startPulse and pre(mainState) == MainState.Initial and B3_available then
      mainState := MainState.Step1;
      branchAState := BranchAState.A_Idle;
      branchBState := BranchBState.B_Idle;
    elseif pre(mainState) == MainState.Step1 and LIS_301_m >= 0.13 then
      mainState := MainState.Step2;
    elseif pre(mainState) == MainState.Step2 and QI_302_kgkg >= 0.080 then
      mainState := MainState.Step3;
    elseif pre(mainState) == MainState.Step3 and LIS_301_m < 0.01 then
      mainState := MainState.Step4;
    elseif pre(mainState) == MainState.Step4 and LIS_501_m < 0.01 and not pre(V15_open) then
      mainState := MainState.Step5;
    elseif pre(mainState) == MainState.Step5 and LIS_501_m >= 0.18 then
      mainState := MainState.Step6;
      branchAState := BranchAState.A_Idle;
      branchBState := BranchBState.B_Idle;
    elseif pre(mainState) == MainState.Step6 and QIS_502_kgkg >= 0.180 then
      mainState := MainState.JoinWait;
      branchAState := BranchAState.Step12;
      branchBState := BranchBState.Step7;
    elseif pre(branchAState) == BranchAState.Step12 and TIS_602_degC <= 20 then
      branchAState := BranchAState.Step13;
    elseif pre(branchAState) == BranchAState.Step13 and LIS_601_m <= 0.02 then
      branchAState := BranchAState.A_Complete;
    elseif pre(branchBState) == BranchBState.Step7 and LIS_701_m < 0.01 then
      branchBState := BranchBState.Step8;
    elseif pre(branchBState) == BranchBState.Step8 and LIS_501_m < 0.01 then
      branchBState := BranchBState.Step9;
    elseif pre(branchBState) == BranchBState.Step9 and TIS_702_degC <= 25 then
      branchBState := BranchBState.Step10_11;
    elseif pre(branchBState) == BranchBState.Step10_11 and LIS_701_m <= 0.02 then
      branchBState := BranchBState.B_Complete;
    elseif pre(mainState) == MainState.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > restartTime_s then
      mainState := MainState.Initial;
      branchAState := BranchAState.A_Idle;
      branchBState := BranchBState.B_Idle;
    end if;
  end when;

annotation(
  Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),Text(extent={{-90,20},{90,80}}, textString="Controller"),Text(extent={{-90,-20},{90,20}}, textString="NaCl Batch"),Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255})}));
end NaClController;
