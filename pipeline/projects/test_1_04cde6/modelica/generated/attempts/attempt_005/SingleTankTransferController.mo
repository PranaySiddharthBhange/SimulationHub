model SingleTankTransferController
  type Mode = enumeration(Idle, FillTank1, WaitAfterFill, TransferToTank2, WaitAfterTransfer, DrainTank2, Paused, ShutdownEmptying, ShutdownComplete);
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,70},{-100,90}}), iconTransformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,35},{-100,55}}), iconTransformation(extent={{-120,35},{-100,55}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,0},{-100,20}}), iconTransformation(extent={{-120,0},{-100,20}})));
  Modelica.Blocks.Interfaces.BooleanInput highLevelReached annotation(Placement(transformation(extent={{-120,-35},{-100,-15}}), iconTransformation(extent={{-120,-35},{-100,-15}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelReachedTank1 annotation(Placement(transformation(extent={{-120,-70},{-100,-50}}), iconTransformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelReachedTank2 annotation(Placement(transformation(extent={{-120,-105},{-100,-85}}), iconTransformation(extent={{-120,-105},{-100,-85}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletOpen annotation(Placement(transformation(extent={{100,60},{120,80}}), iconTransformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput transferOpen annotation(Placement(transformation(extent={{100,20},{120,40}}), iconTransformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput drainOpen annotation(Placement(transformation(extent={{100,-20},{120,0}}), iconTransformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletInhibited annotation(Placement(transformation(extent={{100,-60},{120,-40}}), iconTransformation(extent={{100,-60},{120,-40}})));
  parameter Modelica.Units.SI.Time waitDuration = 10;
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  discrete Mode mode(start=Mode.Idle, fixed=true);
  discrete Mode pausedFrom(start=Mode.Idle, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real pausedWaitRemaining(start=0, fixed=true);
  Real waitElapsed;
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
equation
  startPulse = edge(sample(0, scanPeriod) and startButton);
  stopPulse = edge(sample(0, scanPeriod) and stopButton);
  shutPulse = edge(sample(0, scanPeriod) and shutButton);
  waitElapsed = time - pre(tEnter);

  inletOpen = mode == Mode.FillTank1;
  transferOpen = mode == Mode.TransferToTank2 or mode == Mode.ShutdownEmptying;
  drainOpen = mode == Mode.DrainTank2 or mode == Mode.ShutdownEmptying;
  inletInhibited = mode == Mode.ShutdownEmptying or mode == Mode.ShutdownComplete;
algorithm
  when {startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FillTank1 and highLevelReached,
        pre(mode) == Mode.WaitAfterFill and waitElapsed >= waitDuration,
        pre(mode) == Mode.TransferToTank2 and lowLevelReachedTank1,
        pre(mode) == Mode.WaitAfterTransfer and waitElapsed >= waitDuration,
        pre(mode) == Mode.DrainTank2 and lowLevelReachedTank2,
        pre(mode) == Mode.ShutdownEmptying and lowLevelReachedTank1 and lowLevelReachedTank2} then
    if shutPulse and pre(mode) <> Mode.ShutdownComplete then
      mode := Mode.ShutdownEmptying;
      tEnter := time;
    elseif pre(mode) == Mode.ShutdownEmptying and lowLevelReachedTank1 and lowLevelReachedTank2 then
      mode := Mode.ShutdownComplete;
      tEnter := time;
    elseif stopPulse and pre(mode) <> Mode.Idle and pre(mode) <> Mode.Paused and pre(mode) <> Mode.ShutdownEmptying and pre(mode) <> Mode.ShutdownComplete then
      pausedFrom := pre(mode);
      if pre(mode) == Mode.WaitAfterFill or pre(mode) == Mode.WaitAfterTransfer then
        pausedWaitRemaining := max(0, waitDuration - waitElapsed);
      else
        pausedWaitRemaining := 0;
      end if;
      mode := Mode.Paused;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.Paused then
      mode := pre(pausedFrom);
      if pre(pausedFrom) == Mode.WaitAfterFill or pre(pausedFrom) == Mode.WaitAfterTransfer then
        tEnter := time - (waitDuration - pre(pausedWaitRemaining));
      else
        tEnter := time;
      end if;
    elseif startPulse and pre(mode) == Mode.Idle then
      mode := Mode.FillTank1;
      tEnter := time;
    elseif pre(mode) == Mode.FillTank1 and highLevelReached then
      mode := Mode.WaitAfterFill;
      tEnter := time;
    elseif pre(mode) == Mode.WaitAfterFill and waitElapsed >= waitDuration then
      mode := Mode.TransferToTank2;
      tEnter := time;
    elseif pre(mode) == Mode.TransferToTank2 and lowLevelReachedTank1 then
      mode := Mode.WaitAfterTransfer;
      tEnter := time;
    elseif pre(mode) == Mode.WaitAfterTransfer and waitElapsed >= waitDuration then
      mode := Mode.DrainTank2;
      tEnter := time;
    elseif pre(mode) == Mode.DrainTank2 and lowLevelReachedTank2 then
      mode := Mode.Idle;
      tEnter := time;
    end if;
  end when;
  annotation(Icon(coordinateSystem(extent={{-100,-120},{100,120}}), graphics={Rectangle(extent={{-80,-100},{80,100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-100,110},{100,140}}, textString="%name"), Text(extent={{-60,40},{60,70}}, textString="CTRL"), Text(extent={{-70,-10},{70,20}}, textString="SEQ")}), Diagram(coordinateSystem(extent={{-100,-120},{100,120}})));
end SingleTankTransferController;
