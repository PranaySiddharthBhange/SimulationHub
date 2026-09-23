model NaClEvaporationController
  type Mode = enumeration(Idle, Step1, Step2, Step3, Step4, Step5, Step6, BranchA_CoolB6, BranchA_ReturnB6, BranchB_WaitB7Idle, BranchB_TransferB5ToB7, BranchB_CoolB7, BranchB_ReturnB7, JoinWait);
  Modelica.Blocks.Interfaces.RealInput LIS_301;
  Modelica.Blocks.Interfaces.RealInput QI_302;
  Modelica.Blocks.Interfaces.RealInput LIS_501;
  Modelica.Blocks.Interfaces.RealInput QIS_502;
  Modelica.Blocks.Interfaces.RealInput TIS_602;
  Modelica.Blocks.Interfaces.RealInput TIS_702;
  Modelica.Blocks.Interfaces.RealInput FIS_801;
  Modelica.Blocks.Interfaces.RealInput LIS_701;
  Modelica.Blocks.Interfaces.BooleanOutput V1;
  Modelica.Blocks.Interfaces.BooleanOutput V3;
  Modelica.Blocks.Interfaces.BooleanOutput V5;
  Modelica.Blocks.Interfaces.BooleanOutput V6;
  Modelica.Blocks.Interfaces.BooleanOutput V8;
  Modelica.Blocks.Interfaces.BooleanOutput V9;
  Modelica.Blocks.Interfaces.BooleanOutput V11;
  Modelica.Blocks.Interfaces.BooleanOutput V12;
  Modelica.Blocks.Interfaces.BooleanOutput V15;
  Modelica.Blocks.Interfaces.BooleanOutput V18;
  Modelica.Blocks.Interfaces.BooleanOutput V20;
  Modelica.Blocks.Interfaces.BooleanOutput V22;
  Modelica.Blocks.Interfaces.BooleanOutput V23;
  Modelica.Blocks.Interfaces.BooleanOutput V24;
  Modelica.Blocks.Interfaces.BooleanOutput V25;
  Modelica.Blocks.Interfaces.BooleanOutput P1;
  Modelica.Blocks.Interfaces.BooleanOutput P2;
  Modelica.Blocks.Interfaces.BooleanOutput B5_Heater;
  Modelica.Blocks.Interfaces.BooleanOutput B6_Cooler;
  Modelica.Blocks.Interfaces.BooleanOutput B7_Cooler;
protected 
  discrete Mode mode(start=Mode.Idle, fixed=true);
  discrete Boolean branchAComplete(start=false, fixed=true);
  discrete Boolean branchBComplete(start=false, fixed=true);
  Boolean startCmd;
  Boolean startPulse;
  Boolean heaterPermissive;
equation
  startCmd = time >= 1;
  startPulse = startCmd and not pre(startCmd);
  heaterPermissive = LIS_501 >= 0.05 and FIS_801 >= 0.10;
  V1 = mode == Mode.BranchB_ReturnB7;
  V3 = mode == Mode.BranchB_ReturnB7;
  V5 = mode == Mode.BranchA_ReturnB6;
  V6 = mode == Mode.BranchA_ReturnB6;
  V8 = mode == Mode.Step1;
  V9 = mode == Mode.Step2;
  V11 = mode == Mode.Step3;
  V12 = mode == Mode.Step5;
  V15 = mode == Mode.BranchB_TransferB5ToB7;
  V18 = mode == Mode.BranchB_ReturnB7;
  V20 = mode == Mode.BranchA_ReturnB6;
  V22 = mode == Mode.BranchB_ReturnB7;
  V23 = mode == Mode.BranchB_ReturnB7;
  V24 = mode == Mode.BranchA_ReturnB6;
  V25 = mode == Mode.BranchA_ReturnB6;
  P1 = mode == Mode.BranchB_ReturnB7 and LIS_701 > 0.02;
  P2 = mode == Mode.BranchA_ReturnB6;
  B5_Heater = mode == Mode.Step6 and heaterPermissive;
  B6_Cooler = mode == Mode.BranchA_CoolB6;
  B7_Cooler = mode == Mode.BranchB_CoolB7;
algorithm
  when {startPulse, pre(mode) == Mode.Step1 and LIS_301 >= 0.13, pre(mode) == Mode.Step2 and QI_302 >= 0.08, pre(mode) == Mode.Step3 and LIS_301 < 0.01, pre(mode) == Mode.Step4 and LIS_501 < 0.01 and not V15, pre(mode) == Mode.Step5 and LIS_501 >= 0.18, pre(mode) == Mode.Step6 and QIS_502 >= 0.18, pre(mode) == Mode.BranchA_CoolB6 and TIS_602 <= 20, pre(mode) == Mode.BranchA_ReturnB6 and branchAComplete, pre(mode) == Mode.BranchB_WaitB7Idle and LIS_701 < 0.01, pre(mode) == Mode.BranchB_TransferB5ToB7 and LIS_501 < 0.01, pre(mode) == Mode.BranchB_CoolB7 and TIS_702 <= 25, pre(mode) == Mode.BranchB_ReturnB7 and branchBComplete, pre(mode) == Mode.JoinWait and branchAComplete and branchBComplete and time > 2500} then
    if startPulse and pre(mode) == Mode.Idle then
      mode := Mode.Step1;
      branchAComplete := false;
      branchBComplete := false;
    elseif pre(mode) == Mode.Step1 and LIS_301 >= 0.13 then
      mode := Mode.Step2;
    elseif pre(mode) == Mode.Step2 and QI_302 >= 0.08 then
      mode := Mode.Step3;
    elseif pre(mode) == Mode.Step3 and LIS_301 < 0.01 then
      mode := Mode.Step4;
    elseif pre(mode) == Mode.Step4 and LIS_501 < 0.01 and not pre(V15) then
      mode := Mode.Step5;
    elseif pre(mode) == Mode.Step5 and LIS_501 >= 0.18 then
      mode := Mode.Step6;
    elseif pre(mode) == Mode.Step6 and QIS_502 >= 0.18 then
      mode := Mode.BranchA_CoolB6;
      branchAComplete := false;
      branchBComplete := false;
    elseif pre(mode) == Mode.BranchA_CoolB6 and TIS_602 <= 20 then
      mode := Mode.BranchA_ReturnB6;
    elseif pre(mode) == Mode.BranchA_ReturnB6 then
      branchAComplete := true;
      if pre(branchBComplete) then
        mode := Mode.JoinWait;
      end if;
    elseif pre(mode) == Mode.BranchB_WaitB7Idle and LIS_701 < 0.01 then
      mode := Mode.BranchB_TransferB5ToB7;
    elseif pre(mode) == Mode.BranchB_TransferB5ToB7 and LIS_501 < 0.01 then
      mode := Mode.BranchB_CoolB7;
    elseif pre(mode) == Mode.BranchB_CoolB7 and TIS_702 <= 25 then
      mode := Mode.BranchB_ReturnB7;
    elseif pre(mode) == Mode.BranchB_ReturnB7 then
      branchBComplete := true;
      if pre(branchAComplete) then
        mode := Mode.JoinWait;
      end if;
    elseif pre(mode) == Mode.JoinWait and pre(branchAComplete) and pre(branchBComplete) and time > 2500 then
      mode := Mode.Idle;
      branchAComplete := false;
      branchBComplete := false;
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}),Text(extent={{-80,20},{80,-20}}, textString="CTRL")}));
end NaClEvaporationController;