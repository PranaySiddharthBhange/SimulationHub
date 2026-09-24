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
  Real waitElapsed;
equation 
  startSample = sample(0, scanPeriod) and startButton;
  stopSample = sample(0, scanPeriod) and stopButton;
  shutSample = sample(0, scanPeriod) and shutButton;
  startPulse = edge(startSample);
  stopPulse = edge(stopSample);
  shutPulse = edge(shutSample);
  waitElapsed = time - pre(tEnter);

  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL then max(0, waitAfterFill - waitElapsed)
    else if mode == Mode.WAIT_AFTER_TRANSFER then max(0, waitAfterTransfer - waitElapsed)
    else if mode == Mode.WAIT_AFTER_DRAIN then max(0, waitAfterDrain - waitElapsed)
    else 0;

  valve1_open_cmd = mode == Mode.FILL_T1;
  valve2_open_cmd = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  valve3_open_cmd = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;
  controller_state_code = Integer(mode) - 1;

algorithm 
  when {startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FILL_T1 and level1 >= T1_high,
        pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill,
        pre(mode) == Mode.TRANSFER_T1_T2 and level1 <= T1_low,
        pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer,
        pre(mode) == Mode.DRAIN_T2 and level2 <= T2_low,
        pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain,
        pre(mode) == Mode.SHUTDOWN and level1 <= T1_low and level2 <= T2_low} then
    if shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    elseif pre(mode) == Mode.SHUTDOWN and level1 <= T1_low and level2 <= T2_low then
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
      pausedWaitRemaining := if pre(mode) == Mode.WAIT_AFTER_FILL then max(0, waitAfterFill - waitElapsed)
        else if pre(mode) == Mode.WAIT_AFTER_TRANSFER then max(0, waitAfterTransfer - waitElapsed)
        else if pre(mode) == Mode.WAIT_AFTER_DRAIN then max(0, waitAfterDrain - waitElapsed)
        else 0;
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
    elseif pre(mode) == Mode.FILL_T1 and level1 >= T1_high then
      mode := Mode.WAIT_AFTER_FILL;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and level1 <= T1_low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.DRAIN_T2 and level2 <= T2_low then
      mode := Mode.WAIT_AFTER_DRAIN;
      resumeMode := pre(resumeMode);
      pausedWaitRemaining := pre(pausedWaitRemaining);
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain then
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
end PLC101;
