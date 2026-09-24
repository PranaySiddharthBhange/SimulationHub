model BatchController
  type Mode = enumeration(
    Initial,
    Step1,
    Step2,
    Step3,
    Step4,
    Step5,
    Step6,
    BranchACool,
    BranchAReturn,
    BranchBCheck,
    Step8,
    Step9,
    Step10_11,
    JoinWait);

  parameter Modelica.Units.SI.Time scanPeriod = 1;

  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,96},{-100,116}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,72},{-100,92}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,48},{-100,68}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,24},{-100,44}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,-24},{-100,-4}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-48},{-100,-28}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-72},{-100,-52}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-120,-96},{-100,-76}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-120},{-100,-100}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-144},{-100,-124}})));

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
  Modelica.Blocks.Interfaces.BooleanOutput P1 annotation(Placement(transformation(extent={{100,-106},{120,-86}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2 annotation(Placement(transformation(extent={{100,-120},{120,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput heater annotation(Placement(transformation(extent={{100,-134},{120,-114}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB6 annotation(Placement(transformation(extent={{100,-148},{120,-128}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB7 annotation(Placement(transformation(extent={{100,-162},{120,-142}})));

  output Integer controller_state;
  output Integer region;

protected 
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchADone(start=false, fixed=true);
  discrete Boolean branchBDone(start=false, fixed=true);
  Boolean tick;
equation
  tick = sample(0, scanPeriod);

  controller_state = Integer(mode);
  region = if mode == Mode.BranchACool or mode == Mode.BranchAReturn or mode == Mode.BranchBCheck or mode == Mode.Step8 or mode == Mode.Step9 or mode == Mode.Step10_11 or mode == Mode.JoinWait then 2 else 1;

  V1 = mode == Mode.Step10_11;
  V3 = mode == Mode.Step10_11;
  V5 = mode == Mode.BranchAReturn;
  V6 = mode == Mode.BranchAReturn;
  V8 = mode == Mode.Step1;
  V9 = mode == Mode.Step2;
  V11 = mode == Mode.Step3;
  V12 = mode == Mode.Step5;
  V15 = mode == Mode.Step8;
  V18 = mode == Mode.Step10_11;
  V20 = mode == Mode.BranchAReturn;
  V22 = mode == Mode.Step10_11;
  V23 = mode == Mode.Step10_11;
  V24 = mode == Mode.BranchAReturn;
  V25 = mode == Mode.BranchAReturn;
  P1 = (mode == Mode.Step10_11) and LIS_701 > 0.02;
  P2 = (mode == Mode.BranchAReturn) and LIS_601 > 0.02;
  heater = (mode == Mode.Step6) and LIS_501 >= 0.05 and FIS_801 >= 0.10;
  coolerB6 = mode == Mode.BranchACool;
  coolerB7 = mode == Mode.Step9;
algorithm 
  when tick then
    if pre(mode) == Mode.Initial and startEnable and B3_available then
      mode := Mode.Step1;
      branchADone := false;
      branchBDone := false;
    elseif pre(mode) == Mode.Step1 and LIS_301 >= 0.13 then
      mode := Mode.Step2;
    elseif pre(mode) == Mode.Step2 and QI_302 >= 0.08 then
      mode := Mode.Step3;
    elseif pre(mode) == Mode.Step3 and LIS_301 < 0.01 then
      mode := Mode.Step4;
    elseif pre(mode) == Mode.Step4 and LIS_501 < 0.01 then
      mode := Mode.Step5;
    elseif pre(mode) == Mode.Step5 and LIS_501 >= 0.18 then
      mode := Mode.Step6;
    elseif pre(mode) == Mode.Step6 and QIS_502 >= 0.18 then
      mode := Mode.BranchACool;
      branchADone := false;
      branchBDone := false;
    elseif pre(mode) == Mode.BranchACool and TIS_602 <= 20 then
      mode := Mode.BranchAReturn;
    elseif pre(mode) == Mode.BranchAReturn and LIS_601 <= 0.02 then
      branchADone := true;
      if pre(branchBDone) then
        mode := Mode.JoinWait;
      else
        mode := Mode.BranchBCheck;
      end if;
    elseif pre(mode) == Mode.BranchBCheck and LIS_701 < 0.01 then
      mode := Mode.Step8;
    elseif pre(mode) == Mode.Step8 and LIS_501 < 0.01 then
      mode := Mode.Step9;
    elseif pre(mode) == Mode.Step9 and TIS_702 <= 25 then
      mode := Mode.Step10_11;
    elseif pre(mode) == Mode.Step10_11 and LIS_701 <= 0.02 then
      branchBDone := true;
      if pre(branchADone) then
        mode := Mode.JoinWait;
      else
        mode := Mode.BranchACool;
      end if;
    elseif pre(mode) == Mode.JoinWait and time > 2500 then
      mode := Mode.Initial;
    end if;
  end when;
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-100},{100,100}}, lineColor={255,0,255}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),
    Text(extent={{-90,34},{90,74}}, textString="Controller"),
    Text(extent={{-100,100},{100,140}}, textString="%name")
  }));
end BatchController;
