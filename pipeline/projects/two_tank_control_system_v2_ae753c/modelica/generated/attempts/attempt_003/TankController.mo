model TankController
  type Mode = enumeration(IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, SHUTDOWN);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Modelica.Units.SI.Time waitAfterFill_s = 10;
  parameter Modelica.Units.SI.Time waitAfterTransfer_s = 12;
  parameter Modelica.Units.SI.Time waitAfterDrain_s = 8;
  parameter Modelica.Units.SI.Height t1Low_m = 0.05;
  parameter Modelica.Units.SI.Height t2Low_m = 0.05;
  parameter Modelica.Units.SI.Height t1High_m = 0.80;

  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput level1_m annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput level2_m annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));

  Modelica.Blocks.Interfaces.BooleanOutput valve1Cmd annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2Cmd annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3Cmd annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput waitRemaining_s annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
  Modelica.Blocks.Interfaces.IntegerOutput stateCode annotation(Placement(transformation(extent={{100,-110},{120,-90}})));

  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real pausedWaitRemaining(start=0, fixed=true);
  discrete Real activeWaitDuration(start=0, fixed=true);
  Boolean startSample;
  Boolean stopSample;
  Boolean shutSample;
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
  Real rawWaitRemaining;
algorithm
  when initial() then
    mode := Mode.IDLE;
    resumeMode := Mode.IDLE;
    tEnter := 0;
    pausedWaitRemaining := 0;
    activeWaitDuration := 0;
  end when;

  when {startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FILL_T1 and level1_m >= t1High_m,
        pre(mode) == Mode.WAIT_AFTER_FILL and rawWaitRemaining <= 0,
        pre(mode) == Mode.TRANSFER_T1_T2 and level1_m <= t1Low_m,
        pre(mode) == Mode.WAIT_AFTER_TRANSFER and rawWaitRemaining <= 0,
        pre(mode) == Mode.DRAIN_T2 and level2_m <= t2Low_m,
        pre(mode) == Mode.WAIT_AFTER_DRAIN and rawWaitRemaining <= 0,
        pre(mode) == Mode.SHUTDOWN and level1_m <= t1Low_m and level2_m <= t2Low_m} then
    if shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      activeWaitDuration := 0;
      tEnter := time;
    elseif stopPulse and (pre(mode) == Mode.FILL_T1 or pre(mode) == Mode.WAIT_AFTER_FILL or pre(mode) == Mode.TRANSFER_T1_T2 or pre(mode) == Mode.WAIT_AFTER_TRANSFER or pre(mode) == Mode.DRAIN_T2 or pre(mode) == Mode.WAIT_AFTER_DRAIN) then
      mode := Mode.PAUSED;
      resumeMode := pre(mode);
      if pre(mode) == Mode.WAIT_AFTER_FILL or pre(mode) == Mode.WAIT_AFTER_TRANSFER or pre(mode) == Mode.WAIT_AFTER_DRAIN then
        pausedWaitRemaining := max(0, pre(activeWaitDuration) - (time - pre(tEnter)));
      else
        pausedWaitRemaining := 0;
      end if;
    elseif startPulse and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      activeWaitDuration := 0;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.PAUSED then
      mode := pre(resumeMode);
      if pre(resumeMode) == Mode.WAIT_AFTER_FILL or pre(resumeMode) == Mode.WAIT_AFTER_TRANSFER or pre(resumeMode) == Mode.WAIT_AFTER_DRAIN then
        activeWaitDuration := pre(pausedWaitRemaining);
        tEnter := time;
        pausedWaitRemaining := 0;
      elseif pre(resumeMode) == Mode.FILL_T1 or pre(resumeMode) == Mode.TRANSFER_T1_T2 or pre(resumeMode) == Mode.DRAIN_T2 then
        tEnter := time;
      end if;
    elseif pre(mode) == Mode.FILL_T1 and level1_m >= t1High_m then
      mode := Mode.WAIT_AFTER_FILL;
      activeWaitDuration := waitAfterFill_s;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and rawWaitRemaining <= 0 then
      mode := Mode.TRANSFER_T1_T2;
      activeWaitDuration := 0;
      tEnter := time;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and level1_m <= t1Low_m then
      mode := Mode.WAIT_AFTER_TRANSFER;
      activeWaitDuration := waitAfterTransfer_s;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and rawWaitRemaining <= 0 then
      mode := Mode.DRAIN_T2;
      activeWaitDuration := 0;
      tEnter := time;
    elseif pre(mode) == Mode.DRAIN_T2 and level2_m <= t2Low_m then
      mode := Mode.WAIT_AFTER_DRAIN;
      activeWaitDuration := waitAfterDrain_s;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and rawWaitRemaining <= 0 then
      mode := Mode.FILL_T1;
      activeWaitDuration := 0;
      tEnter := time;
    elseif pre(mode) == Mode.SHUTDOWN and level1_m <= t1Low_m and level2_m <= t2Low_m then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      activeWaitDuration := 0;
      tEnter := time;
    end if;
  end when;
equation
  startSample = sample(0, scanPeriod) and startButton;
  stopSample = sample(0, scanPeriod) and stopButton;
  shutSample = sample(0, scanPeriod) and shutButton;
  startPulse = edge(startSample);
  stopPulse = edge(stopSample);
  shutPulse = edge(shutSample);

  rawWaitRemaining = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then activeWaitDuration - (time - pre(tEnter)) else 0;
  waitRemaining_s = max(0, rawWaitRemaining);

  valve1Cmd = mode == Mode.FILL_T1;
  valve2Cmd = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  valve3Cmd = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;

  stateCode = if mode == Mode.IDLE then 0 else if mode == Mode.FILL_T1 then 1 else if mode == Mode.WAIT_AFTER_FILL then 2 else if mode == Mode.TRANSFER_T1_T2 then 3 else if mode == Mode.WAIT_AFTER_TRANSFER then 4 else if mode == Mode.DRAIN_T2 then 5 else if mode == Mode.WAIT_AFTER_DRAIN then 6 else if mode == Mode.PAUSED then 7 else 8;

  annotation(
    Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),Text(extent={{-90,40},{90,80}}, textString="PLC-101"),Text(extent={{-90,0},{90,30}}, textString="START STOP SHUT"),Text(extent={{-90,-40},{90,-10}}, textString="L1 L2 -> V1 V2 V3"),Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255})}));
end TankController;
