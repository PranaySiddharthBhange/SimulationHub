model PLC101
  type Mode = enumeration(IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, SHUTDOWN);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Modelica.Units.SI.Height T1_high = 0.80;
  parameter Modelica.Units.SI.Height T1_low = 0.05;
  parameter Modelica.Units.SI.Height T2_low = 0.05;
  parameter Modelica.Units.SI.Time waitAfterFill = 10;
  parameter Modelica.Units.SI.Time waitAfterTransfer = 12;
  parameter Modelica.Units.SI.Time waitAfterDrain = 8;

  Modelica.Blocks.Interfaces.RealInput level1 annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput level2 annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-100},{-100,-80}})));

  Modelica.Blocks.Interfaces.BooleanOutput valve1_open_cmd annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2_open_cmd annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3_open_cmd annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput wait_remaining_s annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state_code annotation(Placement(transformation(extent={{100,-100},{120,-80}})));

protected 
  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real pausedWaitRemaining(start=0, fixed=true);
  Boolean startSample;
  Boolean stopSample;
  Boolean shutSample;
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
  Boolean fillDone;
  Boolean waitAfterFillDone;
  Boolean transferDone;
  Boolean waitAfterTransferDone;
  Boolean drainDone;
  Boolean waitAfterDrainDone;
  Boolean shutdownDone;
  Real activeWaitDuration;
  Real activeWaitElapsed;
equation 
  startSample = sample(0, scanPeriod) and startButton;
  stopSample = sample(0, scanPeriod) and stopButton;
  shutSample = sample(0, scanPeriod) and shutButton;
  startPulse = edge(startSample);
  stopPulse = edge(stopSample);
  shutPulse = edge(shutSample);

  activeWaitDuration = if mode == Mode.WAIT_AFTER_FILL then waitAfterFill else if mode == Mode.WAIT_AFTER_TRANSFER then waitAfterTransfer else if mode == Mode.WAIT_AFTER_DRAIN then waitAfterDrain else 0;
  activeWaitElapsed = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then time - pre(tEnter) else 0;
  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then max(0, activeWaitDuration - activeWaitElapsed) else 0;

  fillDone = level1 >= T1_high;
  waitAfterFillDone = pre(mode) == Mode.WAIT_AFTER_FILL and activeWaitElapsed >= waitAfterFill;
  transferDone = level1 <= T1_low;
  waitAfterTransferDone = pre(mode) == Mode.WAIT_AFTER_TRANSFER and activeWaitElapsed >= waitAfterTransfer;
  drainDone = level2 <= T2_low;
  waitAfterDrainDone = pre(mode) == Mode.WAIT_AFTER_DRAIN and activeWaitElapsed >= waitAfterDrain;
  shutdownDone = level1 <= T1_low and level2 <= T2_low;

  valve1_open_cmd = mode == Mode.FILL_T1;
  valve2_open_cmd = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  valve3_open_cmd = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;
  controller_state_code = Integer(mode) - 1;

algorithm 
  when {startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FILL_T1 and fillDone,
        waitAfterFillDone,
        pre(mode) == Mode.TRANSFER_T1_T2 and transferDone,
        waitAfterTransferDone,
        pre(mode) == Mode.DRAIN_T2 and drainDone,
        waitAfterDrainDone,
        pre(mode) == Mode.SHUTDOWN and shutdownDone} then
    if shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    elseif pre(mode) == Mode.SHUTDOWN and shutdownDone then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    elseif pre(mode) == Mode.SHUTDOWN then
      mode := pre(mode);
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := pre(tEnter);
    elseif stopPulse and pre(mode) <> Mode.IDLE and pre(mode) <> Mode.PAUSED then
      mode := Mode.PAUSED;
      resumeMode := pre(mode);
      pausedWaitRemaining := if pre(mode) == Mode.WAIT_AFTER_FILL then max(0, waitAfterFill - (time - pre(tEnter))) else if pre(mode) == Mode.WAIT_AFTER_TRANSFER then max(0, waitAfterTransfer - (time - pre(tEnter))) else if pre(mode) == Mode.WAIT_AFTER_DRAIN then max(0, waitAfterDrain - (time - pre(tEnter))) else 0;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.PAUSED then
      if pre(resumeMode) == Mode.FILL_T1 then
        mode := Mode.FILL_T1;
        resumeMode := Mode.IDLE;
        pausedWaitRemaining := 0;
        tEnter := time;
      elseif pre(resumeMode) == Mode.WAIT_AFTER_FILL then
        mode := Mode.WAIT_AFTER_FILL;
        resumeMode := Mode.IDLE;
        pausedWaitRemaining := 0;
        tEnter := time - (waitAfterFill - pre(pausedWaitRemaining));
      elseif pre(resumeMode) == Mode.TRANSFER_T1_T2 then
        mode := Mode.TRANSFER_T1_T2;
        resumeMode := Mode.IDLE;
        pausedWaitRemaining := 0;
        tEnter := time;
      elseif pre(resumeMode) == Mode.WAIT_AFTER_TRANSFER then
        mode := Mode.WAIT_AFTER_TRANSFER;
        resumeMode := Mode.IDLE;
        pausedWaitRemaining := 0;
        tEnter := time - (waitAfterTransfer - pre(pausedWaitRemaining));
      elseif pre(resumeMode) == Mode.DRAIN_T2 then
        mode := Mode.DRAIN_T2;
        resumeMode := Mode.IDLE;
        pausedWaitRemaining := 0;
        tEnter := time;
      elseif pre(resumeMode) == Mode.WAIT_AFTER_DRAIN then
        mode := Mode.WAIT_AFTER_DRAIN;
        resumeMode := Mode.IDLE;
        pausedWaitRemaining := 0;
        tEnter := time - (waitAfterDrain - pre(pausedWaitRemaining));
      else
        mode := pre(mode);
        resumeMode := pre(resumeMode);
        pausedWaitRemaining := pre(pausedWaitRemaining);
        tEnter := pre(tEnter);
      end if;
    elseif pre(mode) == Mode.FILL_T1 and fillDone then
      mode := Mode.WAIT_AFTER_FILL;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif waitAfterFillDone then
      mode := Mode.TRANSFER_T1_T2;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and transferDone then
      mode := Mode.WAIT_AFTER_TRANSFER;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif waitAfterTransferDone then
      mode := Mode.DRAIN_T2;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.DRAIN_T2 and drainDone then
      mode := Mode.WAIT_AFTER_DRAIN;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif waitAfterDrainDone then
      mode := Mode.FILL_T1;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    else
      mode := pre(mode);
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := pre(tEnter);
    end if;
  end when;

  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-88,50},{88,20}}, textString="PLC-101"),
      Text(extent={{-94,0},{-24,-20}}, textString="L1"),
      Text(extent={{-94,-20},{-24,-40}}, textString="L2"),
      Text(extent={{20,40},{92,20}}, textString="V1"),
      Text(extent={{20,0},{92,-20}}, textString="V2"),
      Text(extent={{20,-40},{92,-60}}, textString="V3")}),
    Diagram(graphics={
      Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,0})}));
end PLC101;
