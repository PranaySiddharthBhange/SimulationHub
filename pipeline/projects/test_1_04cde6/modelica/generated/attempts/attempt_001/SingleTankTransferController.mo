model SingleTankTransferController
  type Mode = enumeration(Idle, FillTank1, WaitAfterFill, TransferToTank2, WaitAfterTransfer, DrainTank2, Paused, ShutdownEmptying, ShutdownComplete);
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,60},{-100,80}}), iconTransformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,20},{-100,40}}), iconTransformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-20},{-100,0}}), iconTransformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.BooleanInput highLevelReached annotation(Placement(transformation(extent={{-120,-60},{-100,-40}}), iconTransformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelReachedTank1 annotation(Placement(transformation(extent={{-120,-90},{-100,-70}}), iconTransformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelReachedTank2 annotation(Placement(transformation(extent={{-120,-120},{-100,-100}}), iconTransformation(extent={{-120,-120},{-100,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletOpen annotation(Placement(transformation(extent={{100,60},{120,80}}), iconTransformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput transferOpen annotation(Placement(transformation(extent={{100,20},{120,40}}), iconTransformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput drainOpen annotation(Placement(transformation(extent={{100,-20},{120,0}}), iconTransformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletInhibited annotation(Placement(transformation(extent={{100,-60},{120,-40}}), iconTransformation(extent={{100,-60},{120,-40}})));
  parameter Modelica.Units.SI.Time waitDuration = 10;
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  discrete Mode mode(start=Mode.Idle, fixed=true);
  discrete Mode pausedFrom(start=Mode.Idle, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
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
  when {startPulse, stopPulse, shutPulse, pre(mode) == Mode.FillTank1 and highLevelReached, pre(mode) == Mode.WaitAfterFill and waitElapsed >= waitDuration, pre(mode) == Mode.TransferToTank2 and lowLevelReachedTank1, pre(mode) == Mode.WaitAfterTransfer and waitElapsed >= waitDuration, pre(mode) == Mode.DrainTank2 and lowLevelReachedTank2, pre(mode) == Mode.ShutdownEmptying and lowLevelReachedTank1 and lowLevelReachedTank2} then
    if shutPulse and pre(mode) <> Mode.ShutdownComplete then
      mode := Mode.ShutdownEmptying;
      tEnter := time;
    elseif pre(mode) == Mode.ShutdownEmptying and lowLevelReachedTank1 and lowLevelReachedTank2 then
      mode := Mode.ShutdownComplete;
      tEnter := time;
    elseif stopPulse and pre(mode) <> Mode.Idle and pre(mode) <> Mode.Paused and pre(mode) <> Mode.ShutdownEmptying and pre(mode) <> Mode.ShutdownComplete then
      pausedFrom := pre(mode);
      mode := Mode.Paused;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.Paused then
      mode := pre(pausedFrom);
      if pre(pausedFrom) == Mode.WaitAfterFill or pre(pausedFrom) == Mode.WaitAfterTransfer then
        tEnter := time - (time - pre(tEnter));
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
  annotation(Icon(coordinateSystem(extent={{-100,-140},{100,140}}), graphics={Rectangle(extent={{-80,-120},{80,120}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-100,130},{100,160}}, textString="%name"), Text(extent={{-70,70},{70,100}}, textString="CTRL"), Text(extent={{-70,30},{70,50}}, textString="START STOP SHUT")}), Diagram(coordinateSystem(extent={{-100,-140},{100,140}})));
end SingleTankTransferController;
