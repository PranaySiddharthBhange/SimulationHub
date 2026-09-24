model BatchController
  type Mode = enumeration(Initial, Step1_Charge_Water, Step2_Charge_Brine_Mix, Step3_Buffer_Transfer, Step4_B5_Idle_Check, Step5_Evaporator_Charge, Step6_Evaporation, ParallelSplit, BranchA_Cool_B6, BranchA_Return_B6_to_B1, BranchB_B7_Availability_Check, Step8_Transfer_B5_to_B7, Step9_Cool_B7, Step10_11_Return_B7_to_B2, JoinWait);
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,80},{-100,100}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-40},{-100,-20}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-80},{-100,-60}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-100},{-100,-80}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-120,-120},{-100,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput V1 annotation(Placement(transformation(extent={{100,90},{120,110}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3 annotation(Placement(transformation(extent={{100,78},{120,98}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5 annotation(Placement(transformation(extent={{100,66},{120,86}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6 annotation(Placement(transformation(extent={{100,54},{120,74}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8 annotation(Placement(transformation(extent={{100,42},{120,62}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9 annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11 annotation(Placement(transformation(extent={{100,18},{120,38}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12 annotation(Placement(transformation(extent={{100,6},{120,26}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15 annotation(Placement(transformation(extent={{100,-6},{120,14}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18 annotation(Placement(transformation(extent={{100,-18},{120,2}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20 annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22 annotation(Placement(transformation(extent={{100,-42},{120,-22}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23 annotation(Placement(transformation(extent={{100,-54},{120,-34}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24 annotation(Placement(transformation(extent={{100,-66},{120,-46}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25 annotation(Placement(transformation(extent={{100,-78},{120,-58}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1 annotation(Placement(transformation(extent={{100,-90},{120,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2 annotation(Placement(transformation(extent={{100,-102},{120,-82}})));
  Modelica.Blocks.Interfaces.BooleanOutput heaterB5 annotation(Placement(transformation(extent={{100,-114},{120,-94}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB6 annotation(Placement(transformation(extent={{100,-126},{120,-106}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB7 annotation(Placement(transformation(extent={{100,-138},{120,-118}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state annotation(Placement(transformation(extent={{100,-150},{120,-130}})));
  Modelica.Blocks.Interfaces.IntegerOutput region annotation(Placement(transformation(extent={{100,-162},{120,-142}})));
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchADone(start=false, fixed=true);
  discrete Boolean branchBDone(start=false, fixed=true);
algorithm
  when {initial(), sample(0, scanPeriod)} then
    if pre(mode) == Mode.Initial then
      branchADone := false;
      branchBDone := false;
      if startEnable and B3_available then
        mode := Mode.Step1_Charge_Water;
      else
        mode := Mode.Initial;
      end if;
    elseif pre(mode) == Mode.Step1_Charge_Water then
      if LIS_301 >= 0.13 then
        mode := Mode.Step2_Charge_Brine_Mix;
      else
        mode := Mode.Step1_Charge_Water;
      end if;
    elseif pre(mode) == Mode.Step2_Charge_Brine_Mix then
      if QI_302 >= 0.08 then
        mode := Mode.Step3_Buffer_Transfer;
      else
        mode := Mode.Step2_Charge_Brine_Mix;
      end if;
    elseif pre(mode) == Mode.Step3_Buffer_Transfer then
      if LIS_301 < 0.01 then
        mode := Mode.Step4_B5_Idle_Check;
      else
        mode := Mode.Step3_Buffer_Transfer;
      end if;
    elseif pre(mode) == Mode.Step4_B5_Idle_Check then
      if LIS_501 < 0.01 and not pre(V15) then
        mode := Mode.Step5_Evaporator_Charge;
      else
        mode := Mode.Step4_B5_Idle_Check;
      end if;
    elseif pre(mode) == Mode.Step5_Evaporator_Charge then
      if LIS_501 >= 0.18 then
        mode := Mode.Step6_Evaporation;
      else
        mode := Mode.Step5_Evaporator_Charge;
      end if;
    elseif pre(mode) == Mode.Step6_Evaporation then
      if QIS_502 >= 0.18 then
        mode := Mode.ParallelSplit;
      else
        mode := Mode.Step6_Evaporation;
      end if;
    elseif pre(mode) == Mode.ParallelSplit then
      if TIS_602 <= 20 then
        branchADone := true;
      end if;
      if LIS_701 < 0.01 and LIS_501 < 0.01 and TIS_702 <= 25 then
        branchBDone := true;
      end if;
      if pre(branchADone) and pre(branchBDone) then
        mode := Mode.JoinWait;
      else
        mode := Mode.ParallelSplit;
      end if;
    elseif pre(mode) == Mode.JoinWait then
      if time > 2500 then
        branchADone := false;
        branchBDone := false;
        if startEnable and B3_available then
          mode := Mode.Step1_Charge_Water;
        else
          mode := Mode.Initial;
        end if;
      else
        mode := Mode.JoinWait;
      end if;
    else
      mode := Mode.Initial;
    end if;
  end when;

equation
  V1 = (mode == Mode.ParallelSplit) and (LIS_701 < 0.01) and (LIS_501 < 0.01) and (TIS_702 <= 25) and (LIS_701 > 0.02);
  V3 = V1;
  V18 = V1;
  V22 = V1;
  V23 = V1;
  V5 = (mode == Mode.ParallelSplit) and (TIS_602 <= 20) and (LIS_601 > 0.02);
  V6 = V5;
  V20 = V5;
  V24 = V5;
  V25 = V5;
  V8 = mode == Mode.Step1_Charge_Water;
  V9 = mode == Mode.Step2_Charge_Brine_Mix;
  V11 = mode == Mode.Step3_Buffer_Transfer;
  V12 = mode == Mode.Step5_Evaporator_Charge;
  V15 = (mode == Mode.Step8_Transfer_B5_to_B7) or ((mode == Mode.ParallelSplit) and (LIS_701 < 0.01) and not (LIS_501 < 0.01));
  P1 = V1;
  P2 = V5;
  heaterB5 = (mode == Mode.Step6_Evaporation) and (LIS_501 >= 0.05) and (FIS_801 >= 0.10);
  coolerB6 = (mode == Mode.ParallelSplit) and not branchADone;
  coolerB7 = (mode == Mode.ParallelSplit) and not branchBDone;
  controller_state = Integer(mode);
  region = if mode == Mode.ParallelSplit or mode == Mode.JoinWait then 2 else 1;
annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}),Text(extent={{-90,20},{90,-20}}, textString="Controller"),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end BatchController;