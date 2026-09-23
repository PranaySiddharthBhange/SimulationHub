model TransferController
  type Mode = enumeration(Idle, FillTank1, WaitAfterFill, TransferToTank2, WaitAfterTransfer, DrainTank2, Paused, ShutdownEmptying, ShutdownComplete);
  parameter Modelica.Units.SI.Time waitDuration = 10;
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.BooleanInput highLevelTank1 annotation(Placement(transformation(extent={{-120,-80},{-100,-60}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelTank1 annotation(Placement(transformation(extent={{-120,-110},{-100,-90}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelTank2 annotation(Placement(transformation(extent={{-120,-140},{-100,-120}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletOpen annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput transferOpen annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.BooleanOutput drainOpen annotation(Placement(transformation(extent={{100,-40},{120,-20}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletInhibited annotation(Placement(transformation(extent={{100,-90},{120,-70}})));
  Modelica.Blocks.Interfaces.IntegerOutput sequenceState annotation(Placement(transformation(extent={{100,-140},{120,-120}})));
protected 
  discrete Mode mode(start=Mode.Idle, fixed=true);
  discrete Mode pausedFrom(start=Mode.Idle, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real waitRemaining(start=0, fixed=true);
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
  Real waitElapsed;
equation
  startPulse = edge(sample(0, scanPeriod) and startButton);
  stopPulse = edge(sample(0, scanPeriod) and stopButton);
  shutPulse = edge(sample(0, scanPeriod) and shutButton);
  waitElapsed = time - pre(tEnter);

  inletOpen = mode == Mode.FillTank1;
  transferOpen = mode == Mode.TransferToTank2 or mode == Mode.ShutdownEmptying;
  drainOpen = mode == Mode.DrainTank2 or mode == Mode.ShutdownEmptying;
  inletInhibited = mode == Mode.ShutdownEmptying or mode == Mode.ShutdownComplete;
  sequenceState = if mode == Mode.Idle then 1 else if mode == Mode.FillTank1 then 2 else if mode == Mode.WaitAfterFill then 3 else if mode == Mode.TransferToTank2 then 4 else if mode == Mode.WaitAfterTransfer then 5 else if mode == Mode.DrainTank2 then 6 else if mode == Mode.Paused then 7 else if mode == Mode.ShutdownEmptying then 8 else 9;
algorithm
  when {initial(), startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FillTank1 and highLevelTank1,
        pre(mode) == Mode.WaitAfterFill and waitElapsed >= waitDuration,
        pre(mode) == Mode.TransferToTank2 and lowLevelTank1,
        pre(mode) == Mode.WaitAfterTransfer and waitElapsed >= waitDuration,
        pre(mode) == Mode.DrainTank2 and lowLevelTank2,
        pre(mode) == Mode.ShutdownEmptying and lowLevelTank1 and lowLevelTank2} then
    if initial() then
      mode := Mode.Idle;
      pausedFrom := Mode.Idle;
      tEnter := 0;
      waitRemaining := 0;
    elseif shutPulse and pre(mode) <> Mode.ShutdownComplete then
      mode := Mode.ShutdownEmptying;
      pausedFrom := pre(mode);
      tEnter := pre(tEnter);
      waitRemaining := if pre(mode) == Mode.WaitAfterFill or pre(mode) == Mode.WaitAfterTransfer then waitDuration - (time - pre(tEnter)) else pre(waitRemaining);
    elseif pre(mode) == Mode.ShutdownEmptying and lowLevelTank1 and lowLevelTank2 then
      mode := Mode.ShutdownComplete;
      pausedFrom := pre(pausedFrom);
      tEnter := pre(tEnter);
      waitRemaining := pre(waitRemaining);
    elseif stopPulse and pre(mode) <> Mode.Idle and pre(mode) <> Mode.ShutdownEmptying and pre(mode) <> Mode.ShutdownComplete and pre(mode) <> Mode.Paused then
      mode := Mode.Paused;
      pausedFrom := pre(mode);
      if pre(mode) == Mode.WaitAfterFill or pre(mode) == Mode.WaitAfterTransfer then
        waitRemaining := waitDuration - (time - pre(tEnter));
      else
        waitRemaining := pre(waitRemaining);
      end if;
      tEnter := pre(tEnter);
    elseif startPulse and pre(mode) == Mode.Paused then
      mode := pre(pausedFrom);
      pausedFrom := pre(pausedFrom);
      if pre(pausedFrom) == Mode.WaitAfterFill or pre(pausedFrom) == Mode.WaitAfterTransfer then
        tEnter := time - (waitDuration - pre(waitRemaining));
        waitRemaining := pre(waitRemaining);
      else
        tEnter := time;
        waitRemaining := pre(waitRemaining);
      end if;
    elseif startPulse and pre(mode) == Mode.Idle then
      mode := Mode.FillTank1;
      pausedFrom := pre(pausedFrom);
      tEnter := time;
      waitRemaining := 0;
    elseif pre(mode) == Mode.FillTank1 and highLevelTank1 then
      mode := Mode.WaitAfterFill;
      pausedFrom := pre(pausedFrom);
      tEnter := time;
      waitRemaining := waitDuration;
    elseif pre(mode) == Mode.WaitAfterFill and waitElapsed >= waitDuration then
      mode := Mode.TransferToTank2;
      pausedFrom := pre(pausedFrom);
      tEnter := time;
      waitRemaining := 0;
    elseif pre(mode) == Mode.TransferToTank2 and lowLevelTank1 then
      mode := Mode.WaitAfterTransfer;
      pausedFrom := pre(pausedFrom);
      tEnter := time;
      waitRemaining := waitDuration;
    elseif pre(mode) == Mode.WaitAfterTransfer and waitElapsed >= waitDuration then
      mode := Mode.DrainTank2;
      pausedFrom := pre(pausedFrom);
      tEnter := time;
      waitRemaining := 0;
    elseif pre(mode) == Mode.DrainTank2 and lowLevelTank2 then
      mode := Mode.Idle;
      pausedFrom := pre(pausedFrom);
      tEnter := time;
      waitRemaining := 0;
    end if;
  end when;
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-90,50},{90,80}}, textString="SEQ"),
    Text(extent={{-94,8},{-22,24}}, textString="START"),
    Text(extent={{-94,-42},{-22,-26}}, textString="STOP"),
    Text(extent={{-94,-92},{-22,-76}}, textString="SHUT")}),
  Diagram(graphics={Text(extent={{-94,146},{96,164}}, textString="Discrete sequence controller with pause/resume and shutdown override")})
);
end TransferController;
