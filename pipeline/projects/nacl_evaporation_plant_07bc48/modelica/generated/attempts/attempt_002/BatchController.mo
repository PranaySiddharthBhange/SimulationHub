model BatchController
  type Mode = enumeration(
    Initial,
    Step1_Charge_Water,
    Step2_Charge_Brine_Mix,
    Step3_Buffer_Transfer,
    Step4_B5_Idle_Check,
    Step5_Evaporator_Charge,
    Step6_Evaporation,
    BranchA_Cool_B6,
    BranchA_Return_B6_to_B1,
    BranchB_B7_Availability_Check,
    Step8_Transfer_B5_to_B7,
    Step9_Cool_B7,
    Step10_11_Return_B7_to_B2,
    JoinWait);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-120,-110},{-100,-90}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1 annotation(Placement(transformation(extent={{100,92},{120,112}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3 annotation(Placement(transformation(extent={{100,80},{120,100}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5 annotation(Placement(transformation(extent={{100,68},{120,88}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6 annotation(Placement(transformation(extent={{100,56},{120,76}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8 annotation(Placement(transformation(extent={{100,44},{120,64}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9 annotation(Placement(transformation(extent={{100,32},{120,52}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11 annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12 annotation(Placement(transformation(extent={{100,8},{120,28}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15 annotation(Placement(transformation(extent={{100,-4},{120,16}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18 annotation(Placement(transformation(extent={{100,-16},{120,4}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20 annotation(Placement(transformation(extent={{100,-28},{120,-8}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22 annotation(Placement(transformation(extent={{100,-40},{120,-20}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23 annotation(Placement(transformation(extent={{100,-52},{120,-32}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24 annotation(Placement(transformation(extent={{100,-64},{120,-44}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25 annotation(Placement(transformation(extent={{100,-76},{120,-56}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1 annotation(Placement(transformation(extent={{100,-88},{120,-68}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2 annotation(Placement(transformation(extent={{100,-100},{120,-80}})));
  Modelica.Blocks.Interfaces.BooleanOutput heaterB5 annotation(Placement(transformation(extent={{100,-112},{120,-92}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB6 annotation(Placement(transformation(extent={{100,-124},{120,-104}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB7 annotation(Placement(transformation(extent={{100,-136},{120,-116}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state annotation(Placement(transformation(extent={{100,-148},{120,-128}})));
  Modelica.Blocks.Interfaces.IntegerOutput region annotation(Placement(transformation(extent={{100,-160},{120,-140}})));

protected 
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchADone(start=false, fixed=true);
  discrete Boolean branchBDone(start=false, fixed=true);

equation
  V8 = mode == Mode.Step1_Charge_Water;
  V9 = mode == Mode.Step2_Charge_Brine_Mix;
  V11 = mode == Mode.Step3_Buffer_Transfer;
  V12 = mode == Mode.Step5_Evaporator_Charge;
  V15 = mode == Mode.Step8_Transfer_B5_to_B7;
  heaterB5 = (mode == Mode.Step6_Evaporation) and (LIS_501 >= 0.05) and (FIS_801 >= 0.10);
  coolerB6 = mode == Mode.BranchA_Cool_B6;
  V5 = (mode == Mode.BranchA_Return_B6_to_B1) and (LIS_601 > 0.02);
  V6 = V5;
  V20 = V5;
  V24 = V5;
  V25 = V5;
  P2 = V5;
  coolerB7 = mode == Mode.Step9_Cool_B7;
  V1 = (mode == Mode.Step10_11_Return_B7_to_B2) and (LIS_701 > 0.02);
  V3 = V1;
  V18 = V1;
  V22 = V1;
  V23 = V1;
  P1 = V1;
  controller_state = Integer(mode);
  region = if mode == Mode.BranchA_Cool_B6 or mode == Mode.BranchA_Return_B6_to_B1 or mode == Mode.BranchB_B7_Availability_Check or mode == Mode.Step8_Transfer_B5_to_B7 or mode == Mode.Step9_Cool_B7 or mode == Mode.Step10_11_Return_B7_to_B2 or mode == Mode.JoinWait then 2 else 1;

algorithm 
  when {initial(), sample(0, scanPeriod)} then
    if initial() then
      mode := Mode.Initial;
      branchADone := false;
      branchBDone := false;
    elseif pre(mode) == Mode.Initial then
      branchADone := false;
      branchBDone := false;
      if startEnable and B3_available then
        mode := Mode.Step1_Charge_Water;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step1_Charge_Water then
      if LIS_301 >= 0.13 then
        mode := Mode.Step2_Charge_Brine_Mix;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step2_Charge_Brine_Mix then
      if QI_302 >= 0.08 then
        mode := Mode.Step3_Buffer_Transfer;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step3_Buffer_Transfer then
      if LIS_301 < 0.01 then
        mode := Mode.Step4_B5_Idle_Check;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step4_B5_Idle_Check then
      if LIS_501 < 0.01 then
        mode := Mode.Step5_Evaporator_Charge;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step5_Evaporator_Charge then
      if LIS_501 >= 0.18 then
        mode := Mode.Step6_Evaporation;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step6_Evaporation then
      if QIS_502 >= 0.18 then
        mode := Mode.BranchA_Cool_B6;
        branchADone := false;
        branchBDone := false;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.BranchA_Cool_B6 then
      if TIS_602 <= 20 then
        branchADone := true;
        mode := Mode.BranchB_B7_Availability_Check;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.BranchB_B7_Availability_Check then
      if LIS_701 < 0.01 then
        mode := Mode.Step8_Transfer_B5_to_B7;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step8_Transfer_B5_to_B7 then
      if LIS_501 < 0.01 then
        mode := Mode.Step9_Cool_B7;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step9_Cool_B7 then
      if TIS_702 <= 25 then
        branchBDone := true;
        if pre(branchADone) then
          mode := Mode.BranchA_Return_B6_to_B1;
        else
          mode := Mode.JoinWait;
        end if;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.BranchA_Return_B6_to_B1 then
      if LIS_601 <= 0.02 then
        if pre(branchBDone) then
          mode := Mode.Step10_11_Return_B7_to_B2;
        else
          mode := Mode.JoinWait;
        end if;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.Step10_11_Return_B7_to_B2 then
      if LIS_701 <= 0.02 then
        mode := Mode.JoinWait;
      else
        mode := pre(mode);
      end if;
    elseif pre(mode) == Mode.JoinWait then
      if time > 2500 and pre(branchADone) and pre(branchBDone) then
        if startEnable and B3_available then
          mode := Mode.Step1_Charge_Water;
          branchADone := false;
          branchBDone := false;
        else
          mode := Mode.Initial;
          branchADone := false;
          branchBDone := false;
        end if;
      else
        mode := pre(mode);
      end if;
    else
      mode := Mode.Initial;
      branchADone := false;
      branchBDone := false;
    end if;
  end when;

annotation(
  Icon(graphics={
    Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),
    Text(extent={{-86,30},{86,-10}}, textString="Controller"),
    Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={
    Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}),
    Text(extent={{-90,20},{90,-20}}, textString="Sequential\nController")}));
end BatchController;
