model TwoTankController
  type State = enumeration(
    IDLE,
    FILL_T1,
    WAIT_AFTER_FILL,
    TRANSFER_T1_T2,
    WAIT_AFTER_TRANSFER,
    DRAIN_T2,
    WAIT_AFTER_DRAIN,
    PAUSED,
    SHUTDOWN);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Modelica.Units.SI.Height t1High = 0.80;
  parameter Modelica.Units.SI.Height t1Low = 0.05;
  parameter Modelica.Units.SI.Height t2Low = 0.05;
  parameter Modelica.Units.SI.Time waitAfterFill = 10;
  parameter Modelica.Units.SI.Time waitAfterTransfer = 12;
  parameter Modelica.Units.SI.Time waitAfterDrain = 8;

  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealInput level1 annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealInput level2 annotation(Placement(transformation(extent={{-120,-100},{-100,-80}})));

  Modelica.Blocks.Interfaces.BooleanOutput valve1 annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2 annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3 annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput waitRemaining annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
  Modelica.Blocks.Interfaces.IntegerOutput stateCode annotation(Placement(transformation(extent={{100,-100},{120,-80}})));

  discrete State mode(start=State.IDLE, fixed=true);
  discrete State resumeMode(start=State.IDLE, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real storedWaitRemaining(start=0, fixed=true);
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
  Real activeWaitDuration;
  Real rawWaitRemaining;
equation
  startPulse = edge(startButton);
  stopPulse = edge(stopButton);
  shutPulse = edge(shutButton);

  activeWaitDuration = if mode == State.WAIT_AFTER_FILL then waitAfterFill else if mode == State.WAIT_AFTER_TRANSFER then waitAfterTransfer else if mode == State.WAIT_AFTER_DRAIN then waitAfterDrain else 0;
  rawWaitRemaining = if mode == State.WAIT_AFTER_FILL or mode == State.WAIT_AFTER_TRANSFER or mode == State.WAIT_AFTER_DRAIN then max(0, activeWaitDuration - (time - pre(tEnter))) else 0;
  waitRemaining = rawWaitRemaining;

  valve1 = mode == State.FILL_T1;
  valve2 = mode == State.TRANSFER_T1_T2 or mode == State.SHUTDOWN;
  valve3 = mode == State.DRAIN_T2 or mode == State.SHUTDOWN;
  stateCode = Integer(mode) - 1;
algorithm
  when {shutPulse,
        stopPulse,
        startPulse,
        pre(mode) == State.FILL_T1 and level1 >= t1High,
        pre(mode) == State.WAIT_AFTER_FILL and time - pre(tEnter) >= waitAfterFill,
        pre(mode) == State.TRANSFER_T1_T2 and level1 <= t1Low,
        pre(mode) == State.WAIT_AFTER_TRANSFER and time - pre(tEnter) >= waitAfterTransfer,
        pre(mode) == State.DRAIN_T2 and level2 <= t2Low,
        pre(mode) == State.WAIT_AFTER_DRAIN and time - pre(tEnter) >= waitAfterDrain,
        pre(mode) == State.SHUTDOWN and level1 <= t1Low and level2 <= t2Low} then
    if shutPulse and pre(mode) <> State.SHUTDOWN then
      mode := State.SHUTDOWN;
      resumeMode := State.IDLE;
      storedWaitRemaining := 0;
    elseif pre(mode) <> State.SHUTDOWN and stopPulse and pre(mode) <> State.IDLE and pre(mode) <> State.PAUSED then
      if pre(mode) == State.WAIT_AFTER_FILL then
        storedWaitRemaining := max(0, waitAfterFill - (time - pre(tEnter)));
      elseif pre(mode) == State.WAIT_AFTER_TRANSFER then
        storedWaitRemaining := max(0, waitAfterTransfer - (time - pre(tEnter)));
      elseif pre(mode) == State.WAIT_AFTER_DRAIN then
        storedWaitRemaining := max(0, waitAfterDrain - (time - pre(tEnter)));
      else
        storedWaitRemaining := 0;
      end if;
      resumeMode := pre(mode);
      mode := State.PAUSED;
    elseif pre(mode) == State.PAUSED and startPulse then
      mode := pre(resumeMode);
      if pre(resumeMode) == State.WAIT_AFTER_FILL then
        tEnter := time - (waitAfterFill - pre(storedWaitRemaining));
      elseif pre(resumeMode) == State.WAIT_AFTER_TRANSFER then
        tEnter := time - (waitAfterTransfer - pre(storedWaitRemaining));
      elseif pre(resumeMode) == State.WAIT_AFTER_DRAIN then
        tEnter := time - (waitAfterDrain - pre(storedWaitRemaining));
      end if;
    elseif pre(mode) == State.IDLE and startPulse then
      mode := State.FILL_T1;
    elseif pre(mode) == State.FILL_T1 and level1 >= t1High then
      mode := State.WAIT_AFTER_FILL;
      tEnter := time;
    elseif pre(mode) == State.WAIT_AFTER_FILL and time - pre(tEnter) >= waitAfterFill then
      mode := State.TRANSFER_T1_T2;
    elseif pre(mode) == State.TRANSFER_T1_T2 and level1 <= t1Low then
      mode := State.WAIT_AFTER_TRANSFER;
      tEnter := time;
    elseif pre(mode) == State.WAIT_AFTER_TRANSFER and time - pre(tEnter) >= waitAfterTransfer then
      mode := State.DRAIN_T2;
    elseif pre(mode) == State.DRAIN_T2 and level2 <= t2Low then
      mode := State.WAIT_AFTER_DRAIN;
      tEnter := time;
    elseif pre(mode) == State.WAIT_AFTER_DRAIN and time - pre(tEnter) >= waitAfterDrain then
      mode := State.FILL_T1;
    elseif pre(mode) == State.SHUTDOWN and level1 <= t1Low and level2 <= t2Low then
      mode := State.IDLE;
      resumeMode := State.IDLE;
      storedWaitRemaining := 0;
    end if;
  end when;
annotation(
  Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),Text(extent={{-90,30},{90,-10}}, textString="PLC-101"),Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-96,92},{92,76}}, textString="Two-Tank Fill/Transfer/Drain Controller")}));
end TwoTankController;
