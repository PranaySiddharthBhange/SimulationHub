model PLC101
  type Mode = enumeration(IDLE,FILL_T1,WAIT_AFTER_FILL,TRANSFER_T1_T2,WAIT_AFTER_TRANSFER,DRAIN_T2,WAIT_AFTER_DRAIN,PAUSED,SHUTDOWN);
  parameter Modelica.Units.SI.Time scanPeriod=0.1;
  parameter Modelica.Units.SI.Height T1_High=0.80;
  parameter Modelica.Units.SI.Height T1_Low=0.05;
  parameter Modelica.Units.SI.Height T2_Low=0.05;
  parameter Modelica.Units.SI.Time waitAfterFill=10.0;
  parameter Modelica.Units.SI.Time waitAfterTransfer=12.0;
  parameter Modelica.Units.SI.Time waitAfterDrain=8.0;
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput LT101_level_m annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput LT102_level_m annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve1_cmd annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2_cmd annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3_cmd annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state_id annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
  Modelica.Blocks.Interfaces.RealOutput wait_remaining_s annotation(Placement(transformation(extent={{100,-100},{120,-80}})));
protected
  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  discrete Real tEnter(start=0.0, fixed=true);
  discrete Real storedWaitRemaining(start=0.0, fixed=true);
  Boolean startSample;
  Boolean stopSample;
  Boolean shutSample;
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
  Real activeWaitDuration;
  Real waitElapsed;
equation
  startSample = sample(0, scanPeriod) and startButton;
  stopSample = sample(0, scanPeriod) and stopButton;
  shutSample = sample(0, scanPeriod) and shutButton;
  startPulse = edge(startSample);
  stopPulse = edge(stopSample);
  shutPulse = edge(shutSample);
  activeWaitDuration = if mode == Mode.WAIT_AFTER_FILL then waitAfterFill else if mode == Mode.WAIT_AFTER_TRANSFER then waitAfterTransfer else if mode == Mode.WAIT_AFTER_DRAIN then waitAfterDrain else 0.0;
  waitElapsed = time - pre(tEnter);
  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then max(0.0, activeWaitDuration - waitElapsed) else if mode == Mode.PAUSED and (resumeMode == Mode.WAIT_AFTER_FILL or resumeMode == Mode.WAIT_AFTER_TRANSFER or resumeMode == Mode.WAIT_AFTER_DRAIN) then storedWaitRemaining else 0.0;
  valve1_cmd = mode == Mode.FILL_T1;
  valve2_cmd = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  valve3_cmd = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;
  controller_state_id = if mode == Mode.IDLE then 0 else if mode == Mode.FILL_T1 then 1 else if mode == Mode.WAIT_AFTER_FILL then 2 else if mode == Mode.TRANSFER_T1_T2 then 3 else if mode == Mode.WAIT_AFTER_TRANSFER then 4 else if mode == Mode.DRAIN_T2 then 5 else if mode == Mode.WAIT_AFTER_DRAIN then 6 else if mode == Mode.PAUSED then 7 else 8;
algorithm
  when {startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FILL_T1 and LT101_level_m >= T1_High,
        pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill,
        pre(mode) == Mode.TRANSFER_T1_T2 and LT101_level_m <= T1_Low,
        pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer,
        pre(mode) == Mode.DRAIN_T2 and LT102_level_m <= T2_Low,
        pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain,
        pre(mode) == Mode.SHUTDOWN and LT101_level_m <= T1_Low and LT102_level_m <= T2_Low} then
    if shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.SHUTDOWN;
      storedWaitRemaining := 0.0;
      tEnter := time;
    elseif stopPulse and (pre(mode) == Mode.FILL_T1 or pre(mode) == Mode.WAIT_AFTER_FILL or pre(mode) == Mode.TRANSFER_T1_T2 or pre(mode) == Mode.WAIT_AFTER_TRANSFER or pre(mode) == Mode.DRAIN_T2 or pre(mode) == Mode.WAIT_AFTER_DRAIN) then
      resumeMode := pre(mode);
      if pre(mode) == Mode.WAIT_AFTER_FILL then
        storedWaitRemaining := max(0.0, waitAfterFill - (time - pre(tEnter)));
      elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER then
        storedWaitRemaining := max(0.0, waitAfterTransfer - (time - pre(tEnter)));
      elseif pre(mode) == Mode.WAIT_AFTER_DRAIN then
        storedWaitRemaining := max(0.0, waitAfterDrain - (time - pre(tEnter)));
      else
        storedWaitRemaining := 0.0;
      end if;
      mode := Mode.PAUSED;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.PAUSED then
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
    elseif pre(mode) == Mode.FILL_T1 and LT101_level_m >= T1_High then
      mode := Mode.WAIT_AFTER_FILL;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
      tEnter := time;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and LT101_level_m <= T1_Low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
      tEnter := time;
    elseif pre(mode) == Mode.DRAIN_T2 and LT102_level_m <= T2_Low then
      mode := Mode.WAIT_AFTER_DRAIN;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain then
      mode := Mode.FILL_T1;
      tEnter := time;
    elseif pre(mode) == Mode.SHUTDOWN and LT101_level_m <= T1_Low and LT102_level_m <= T2_Low then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      storedWaitRemaining := 0.0;
      tEnter := time;
    end if;
  end when;
  annotation(
    Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),Text(extent={{-96,58},{-22,82}}, textString="START"),Text(extent={{-96,18},{-22,42}}, textString="STOP"),Text(extent={{-96,-22},{-22,2}}, textString="SHUT"),Text(extent={{-96,-62},{-16,-38}}, textString="LT101"),Text(extent={{-96,-100},{-16,-76}}, textString="LT102"),Text(extent={{20,48},{94,72}}, textString="V1"),Text(extent={{20,10},{94,34}}, textString="V2"),Text(extent={{20,-30},{94,-6}}, textString="V3"),Text(extent={{4,-70},{96,-46}}, textString="STATE"),Text(extent={{-10,-100},{96,-78}}, textString="WAIT"),Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end PLC101;
