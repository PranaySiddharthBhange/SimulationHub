model BatchSequenceController
  type MainMode = enumeration(Initial, Step1_Charge_B1_to_B3, Step2_Charge_B2_to_B3, Step3_Transfer_B3_to_B4, Step4_Wait_B5_Idle, Step5_Transfer_B4_to_B5, Step6_Evaporate_B5, JoinWait);
  type BranchAMode = enumeration(A_Idle, Step12_Cool_B6, Step13_Return_B6_to_B1, A_Complete);
  type BranchBMode = enumeration(B_Idle, Step7_Wait_Branch_B_Ready, Step8_Transfer_B5_to_B7, Step9_Cool_B7, Step10_11_Return_B7_to_B2, B_Complete);

  parameter Modelica.Units.SI.Height B3_fillLevel = 0.13;
  parameter Real B3_targetX = 0.080;
  parameter Modelica.Units.SI.Height B3_emptyLevel = 0.01;
  parameter Modelica.Units.SI.Height B5_idleLevel = 0.01;
  parameter Modelica.Units.SI.Height B5_fillLevel = 0.18;
  parameter Real B5_targetX = 0.180;
  parameter Modelica.Units.SI.Height B5_heaterMinLevel = 0.05;
  parameter Modelica.Units.SI.MassFlowRate FIS801_minFlow = 0.10;
  parameter Modelica.Units.SI.Temperature B6_coolTargetK = 293.15;
  parameter Modelica.Units.SI.Temperature B7_coolTargetK = 298.15;
  parameter Modelica.Units.SI.Time restartEarliest = 2500;
  parameter Boolean B3_available = true;

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Interfaces.RealInput LIS301 annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput QI302 annotation(Placement(transformation(extent={{-120,35},{-100,55}})));
  Modelica.Blocks.Interfaces.RealInput LIS501 annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput QIS502 annotation(Placement(transformation(extent={{-120,-15},{-100,5}})));
  Modelica.Blocks.Interfaces.RealInput TIS602 annotation(Placement(transformation(extent={{-120,-40},{-100,-20}})));
  Modelica.Blocks.Interfaces.RealInput TIS702 annotation(Placement(transformation(extent={{-120,-65},{-100,-45}})));
  Modelica.Blocks.Interfaces.RealInput FIS801 annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.RealInput LIS601 annotation(Placement(transformation(extent={{-120,-115},{-100,-95}})));
  Modelica.Blocks.Interfaces.RealInput LIS701 annotation(Placement(transformation(extent={{-120,-140},{-100,-120}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1_open annotation(Placement(transformation(extent={{100,100},{120,120}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3_open annotation(Placement(transformation(extent={{100,88},{120,108}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5_open annotation(Placement(transformation(extent={{100,76},{120,96}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6_open annotation(Placement(transformation(extent={{100,64},{120,84}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8_open annotation(Placement(transformation(extent={{100,52},{120,72}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9_open annotation(Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11_open annotation(Placement(transformation(extent={{100,28},{120,48}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12_open annotation(Placement(transformation(extent={{100,16},{120,36}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15_open annotation(Placement(transformation(extent={{100,4},{120,24}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18_open annotation(Placement(transformation(extent={{100,-8},{120,12}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20_open annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22_open annotation(Placement(transformation(extent={{100,-32},{120,-12}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23_open annotation(Placement(transformation(extent={{100,-44},{120,-24}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24_open annotation(Placement(transformation(extent={{100,-56},{120,-36}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25_open annotation(Placement(transformation(extent={{100,-68},{120,-48}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1_on annotation(Placement(transformation(extent={{100,-80},{120,-60}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2_on annotation(Placement(transformation(extent={{100,-92},{120,-72}})));
  Modelica.Blocks.Interfaces.BooleanOutput B5_heater_on annotation(Placement(transformation(extent={{100,-104},{120,-84}})));
  Modelica.Blocks.Interfaces.BooleanOutput B6_cooler_on annotation(Placement(transformation(extent={{100,-116},{120,-96}})));
  Modelica.Blocks.Interfaces.BooleanOutput B7_cooler_on annotation(Placement(transformation(extent={{100,-128},{120,-108}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state annotation(Placement(transformation(extent={{100,-140},{120,-120}})));
  Modelica.Blocks.Interfaces.IntegerOutput region annotation(Placement(transformation(extent={{100,-152},{120,-132}})));

protected
  discrete MainMode mainMode(start=MainMode.Initial, fixed=true);
  discrete BranchAMode branchAMode(start=BranchAMode.A_Idle, fixed=true);
  discrete BranchBMode branchBMode(start=BranchBMode.B_Idle, fixed=true);
  Boolean startPulse;
  Boolean branchAComplete;
  Boolean branchBComplete;
equation
  startPulse = edge(startEnable);

  branchAComplete = branchAMode == BranchAMode.A_Complete;
  branchBComplete = branchBMode == BranchBMode.B_Complete;

  V8_open = mainMode == MainMode.Step1_Charge_B1_to_B3;
  V9_open = mainMode == MainMode.Step2_Charge_B2_to_B3;
  V11_open = mainMode == MainMode.Step3_Transfer_B3_to_B4;
  V12_open = mainMode == MainMode.Step5_Transfer_B4_to_B5;
  V15_open = branchBMode == BranchBMode.Step8_Transfer_B5_to_B7;

  B6_cooler_on = branchAMode == BranchAMode.Step12_Cool_B6;
  B7_cooler_on = branchBMode == BranchBMode.Step9_Cool_B7;

  P2_on = branchAMode == BranchAMode.Step13_Return_B6_to_B1 and LIS601 > 0.02;
  V20_open = P2_on;
  V24_open = P2_on;
  V25_open = P2_on;
  V1_open = P2_on;
  V3_open = P2_on;

  P1_on = branchBMode == BranchBMode.Step10_11_Return_B7_to_B2 and LIS701 > 0.02;
  V18_open = P1_on;
  V23_open = P1_on;
  V22_open = P1_on;
  V5_open = P1_on;
  V6_open = P1_on;

  B5_heater_on = mainMode == MainMode.Step6_Evaporate_B5 and LIS501 >= B5_heaterMinLevel and FIS801 >= FIS801_minFlow;

  controller_state = Integer(mainMode);
  region = if mainMode == MainMode.JoinWait then 3 else if mainMode == MainMode.Step6_Evaporate_B5 then 2 else 1;
algorithm
  when {startPulse,
        pre(mainMode) == MainMode.Step1_Charge_B1_to_B3 and LIS301 >= B3_fillLevel,
        pre(mainMode) == MainMode.Step2_Charge_B2_to_B3 and QI302 >= B3_targetX,
        pre(mainMode) == MainMode.Step3_Transfer_B3_to_B4 and LIS301 < B3_emptyLevel,
        pre(mainMode) == MainMode.Step4_Wait_B5_Idle and LIS501 < B5_idleLevel and pre(branchBMode) <> BranchBMode.Step8_Transfer_B5_to_B7,
        pre(mainMode) == MainMode.Step5_Transfer_B4_to_B5 and LIS501 >= B5_fillLevel,
        pre(mainMode) == MainMode.Step6_Evaporate_B5 and QIS502 >= B5_targetX,
        pre(mainMode) == MainMode.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > restartEarliest} then
    if startPulse and pre(mainMode) == MainMode.Initial and B3_available then
      mainMode := MainMode.Step1_Charge_B1_to_B3;
    elseif pre(mainMode) == MainMode.Step1_Charge_B1_to_B3 and LIS301 >= B3_fillLevel then
      mainMode := MainMode.Step2_Charge_B2_to_B3;
    elseif pre(mainMode) == MainMode.Step2_Charge_B2_to_B3 and QI302 >= B3_targetX then
      mainMode := MainMode.Step3_Transfer_B3_to_B4;
    elseif pre(mainMode) == MainMode.Step3_Transfer_B3_to_B4 and LIS301 < B3_emptyLevel then
      mainMode := MainMode.Step4_Wait_B5_Idle;
    elseif pre(mainMode) == MainMode.Step4_Wait_B5_Idle and LIS501 < B5_idleLevel and pre(branchBMode) <> BranchBMode.Step8_Transfer_B5_to_B7 then
      mainMode := MainMode.Step5_Transfer_B4_to_B5;
    elseif pre(mainMode) == MainMode.Step5_Transfer_B4_to_B5 and LIS501 >= B5_fillLevel then
      mainMode := MainMode.Step6_Evaporate_B5;
    elseif pre(mainMode) == MainMode.Step6_Evaporate_B5 and QIS502 >= B5_targetX then
      mainMode := MainMode.JoinWait;
    elseif pre(mainMode) == MainMode.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > restartEarliest then
      mainMode := MainMode.Initial;
      branchAMode := BranchAMode.A_Idle;
      branchBMode := BranchBMode.B_Idle;
    end if;
  end when;

  when {pre(branchAMode) == BranchAMode.A_Idle and pre(mainMode) == MainMode.JoinWait,
        pre(branchAMode) == BranchAMode.Step12_Cool_B6 and TIS602 <= B6_coolTargetK,
        pre(branchAMode) == BranchAMode.Step13_Return_B6_to_B1 and LIS601 <= 0.02} then
    if pre(branchAMode) == BranchAMode.A_Idle and pre(mainMode) == MainMode.JoinWait then
      branchAMode := BranchAMode.Step12_Cool_B6;
    elseif pre(branchAMode) == BranchAMode.Step12_Cool_B6 and TIS602 <= B6_coolTargetK then
      branchAMode := BranchAMode.Step13_Return_B6_to_B1;
    elseif pre(branchAMode) == BranchAMode.Step13_Return_B6_to_B1 and LIS601 <= 0.02 then
      branchAMode := BranchAMode.A_Complete;
    end if;
  end when;

  when {pre(branchBMode) == BranchBMode.B_Idle and pre(mainMode) == MainMode.JoinWait,
        pre(branchBMode) == BranchBMode.Step7_Wait_Branch_B_Ready and LIS701 < 0.01,
        pre(branchBMode) == BranchBMode.Step8_Transfer_B5_to_B7 and LIS501 < B5_idleLevel,
        pre(branchBMode) == BranchBMode.Step9_Cool_B7 and TIS702 <= B7_coolTargetK,
        pre(branchBMode) == BranchBMode.Step10_11_Return_B7_to_B2 and LIS701 <= 0.02} then
    if pre(branchBMode) == BranchBMode.B_Idle and pre(mainMode) == MainMode.JoinWait then
      branchBMode := BranchBMode.Step7_Wait_Branch_B_Ready;
    elseif pre(branchBMode) == BranchBMode.Step7_Wait_Branch_B_Ready and LIS701 < 0.01 then
      branchBMode := BranchBMode.Step8_Transfer_B5_to_B7;
    elseif pre(branchBMode) == BranchBMode.Step8_Transfer_B5_to_B7 and LIS501 < B5_idleLevel then
      branchBMode := BranchBMode.Step9_Cool_B7;
    elseif pre(branchBMode) == BranchBMode.Step9_Cool_B7 and TIS702 <= B7_coolTargetK then
      branchBMode := BranchBMode.Step10_11_Return_B7_to_B2;
    elseif pre(branchBMode) == BranchBMode.Step10_11_Return_B7_to_B2 and LIS701 <= 0.02 then
      branchBMode := BranchBMode.B_Complete;
    end if;
  end when;
annotation(
  Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),
                 Text(extent={{-90,30},{90,80}}, textString="Controller"),
                 Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255})}));
end BatchSequenceController;
