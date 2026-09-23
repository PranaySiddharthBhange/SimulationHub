model NaClEvaporationController
  extends Modelica.Blocks.Icons.Block;
  type MainMode = enumeration(Idle, Step1, Step2, Step3, Step4, Step5, Step6, JoinWait);
  Modelica.Blocks.Interfaces.RealInput LIS_301 annotation(Placement(transformation(extent={{-120,90},{-80,130}})));
  Modelica.Blocks.Interfaces.RealInput QI_302 annotation(Placement(transformation(extent={{-120,60},{-80,100}})));
  Modelica.Blocks.Interfaces.RealInput LIS_501 annotation(Placement(transformation(extent={{-120,30},{-80,70}})));
  Modelica.Blocks.Interfaces.RealInput QIS_502 annotation(Placement(transformation(extent={{-120,0},{-80,40}})));
  Modelica.Blocks.Interfaces.RealInput TIS_602 annotation(Placement(transformation(extent={{-120,-30},{-80,10}})));
  Modelica.Blocks.Interfaces.RealInput TIS_702 annotation(Placement(transformation(extent={{-120,-60},{-80,-20}})));
  Modelica.Blocks.Interfaces.RealInput FIS_801 annotation(Placement(transformation(extent={{-120,-90},{-80,-50}})));
  Modelica.Blocks.Interfaces.RealInput LIS_701 annotation(Placement(transformation(extent={{-120,-120},{-80,-80}})));
  Modelica.Blocks.Interfaces.BooleanOutput V1 annotation(Placement(transformation(extent={{80,100},{120,140}})));
  Modelica.Blocks.Interfaces.BooleanOutput V3 annotation(Placement(transformation(extent={{80,85},{120,125}})));
  Modelica.Blocks.Interfaces.BooleanOutput V5 annotation(Placement(transformation(extent={{80,70},{120,110}})));
  Modelica.Blocks.Interfaces.BooleanOutput V6 annotation(Placement(transformation(extent={{80,55},{120,95}})));
  Modelica.Blocks.Interfaces.BooleanOutput V8 annotation(Placement(transformation(extent={{80,40},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput V9 annotation(Placement(transformation(extent={{80,25},{120,65}})));
  Modelica.Blocks.Interfaces.BooleanOutput V11 annotation(Placement(transformation(extent={{80,10},{120,50}})));
  Modelica.Blocks.Interfaces.BooleanOutput V12 annotation(Placement(transformation(extent={{80,-5},{120,35}})));
  Modelica.Blocks.Interfaces.BooleanOutput V15 annotation(Placement(transformation(extent={{80,-20},{120,20}})));
  Modelica.Blocks.Interfaces.BooleanOutput V18 annotation(Placement(transformation(extent={{80,-35},{120,5}})));
  Modelica.Blocks.Interfaces.BooleanOutput V20 annotation(Placement(transformation(extent={{80,-50},{120,-10}})));
  Modelica.Blocks.Interfaces.BooleanOutput V22 annotation(Placement(transformation(extent={{80,-65},{120,-25}})));
  Modelica.Blocks.Interfaces.BooleanOutput V23 annotation(Placement(transformation(extent={{80,-80},{120,-40}})));
  Modelica.Blocks.Interfaces.BooleanOutput V24 annotation(Placement(transformation(extent={{80,-95},{120,-55}})));
  Modelica.Blocks.Interfaces.BooleanOutput V25 annotation(Placement(transformation(extent={{80,-110},{120,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput P1 annotation(Placement(transformation(extent={{80,-125},{120,-85}})));
  Modelica.Blocks.Interfaces.BooleanOutput P2 annotation(Placement(transformation(extent={{80,-140},{120,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput B5_Heater annotation(Placement(transformation(extent={{20,100},{60,140}})));
  Modelica.Blocks.Interfaces.BooleanOutput B6_Cooler annotation(Placement(transformation(extent={{20,70},{60,110}})));
  Modelica.Blocks.Interfaces.BooleanOutput B7_Cooler annotation(Placement(transformation(extent={{20,40},{60,80}})));
protected 
  discrete MainMode mode(start=MainMode.Idle, fixed=true);
  discrete Boolean branchA_coolingDone(start=false, fixed=true);
  discrete Boolean branchA_returnDone(start=false, fixed=true);
  discrete Boolean branchB_waitDone(start=false, fixed=true);
  discrete Boolean branchB_transferDone(start=false, fixed=true);
  discrete Boolean branchB_coolingDone(start=false, fixed=true);
  discrete Boolean branchB_returnDone(start=false, fixed=true);
  Boolean startCmd;
  Boolean startPulse;
  Boolean heaterPermissive;
  Boolean branchAReady;
  Boolean branchBReady;
equation
  startCmd = time >= 1;
  startPulse = startCmd and not pre(startCmd);
  heaterPermissive = LIS_501 >= 0.05 and FIS_801 >= 0.10;
  branchAReady = branchA_returnDone;
  branchBReady = branchB_returnDone;

  V1 = branchB_returnDone == false and pre(mode) == MainMode.JoinWait and false or (branchB_coolingDone and not branchB_returnDone);
  V3 = V1;
  V5 = branchA_coolingDone and not branchA_returnDone;
  V6 = V5;
  V8 = mode == MainMode.Step1;
  V9 = mode == MainMode.Step2;
  V11 = mode == MainMode.Step3;
  V12 = mode == MainMode.Step5;
  V15 = branchB_waitDone and not branchB_transferDone;
  V18 = V1;
  V20 = V5;
  V22 = V1;
  V23 = V1;
  V24 = V5;
  V25 = V5;
  P1 = (branchB_coolingDone and not branchB_returnDone) and LIS_701 > 0.02;
  P2 = branchA_coolingDone and not branchA_returnDone;
  B5_Heater = mode == MainMode.Step6 and heaterPermissive;
  B6_Cooler = mode == MainMode.Step6 and not branchA_coolingDone;
  B7_Cooler = mode == MainMode.Step6 and branchB_transferDone and not branchB_coolingDone;
algorithm
  when {startPulse,
        pre(mode) == MainMode.Step1 and LIS_301 >= 0.13,
        pre(mode) == MainMode.Step2 and QI_302 >= 0.08,
        pre(mode) == MainMode.Step3 and LIS_301 < 0.01,
        pre(mode) == MainMode.Step4 and LIS_501 < 0.01 and not pre(V15),
        pre(mode) == MainMode.Step5 and LIS_501 >= 0.18,
        pre(mode) == MainMode.Step6 and QIS_502 >= 0.18,
        pre(mode) == MainMode.Step6 and not pre(branchA_coolingDone) and TIS_602 <= 20,
        pre(mode) == MainMode.Step6 and pre(branchA_coolingDone) and not pre(branchA_returnDone),
        pre(mode) == MainMode.Step6 and not pre(branchB_waitDone) and LIS_701 < 0.01,
        pre(mode) == MainMode.Step6 and pre(branchB_waitDone) and not pre(branchB_transferDone) and LIS_501 < 0.01,
        pre(mode) == MainMode.Step6 and pre(branchB_transferDone) and not pre(branchB_coolingDone) and TIS_702 <= 25,
        pre(mode) == MainMode.Step6 and pre(branchB_coolingDone) and not pre(branchB_returnDone),
        pre(mode) == MainMode.JoinWait and pre(branchAReady) and pre(branchBReady) and time > 2500} then
    if startPulse and pre(mode) == MainMode.Idle then
      mode := MainMode.Step1;
      branchA_coolingDone := false;
      branchA_returnDone := false;
      branchB_waitDone := false;
      branchB_transferDone := false;
      branchB_coolingDone := false;
      branchB_returnDone := false;
    elseif pre(mode) == MainMode.Step1 and LIS_301 >= 0.13 then
      mode := MainMode.Step2;
    elseif pre(mode) == MainMode.Step2 and QI_302 >= 0.08 then
      mode := MainMode.Step3;
    elseif pre(mode) == MainMode.Step3 and LIS_301 < 0.01 then
      mode := MainMode.Step4;
    elseif pre(mode) == MainMode.Step4 and LIS_501 < 0.01 and not pre(V15) then
      mode := MainMode.Step5;
    elseif pre(mode) == MainMode.Step5 and LIS_501 >= 0.18 then
      mode := MainMode.Step6;
    elseif pre(mode) == MainMode.Step6 and QIS_502 >= 0.18 then
      branchA_coolingDone := false;
      branchA_returnDone := false;
      branchB_waitDone := false;
      branchB_transferDone := false;
      branchB_coolingDone := false;
      branchB_returnDone := false;
    elseif pre(mode) == MainMode.Step6 and not pre(branchA_coolingDone) and TIS_602 <= 20 then
      branchA_coolingDone := true;
    elseif pre(mode) == MainMode.Step6 and pre(branchA_coolingDone) and not pre(branchA_returnDone) then
      branchA_returnDone := true;
      if pre(branchB_returnDone) then
        mode := MainMode.JoinWait;
      end if;
    elseif pre(mode) == MainMode.Step6 and not pre(branchB_waitDone) and LIS_701 < 0.01 then
      branchB_waitDone := true;
    elseif pre(mode) == MainMode.Step6 and pre(branchB_waitDone) and not pre(branchB_transferDone) and LIS_501 < 0.01 then
      branchB_transferDone := true;
    elseif pre(mode) == MainMode.Step6 and pre(branchB_transferDone) and not pre(branchB_coolingDone) and TIS_702 <= 25 then
      branchB_coolingDone := true;
    elseif pre(mode) == MainMode.Step6 and pre(branchB_coolingDone) and not pre(branchB_returnDone) then
      branchB_returnDone := true;
      if pre(branchA_returnDone) then
        mode := MainMode.JoinWait;
      end if;
    elseif pre(mode) == MainMode.JoinWait and pre(branchAReady) and pre(branchBReady) and time > 2500 then
      mode := MainMode.Idle;
      branchA_coolingDone := false;
      branchA_returnDone := false;
      branchB_waitDone := false;
      branchB_transferDone := false;
      branchB_coolingDone := false;
      branchB_returnDone := false;
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}),Text(extent={{-80,20},{80,-20}}, textString="CTRL") }));
end NaClEvaporationController;
