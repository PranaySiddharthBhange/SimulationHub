within ;
model CentralController
  type Mode = enumeration(Initial, Step1, Step2, Step3, Step4, Step5, Step6, BranchA_Cool, BranchA_Return, BranchB_Check, Step8, Step9, Step10_11, JoinWait);
  parameter Modelica.Units.SI.Time scanPeriod = 1;
  Modelica.Blocks.Interfaces.BooleanInput startEnable annotation(Placement(transformation(extent={{-120,80},{-100,100}})));
  Modelica.Blocks.Interfaces.BooleanInput B3_available annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-40},{-100,-20}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-80},{-100,-60}})));
  Modelica.Blocks.Interfaces.RealInput LIS_601 annotation(Placement(transformation(extent={{-20,100},{0,120}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{20,100},{40,120}})));
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
  Modelica.Blocks.Interfaces.BooleanOutput heaterB5 annotation(Placement(transformation(extent={{60,-102},{80,-82}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB6 annotation(Placement(transformation(extent={{20,-102},{40,-82}})));
  Modelica.Blocks.Interfaces.BooleanOutput coolerB7 annotation(Placement(transformation(extent={{-20,-102},{0,-82}})));
  output Integer controller_state;
  output Integer region;
protected 
  discrete Mode mode(start=Mode.Initial, fixed=true);
  discrete Boolean branchA_done(start=false, fixed=true);
  discrete Boolean branchB_done(start=false, fixed=true);
  Boolean tick;
  Boolean heaterPermissive;
equation
  tick = sample(0, scanPeriod);
  heaterPermissive = LIS_501 >= 0.05 and FIS_801 >= 0.10;
  V1 = (mode == Mode.Step10_11) and LIS_701 > 0.02;
  V3 = V1;
  V5 = (mode == Mode.BranchA_Return) and LIS_601 > 0.02;
  V6 = V5;
  V8 = mode == Mode.Step1;
  V9 = mode == Mode.Step2;
  V11 = mode == Mode.Step3;
  V12 = mode == Mode.Step5;
  V15 = mode == Mode.Step8;
  V18 = V1;
  V20 = V5;
  V22 = V1;
  V23 = V1;
  V24 = V5;
  V25 = V5;
  P1 = (mode == Mode.Step10_11) and LIS_701 > 0.02;
  P2 = (mode == Mode.BranchA_Return) and LIS_601 > 0.02;
  heaterB5 = (mode == Mode.Step6) and heaterPermissive;
  coolerB6 = mode == Mode.BranchA_Cool;
  coolerB7 = mode == Mode.Step9;
  controller_state = Integer(mode);
  region = if mode == Mode.BranchA_Cool or mode == Mode.BranchA_Return then 1 else if mode == Mode.BranchB_Check or mode == Mode.Step8 or mode == Mode.Step9 or mode == Mode.Step10_11 then 2 else if mode == Mode.JoinWait then 3 else 0;
algorithm
  when tick then
    if pre(mode) == Mode.Initial and startEnable and B3_available then
      mode := Mode.Step1;
      branchA_done := false;
      branchB_done := false;
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
      mode := Mode.BranchA_Cool;
      branchA_done := false;
      branchB_done := false;
    elseif pre(mode) == Mode.BranchA_Cool and TIS_602 <= 293.15 then
      mode := Mode.BranchA_Return;
    elseif pre(mode) == Mode.BranchA_Return and LIS_601 <= 0.02 then
      branchA_done := true;
      if pre(branchB_done) then
        mode := Mode.JoinWait;
      else
        mode := Mode.BranchB_Check;
      end if;
    elseif pre(mode) == Mode.BranchB_Check and LIS_701 < 0.01 then
      mode := Mode.Step8;
    elseif pre(mode) == Mode.Step8 and LIS_501 < 0.01 then
      mode := Mode.Step9;
    elseif pre(mode) == Mode.Step9 and TIS_702 <= 298.15 then
      mode := Mode.Step10_11;
    elseif pre(mode) == Mode.Step10_11 and LIS_701 <= 0.02 then
      branchB_done := true;
      if pre(branchA_done) then
        mode := Mode.JoinWait;
      else
        mode := Mode.BranchA_Cool;
      end if;
    elseif pre(mode) == Mode.JoinWait and time > 2500 then
      mode := Mode.Initial;
      branchA_done := false;
      branchB_done := false;
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={95,95,95}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-90,20},{90,-20}}, textString="Controller")}), Diagram(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={95,95,95})}));
end CentralController;
