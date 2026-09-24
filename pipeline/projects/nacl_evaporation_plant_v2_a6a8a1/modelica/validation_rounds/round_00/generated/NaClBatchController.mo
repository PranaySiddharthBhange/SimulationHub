model NaClBatchController
  type MainState = enumeration(Initial, Step1, Step2, Step3, Step4, Step5, Step6, JoinWait);
  type BranchAState = enumeration(A_Idle, Step12, Step13, A_Complete);
  type BranchBState = enumeration(B_Idle, Step7, Step8, Step9, Step10_11, B_Complete);
  parameter Modelica.Units.SI.Time restartTime=2500;
  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Interfaces.RealInput LIS301 annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput QI302 annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput LIS501 annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput QIS502 annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput TIS602 annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput TIS702 annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput FIS801 annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput LIS601 annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS701 annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
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
  Modelica.Blocks.Interfaces.BooleanOutput heaterOn annotation(Placement(transformation(extent={{40,-120},{60,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB6On annotation(Placement(transformation(extent={{0,-120},{20,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB7On annotation(Placement(transformation(extent={{-40,-120},{-20,-100}})));
  output Integer controller_state;
  output Integer region;
protected
  discrete MainState mainState(start=MainState.Initial, fixed=true);
  discrete BranchAState branchAState(start=BranchAState.A_Idle, fixed=true);
  discrete BranchBState branchBState(start=BranchBState.B_Idle, fixed=true);
  discrete Boolean branchAComplete(start=false, fixed=true);
  discrete Boolean branchBComplete(start=false, fixed=true);
  Boolean heaterPermissive;
  Boolean startPulse;
  Boolean b5Idle;
equation
  heaterPermissive = LIS501 >= 0.05 and FIS801 >= 0.10;
  startPulse = edge(startEnable);
  b5Idle = LIS501 < 0.01 and not pre(V15_open);
  V8_open = mainState == MainState.Step1;
  V9_open = mainState == MainState.Step2;
  V11_open = mainState == MainState.Step3;
  V12_open = mainState == MainState.Step5;
  V15_open = branchBState == BranchBState.Step8;
  coolerB6On = branchAState == BranchAState.Step12;
  coolerB7On = branchBState == BranchBState.Step9;
  heaterOn = mainState == MainState.Step6 and heaterPermissive;
  P2_on = branchAState == BranchAState.Step13 and LIS601 > 0.02;
  P1_on = branchBState == BranchBState.Step10_11 and LIS701 > 0.02;
  V20_open = P2_on;
  V24_open = P2_on;
  V25_open = P2_on;
  V1_open = P2_on;
  V3_open = P2_on;
  V18_open = P1_on;
  V22_open = P1_on;
  V23_open = P1_on;
  V5_open = P1_on;
  V6_open = P1_on;
  controller_state = Integer(mainState);
  region = if mainState == MainState.JoinWait then 3 else if mainState == MainState.Step6 then 2 else 1;
algorithm
  when {startPulse, pre(mainState) == MainState.Step1 and LIS301 >= 0.13, pre(mainState) == MainState.Step2 and QI302 >= 0.080, pre(mainState) == MainState.Step3 and LIS301 < 0.01, pre(mainState) == MainState.Step4 and b5Idle, pre(mainState) == MainState.Step5 and LIS501 >= 0.18, pre(mainState) == MainState.Step6 and QIS502 >= 0.180, pre(mainState) == MainState.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > restartTime, pre(branchAState) == BranchAState.A_Idle and QIS502 >= 0.180, pre(branchAState) == BranchAState.Step12 and TIS602 <= 20, pre(branchAState) == BranchAState.Step13 and LIS601 <= 0.02, pre(branchBState) == BranchBState.B_Idle and QIS502 >= 0.180, pre(branchBState) == BranchBState.Step7 and LIS701 < 0.01, pre(branchBState) == BranchBState.Step8 and LIS501 < 0.01, pre(branchBState) == BranchBState.Step9 and TIS702 <= 25, pre(branchBState) == BranchBState.Step10_11 and LIS701 <= 0.02} then
    if startPulse and pre(mainState) == MainState.Initial then
      mainState := MainState.Step1;
      branchAComplete := false;
      branchBComplete := false;
      branchAState := BranchAState.A_Idle;
      branchBState := BranchBState.B_Idle;
    elseif pre(mainState) == MainState.Step1 and LIS301 >= 0.13 then
      mainState := MainState.Step2;
    elseif pre(mainState) == MainState.Step2 and QI302 >= 0.080 then
      mainState := MainState.Step3;
    elseif pre(mainState) == MainState.Step3 and LIS301 < 0.01 then
      mainState := MainState.Step4;
    elseif pre(mainState) == MainState.Step4 and b5Idle then
      mainState := MainState.Step5;
    elseif pre(mainState) == MainState.Step5 and LIS501 >= 0.18 then
      mainState := MainState.Step6;
    elseif pre(mainState) == MainState.Step6 and QIS502 >= 0.180 then
      mainState := MainState.JoinWait;
    elseif pre(mainState) == MainState.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > restartTime then
      mainState := MainState.Initial;
      branchAState := BranchAState.A_Idle;
      branchBState := BranchBState.B_Idle;
      branchAComplete := false;
      branchBComplete := false;
    end if;

    if pre(branchAState) == BranchAState.A_Idle and QIS502 >= 0.180 then
      branchAState := BranchAState.Step12;
    elseif pre(branchAState) == BranchAState.Step12 and TIS602 <= 20 then
      branchAState := BranchAState.Step13;
    elseif pre(branchAState) == BranchAState.Step13 and LIS601 <= 0.02 then
      branchAState := BranchAState.A_Complete;
      branchAComplete := true;
    end if;

    if pre(branchBState) == BranchBState.B_Idle and QIS502 >= 0.180 then
      branchBState := BranchBState.Step7;
    elseif pre(branchBState) == BranchBState.Step7 and LIS701 < 0.01 then
      branchBState := BranchBState.Step8;
    elseif pre(branchBState) == BranchBState.Step8 and LIS501 < 0.01 then
      branchBState := BranchBState.Step9;
    elseif pre(branchBState) == BranchBState.Step9 and TIS702 <= 25 then
      branchBState := BranchBState.Step10_11;
    elseif pre(branchBState) == BranchBState.Step10_11 and LIS701 <= 0.02 then
      branchBState := BranchBState.B_Complete;
      branchBComplete := true;
    end if;
  end when;
  annotation(
    Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-90,20},{90,70}}, textString="Controller"), Text(extent={{-100,100},{100,130}}, textString="%name")})
  );
end NaClBatchController;
