model NaClBatchController
  type Mode = enumeration(
    Initial,
    Step1_ChargeWater,
    Step2_ChargeBrineMix,
    Step3_BufferTransfer,
    Step4_B5IdleCheck,
    Step5_EvaporatorCharge,
    Step6_Evaporation,
    BranchA_CoolB6,
    BranchA_ReturnB6,
    BranchB_B7AvailabilityCheck,
    Step8_TransferB5toB7,
    Step9_CoolB7,
    Step10_11_ReturnB7toB2,
    JoinWait);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,94},{-100,114}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,74},{-100,94}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,26},{-100,46}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,2},{-100,22}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,-22},{-100,-2}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-46},{-100,-26}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-120,-94},{-100,-74}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-118},{-100,-98}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-142},{-100,-122}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1 annotation(Placement(transformation(extent={{100,104},{120,124}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3 annotation(Placement(transformation(extent={{100,90},{120,110}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5 annotation(Placement(transformation(extent={{100,76},{120,96}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6 annotation(Placement(transformation(extent={{100,62},{120,82}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8 annotation(Placement(transformation(extent={{100,48},{120,68}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9 annotation(Placement(transformation(extent={{100,34},{120,54}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11 annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12 annotation(Placement(transformation(extent={{100,6},{120,26}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15 annotation(Placement(transformation(extent={{100,-8},{120,12}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18 annotation(Placement(transformation(extent={{100,-22},{120,-2}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20 annotation(Placement(transformation(extent={{100,-36},{120,-16}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22 annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23 annotation(Placement(transformation(extent={{100,-64},{120,-44}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24 annotation(Placement(transformation(extent={{100,-78},{120,-58}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25 annotation(Placement(transformation(extent={{100,-92},{120,-72}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1_on annotation(Placement(transformation(extent={{100,-106},{120,-86}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2_on annotation(Placement(transformation(extent={{100,-120},{120,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput heater_B5_on annotation(Placement(transformation(extent={{100,-134},{120,-114}})));
  Modelica.Blocks.Interfaces.BooleanOutput cooler_B6_on annotation(Placement(transformation(extent={{100,-148},{120,-128}})));
  Modelica.Blocks.Interfaces.BooleanOutput cooler_B7_on annotation(Placement(transformation(extent={{100,-162},{120,-142}})));
  Modelica.Blocks.Interfaces.RealOutput controller_state annotation(Placement(transformation(extent={{100,-176},{120,-156}})));
  Modelica.Blocks.Interfaces.RealOutput region annotation(Placement(transformation(extent={{100,-190},{120,-170}})));

protected 
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchAComplete(start=false, fixed=true);
  discrete Boolean branchBComplete(start=false, fixed=true);
  Boolean startSample;
  Boolean startPulse;
equation
  startSample = sample(0, scanPeriod) and startEnable and B3_available;
  startPulse = edge(startSample);

  V1 = (mode == Mode.Step10_11_ReturnB7toB2);
  V3 = (mode == Mode.Step10_11_ReturnB7toB2);
  V5 = (mode == Mode.BranchA_ReturnB6);
  V6 = (mode == Mode.BranchA_ReturnB6);
  V8 = (mode == Mode.Step1_ChargeWater);
  V9 = (mode == Mode.Step2_ChargeBrineMix);
  V11 = (mode == Mode.Step3_BufferTransfer);
  V12 = (mode == Mode.Step5_EvaporatorCharge);
  V15 = (mode == Mode.Step8_TransferB5toB7);
  V18 = (mode == Mode.Step10_11_ReturnB7toB2);
  V20 = (mode == Mode.BranchA_ReturnB6);
  V22 = (mode == Mode.Step10_11_ReturnB7toB2);
  V23 = (mode == Mode.Step10_11_ReturnB7toB2);
  V24 = (mode == Mode.BranchA_ReturnB6);
  V25 = (mode == Mode.BranchA_ReturnB6);
  P1_on = (mode == Mode.Step10_11_ReturnB7toB2) and LIS_701 > 0.02;
  P2_on = (mode == Mode.BranchA_ReturnB6) and LIS_601 > 0.02;
  heater_B5_on = (mode == Mode.Step6_Evaporation) and LIS_501 >= 0.05 and FIS_801 >= 0.10;
  cooler_B6_on = (mode == Mode.BranchA_CoolB6);
  cooler_B7_on = (mode == Mode.Step9_CoolB7);
  controller_state = Integer(mode);
  region = if mode == Mode.BranchA_CoolB6 or mode == Mode.BranchA_ReturnB6 or mode == Mode.BranchB_B7AvailabilityCheck or mode == Mode.Step8_TransferB5toB7 or mode == Mode.Step9_CoolB7 or mode == Mode.Step10_11_ReturnB7toB2 or branchAComplete or branchBComplete or mode == Mode.JoinWait then 2 else 1;
algorithm 
  when {initial(), startPulse, pre(mode) == Mode.Step1_ChargeWater and LIS_301 >= 0.13, pre(mode) == Mode.Step2_ChargeBrineMix and QI_302 >= 0.08, pre(mode) == Mode.Step3_BufferTransfer and LIS_301 < 0.01, pre(mode) == Mode.Step4_B5IdleCheck and LIS_501 < 0.01 and not V15, pre(mode) == Mode.Step5_EvaporatorCharge and LIS_501 >= 0.18, pre(mode) == Mode.Step6_Evaporation and QIS_502 >= 0.18, pre(mode) == Mode.BranchA_CoolB6 and TIS_602 <= 20, pre(mode) == Mode.BranchA_ReturnB6 and LIS_601 <= 0.02, pre(mode) == Mode.BranchB_B7AvailabilityCheck and LIS_701 < 0.01, pre(mode) == Mode.Step8_TransferB5toB7 and LIS_501 < 0.01, pre(mode) == Mode.Step9_CoolB7 and TIS_702 <= 25, pre(mode) == Mode.Step10_11_ReturnB7toB2 and LIS_701 <= 0.02, pre(mode) == Mode.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > 2500} then
    if initial() then
      mode := Mode.Initial;
      branchAComplete := false;
      branchBComplete := false;
    elseif startPulse and pre(mode) == Mode.Initial then
      mode := Mode.Step1_ChargeWater;
      branchAComplete := false;
      branchBComplete := false;
    elseif pre(mode) == Mode.Step1_ChargeWater and LIS_301 >= 0.13 then
      mode := Mode.Step2_ChargeBrineMix;
    elseif pre(mode) == Mode.Step2_ChargeBrineMix and QI_302 >= 0.08 then
      mode := Mode.Step3_BufferTransfer;
    elseif pre(mode) == Mode.Step3_BufferTransfer and LIS_301 < 0.01 then
      mode := Mode.Step4_B5IdleCheck;
    elseif pre(mode) == Mode.Step4_B5IdleCheck and LIS_501 < 0.01 and not pre(V15) then
      mode := Mode.Step5_EvaporatorCharge;
    elseif pre(mode) == Mode.Step5_EvaporatorCharge and LIS_501 >= 0.18 then
      mode := Mode.Step6_Evaporation;
    elseif pre(mode) == Mode.Step6_Evaporation and QIS_502 >= 0.18 then
      mode := Mode.BranchA_CoolB6;
      branchAComplete := false;
      branchBComplete := false;
    elseif pre(mode) == Mode.BranchA_CoolB6 and TIS_602 <= 20 then
      mode := Mode.BranchA_ReturnB6;
    elseif pre(mode) == Mode.BranchA_ReturnB6 and LIS_601 <= 0.02 then
      branchAComplete := true;
      if pre(branchBComplete) then
        mode := Mode.JoinWait;
      else
        mode := Mode.BranchB_B7AvailabilityCheck;
      end if;
    elseif pre(mode) == Mode.BranchB_B7AvailabilityCheck and LIS_701 < 0.01 then
      mode := Mode.Step8_TransferB5toB7;
    elseif pre(mode) == Mode.Step8_TransferB5toB7 and LIS_501 < 0.01 then
      mode := Mode.Step9_CoolB7;
    elseif pre(mode) == Mode.Step9_CoolB7 and TIS_702 <= 25 then
      mode := Mode.Step10_11_ReturnB7toB2;
    elseif pre(mode) == Mode.Step10_11_ReturnB7toB2 and LIS_701 <= 0.02 then
      branchBComplete := true;
      if pre(branchAComplete) then
        mode := Mode.JoinWait;
      else
        mode := Mode.BranchA_CoolB6;
      end if;
    elseif pre(mode) == Mode.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > 2500 then
      mode := Mode.Step1_ChargeWater;
      branchAComplete := false;
      branchBComplete := false;
    end if;
  end when;

  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{-80,60},{80,-60}}, lineColor={0,0,255}, fillColor={215,215,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-70,30},{70,0}}, textString="Controller", lineColor={0,0,255}),
      Text(extent={{-70,-20},{70,-50}}, textString="State Seq", lineColor={0,0,255}),
      Text(extent={{-100,110},{100,140}}, textString="%name", lineColor={0,0,255})}),
    Diagram(graphics={Text(extent={{-90,90},{90,70}}, textString="NaCl batch sequence controller")}));
end NaClBatchController;
