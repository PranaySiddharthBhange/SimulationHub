model PLC101
  type Mode = enumeration(IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, SHUTDOWN);
  Modelica.Blocks.Interfaces.RealInput level1 annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput level2 annotation(Placement(transformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-110},{-100,-90}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve1 annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2 annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3 annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput controller_state_id annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
  Modelica.Blocks.Interfaces.RealOutput wait_remaining_s annotation(Placement(transformation(extent={{100,-110},{120,-90}})));
  parameter Modelica.Units.SI.Height t1High = 0.80;
  parameter Modelica.Units.SI.Height t1Low = 0.05;
  parameter Modelica.Units.SI.Height t2Low = 0.05;
  parameter Modelica.Units.SI.Time waitAfterFill = 10;
  parameter Modelica.Units.SI.Time waitAfterTransfer = 12;
  parameter Modelica.Units.SI.Time waitAfterDrain = 8;
  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real storedWaitRemaining(start=0, fixed=true);
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
  Real activeWaitDuration;
  Real waitElapsed;
equation
  startPulse = edge(startButton);
  stopPulse = edge(stopButton);
  shutPulse = edge(shutButton);
  activeWaitDuration = if mode == Mode.WAIT_AFTER_FILL then waitAfterFill else if mode == Mode.WAIT_AFTER_TRANSFER then waitAfterTransfer else if mode == Mode.WAIT_AFTER_DRAIN then waitAfterDrain else 0;
  waitElapsed = time - pre(tEnter);
  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then max(0, activeWaitDuration - waitElapsed) else if mode == Mode.PAUSED and (resumeMode == Mode.WAIT_AFTER_FILL or resumeMode == Mode.WAIT_AFTER_TRANSFER or resumeMode == Mode.WAIT_AFTER_DRAIN) then storedWaitRemaining else 0;
  valve1 = mode == Mode.FILL_T1;
  valve2 = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  valve3 = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;
  controller_state_id = if mode == Mode.IDLE then 0 else if mode == Mode.FILL_T1 then 1 else if mode == Mode.WAIT_AFTER_FILL then 2 else if mode == Mode.TRANSFER_T1_T2 then 3 else if mode == Mode.WAIT_AFTER_TRANSFER then 4 else if mode == Mode.DRAIN_T2 then 5 else if mode == Mode.WAIT_AFTER_DRAIN then 6 else if mode == Mode.PAUSED then 7 else 8;
algorithm
  when {shutPulse,stopPulse,startPulse,pre(mode) == Mode.FILL_T1 and level1 >= t1High,pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill,pre(mode) == Mode.TRANSFER_T1_T2 and level1 <= t1Low,pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer,pre(mode) == Mode.DRAIN_T2 and level2 <= t2Low,pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain,pre(mode) == Mode.SHUTDOWN and level1 <= t1Low and level2 <= t2Low} then
    if shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.IDLE;
      storedWaitRemaining := 0;
      tEnter := time;
    elseif pre(mode) <> Mode.SHUTDOWN and stopPulse and (pre(mode) == Mode.FILL_T1 or pre(mode) == Mode.WAIT_AFTER_FILL or pre(mode) == Mode.TRANSFER_T1_T2 or pre(mode) == Mode.WAIT_AFTER_TRANSFER or pre(mode) == Mode.DRAIN_T2 or pre(mode) == Mode.WAIT_AFTER_DRAIN) then
      mode := Mode.PAUSED;
      resumeMode := pre(mode);
      if pre(mode) == Mode.WAIT_AFTER_FILL then
        storedWaitRemaining := max(0, waitAfterFill - waitElapsed);
      elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER then
        storedWaitRemaining := max(0, waitAfterTransfer - waitElapsed);
      elseif pre(mode) == Mode.WAIT_AFTER_DRAIN then
        storedWaitRemaining := max(0, waitAfterDrain - waitElapsed);
      else
        storedWaitRemaining := 0;
      end if;
      tEnter := time;
    elseif pre(mode) == Mode.PAUSED and startPulse then
      mode := pre(resumeMode);
      if pre(resumeMode) == Mode.WAIT_AFTER_FILL then
        tEnter := time - (waitAfterFill - pre(storedWaitRemaining));
      elseif pre(resumeMode) == Mode.WAIT_AFTER_TRANSFER then
        tEnter := time - (waitAfterTransfer - pre(storedWaitRemaining));
      elseif pre(resumeMode) == Mode.WAIT_AFTER_DRAIN then
        tEnter := time - (waitAfterDrain - pre(storedWaitRemaining));
      else
        tEnter := time;
      end if;
    elseif pre(mode) == Mode.IDLE and startPulse then
      mode := Mode.FILL_T1;
      resumeMode := Mode.IDLE;
      storedWaitRemaining := 0;
      tEnter := time;
    elseif pre(mode) == Mode.FILL_T1 and level1 >= t1High then
      mode := Mode.WAIT_AFTER_FILL;
      tEnter := time;
      storedWaitRemaining := waitAfterFill;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and level1 <= t1Low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      tEnter := time;
      storedWaitRemaining := waitAfterTransfer;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.DRAIN_T2 and level2 <= t2Low then
      mode := Mode.WAIT_AFTER_DRAIN;
      tEnter := time;
      storedWaitRemaining := waitAfterDrain;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain then
      mode := Mode.FILL_T1;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.SHUTDOWN and level1 <= t1Low and level2 <= t2Low then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      storedWaitRemaining := 0;
      tEnter := time;
    end if;
  end when;
annotation(
  Icon(graphics={Rectangle(extent={{-100,80},{100,-80}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),Text(extent={{-96,40},{-20,58}}, textString="L1"),Text(extent={{-96,0},{-20,18}}, textString="L2"),Text(extent={{-96,-40},{-20,-22}}, textString="START"),Text(extent={{-96,-80},{-20,-62}}, textString="STOP"),Text(extent={{-96,-120},{-20,-102}}, textString="SHUT"),Text(extent={{20,40},{96,58}}, textString="V1"),Text(extent={{20,0},{96,18}}, textString="V2"),Text(extent={{20,-40},{96,-22}}, textString="V3"),Text(extent={{-100,100},{100,140}}, textString="%name")}),
  Diagram(graphics={Text(extent={{-18,14},{20,-10}}, textString="PLC-101") }));
end PLC101;
