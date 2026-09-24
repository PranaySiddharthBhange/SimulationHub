model NaClController
  type Mode = enumeration(
    Initial,
    Step1_Charge_Water,
    Step2_Charge_Brine_Mix,
    Step3_Buffer_Transfer,
    Step4_B5_Idle_Check,
    Step5_Evaporator_Charge,
    Step6_Evaporation,
    Parallel_A_B,
    Branch_A_Cool_B6,
    Branch_A_Return_B6_to_B1,
    Branch_B_B7_Availability_Check,
    Step8_Transfer_B5_to_B7,
    Step9_Cool_B7,
    Step10_11_Return_B7_to_B2,
    JoinWait);

  parameter Modelica.Units.SI.Time scanPeriod = 1 "Assumption: controller scan period not stated in the brief";

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,100},{-100,120}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,84},{-100,104}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,68},{-100,88}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,52},{-100,72}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,36},{-100,56}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,4},{-100,24}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-12},{-100,8}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-120,-28},{-100,-8}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-44},{-100,-24}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));

  Modelica.Blocks.Interfaces.BooleanOutput V1 annotation(Placement(transformation(extent={{100,100},{120,120}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3 annotation(Placement(transformation(extent={{100,86},{120,106}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5 annotation(Placement(transformation(extent={{100,72},{120,92}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6 annotation(Placement(transformation(extent={{100,58},{120,78}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8 annotation(Placement(transformation(extent={{100,44},{120,64}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9 annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11 annotation(Placement(transformation(extent={{100,16},{120,36}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12 annotation(Placement(transformation(extent={{100,2},{120,22}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15 annotation(Placement(transformation(extent={{100,-12},{120,8}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18 annotation(Placement(transformation(extent={{100,-26},{120,-6}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20 annotation(Placement(transformation(extent={{100,-40},{120,-20}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22 annotation(Placement(transformation(extent={{100,-54},{120,-34}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23 annotation(Placement(transformation(extent={{100,-68},{120,-48}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24 annotation(Placement(transformation(extent={{100,-82},{120,-62}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25 annotation(Placement(transformation(extent={{100,-96},{120,-76}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1 annotation(Placement(transformation(extent={{100,-110},{120,-90}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2 annotation(Placement(transformation(extent={{100,-124},{120,-104}})));
  Modelica.Blocks.Interfaces.BooleanOutput heaterB5 annotation(Placement(transformation(extent={{100,-138},{120,-118}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB6 annotation(Placement(transformation(extent={{100,-152},{120,-132}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB7 annotation(Placement(transformation(extent={{100,-166},{120,-146}})));

  output Integer controller_state;
  output Integer region;
protected 
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchAComplete(start=false, fixed=true);
  discrete Boolean branchBComplete(start=false, fixed=true);
  Boolean scanTick;
  Boolean startSample;
equation
  scanTick = sample(0, scanPeriod);
  startSample = scanTick and startEnable;

  V1 = mode == Mode.Step10_11_Return_B7_to_B2;
  V3 = mode == Mode.Step10_11_Return_B7_to_B2;
  V5 = mode == Mode.Branch_A_Return_B6_to_B1;
  V6 = mode == Mode.Branch_A_Return_B6_to_B1;
  V8 = mode == Mode.Step1_Charge_Water;
  V9 = mode == Mode.Step2_Charge_Brine_Mix;
  V11 = mode == Mode.Step3_Buffer_Transfer;
  V12 = mode == Mode.Step5_Evaporator_Charge;
  V15 = mode == Mode.Step8_Transfer_B5_to_B7;
  V18 = mode == Mode.Step10_11_Return_B7_to_B2;
  V20 = mode == Mode.Branch_A_Return_B6_to_B1;
  V22 = mode == Mode.Step10_11_Return_B7_to_B2;
  V23 = mode == Mode.Step10_11_Return_B7_to_B2;
  V24 = mode == Mode.Branch_A_Return_B6_to_B1;
  V25 = mode == Mode.Branch_A_Return_B6_to_B1;
  P1 = (mode == Mode.Step10_11_Return_B7_to_B2) and LIS_701 > 0.02;
  P2 = (mode == Mode.Branch_A_Return_B6_to_B1) and LIS_601 > 0.02;
  heaterB5 = (mode == Mode.Step6_Evaporation) and LIS_501 >= 0.05 and FIS_801 >= 0.10;
  coolerB6 = mode == Mode.Branch_A_Cool_B6;
  coolerB7 = mode == Mode.Step9_Cool_B7;
  controller_state = Integer(mode);
  region = if mode == Mode.Branch_A_Cool_B6 or mode == Mode.Branch_A_Return_B6_to_B1 or mode == Mode.Branch_B_B7_Availability_Check or mode == Mode.Step8_Transfer_B5_to_B7 or mode == Mode.Step9_Cool_B7 or mode == Mode.Step10_11_Return_B7_to_B2 or mode == Mode.JoinWait or mode == Mode.Parallel_A_B then 2 else 1;
algorithm
  when {initial(), scanTick} then
    if initial() then
      mode := Mode.Initial;
      branchAComplete := false;
      branchBComplete := false;
    else
      if pre(mode) == Mode.Initial then
        branchAComplete := false;
        branchBComplete := false;
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
        if LIS_501 < 0.01 and not V15 then
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
          mode := Mode.Parallel_A_B;
          branchAComplete := false;
          branchBComplete := false;
        else
          mode := pre(mode);
        end if;
      elseif pre(mode) == Mode.Parallel_A_B then
        mode := Mode.Branch_A_Cool_B6;
      elseif pre(mode) == Mode.Branch_A_Cool_B6 then
        if TIS_602 <= 20 then
          mode := Mode.Branch_A_Return_B6_to_B1;
        else
          mode := Mode.Branch_B_B7_Availability_Check;
        end if;
      elseif pre(mode) == Mode.Branch_A_Return_B6_to_B1 then
        if LIS_601 <= 0.02 then
          branchAComplete := true;
          if pre(branchBComplete) then
            mode := Mode.JoinWait;
          else
            mode := Mode.Branch_B_B7_Availability_Check;
          end if;
        else
          mode := pre(mode);
        end if;
      elseif pre(mode) == Mode.Branch_B_B7_Availability_Check then
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
          mode := Mode.Step10_11_Return_B7_to_B2;
        else
          mode := pre(mode);
        end if;
      elseif pre(mode) == Mode.Step10_11_Return_B7_to_B2 then
        if LIS_701 <= 0.02 then
          branchBComplete := true;
          if pre(branchAComplete) then
            mode := Mode.JoinWait;
          else
            mode := Mode.Branch_A_Cool_B6;
          end if;
        else
          mode := pre(mode);
        end if;
      elseif pre(mode) == Mode.JoinWait then
        if time > 2500 then
          mode := Mode.Initial;
        else
          mode := pre(mode);
        end if;
      end if;
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),Text(extent={{-88,20},{88,-20}}, textString="Controller"),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end NaClController;
