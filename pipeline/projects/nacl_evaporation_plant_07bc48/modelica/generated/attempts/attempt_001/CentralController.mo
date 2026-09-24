model CentralController
  type Mode = enumeration(Initial, Step1, Step2, Step3, Step4, Step5, Step6, Parallel, BranchACool, BranchAReturn, BranchBCheck, Step8, Step9, Step10_11, JoinWait);
  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,90},{-100,110}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.RealOutput region annotation(Placement(transformation(extent={{100,90},{120,110}})));
  Modelica.Blocks.Interfaces.RealOutput controller_state annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.BooleanOutput V1 annotation(Placement(transformation(extent={{100,54},{120,66}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3 annotation(Placement(transformation(extent={{100,42},{120,54}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5 annotation(Placement(transformation(extent={{100,30},{120,42}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6 annotation(Placement(transformation(extent={{100,18},{120,30}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8 annotation(Placement(transformation(extent={{100,6},{120,18}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9 annotation(Placement(transformation(extent={{100,-6},{120,6}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11 annotation(Placement(transformation(extent={{100,-18},{120,-6}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12 annotation(Placement(transformation(extent={{100,-30},{120,-18}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15 annotation(Placement(transformation(extent={{100,-42},{120,-30}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18 annotation(Placement(transformation(extent={{100,-54},{120,-42}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20 annotation(Placement(transformation(extent={{100,-66},{120,-54}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22 annotation(Placement(transformation(extent={{100,-78},{120,-66}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23 annotation(Placement(transformation(extent={{100,-90},{120,-78}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24 annotation(Placement(transformation(extent={{100,-102},{120,-90}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25 annotation(Placement(transformation(extent={{100,-114},{120,-102}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1 annotation(Placement(transformation(extent={{60,-114},{80,-102}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2 annotation(Placement(transformation(extent={{20,-114},{40,-102}})));
  Modelica.Blocks.Interfaces.BooleanOutput HeaterB5 annotation(Placement(transformation(extent={{-20,-114},{0,-102}})));
  Modelica.Blocks.Interfaces.BooleanOutput CoolerB6 annotation(Placement(transformation(extent={{-60,-114},{-40,-102}})));
  Modelica.Blocks.Interfaces.BooleanOutput CoolerB7 annotation(Placement(transformation(extent={{-100,-114},{-80,-102}})));
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchADone(start=false, fixed=true);
  discrete Boolean branchBDone(start=false, fixed=true);
 equation
  controller_state = Integer(mode);
  region = if Integer(mode) >= Integer(Mode.Parallel) then 2 else 1;
  V8 = mode == Mode.Step1;
  V9 = mode == Mode.Step2;
  V11 = mode == Mode.Step3;
  V12 = mode == Mode.Step5;
  V15 = mode == Mode.Step8;
  CoolerB6 = mode == Mode.BranchACool;
  P2 = (mode == Mode.BranchAReturn) and (LIS_601 > 0.02);
  V5 = P2;
  V6 = P2;
  V20 = P2;
  V24 = P2;
  V25 = P2;
  CoolerB7 = mode == Mode.Step9;
  P1 = (mode == Mode.Step10_11) and (LIS_701 > 0.02);
  V1 = P1;
  V3 = P1;
  V18 = P1;
  V22 = P1;
  V23 = P1;
  HeaterB5 = (mode == Mode.Step6) and (LIS_501 >= 0.05);
 algorithm
  when {initial(), startEnable, LIS_301 >= 0.13, QI_302 >= 0.08, LIS_301 < 0.01, LIS_501 < 0.01, LIS_501 >= 0.18, QIS_502 >= 0.18, TIS_602 <= 20, LIS_601 <= 0.02, LIS_701 < 0.01, TIS_702 <= 25, LIS_701 <= 0.02, time > 2500} then
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
    elseif pre(mode) == Mode.Step4 and (LIS_501 < 0.01) and not pre(V15) then
      mode := Mode.Step5;
    elseif pre(mode) == Mode.Step5 and LIS_501 >= 0.18 then
      mode := Mode.Step6;
    elseif pre(mode) == Mode.Step6 and QIS_502 >= 0.18 then
      mode := Mode.Parallel;
      branchADone := false;
      branchBDone := false;
    elseif pre(mode) == Mode.Parallel then
      mode := Mode.BranchACool;
    elseif pre(mode) == Mode.BranchACool and TIS_602 <= 20 then
      mode := Mode.BranchAReturn;
    elseif pre(mode) == Mode.BranchAReturn and LIS_601 <= 0.02 then
      mode := Mode.BranchBCheck;
      branchADone := true;
    elseif pre(mode) == Mode.BranchBCheck and LIS_701 < 0.01 then
      mode := Mode.Step8;
    elseif pre(mode) == Mode.Step8 and LIS_501 < 0.01 then
      mode := Mode.Step9;
    elseif pre(mode) == Mode.Step9 and TIS_702 <= 25 then
      mode := Mode.Step10_11;
    elseif pre(mode) == Mode.Step10_11 and LIS_701 <= 0.02 then
      mode := Mode.JoinWait;
      branchBDone := true;
    elseif pre(mode) == Mode.JoinWait and pre(branchADone) and pre(branchBDone) and time > 2500 then
      mode := Mode.Initial;
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-80,40},{80,80}}, textString="Controller"),Text(extent={{-90,-10},{-20,10}}, textString="sens"),Text(extent={{20,-10},{90,10}}, textString="act") }));
end CentralController;
