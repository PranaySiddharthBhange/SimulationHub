model TwoTankController
  extends Modelica.Blocks.Icons.Block;

  type Mode = enumeration(
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
  parameter Modelica.Units.SI.Height T1_High = 0.80;
  parameter Modelica.Units.SI.Height T1_Low = 0.05;
  parameter Modelica.Units.SI.Height T2_Low = 0.05;
  parameter Modelica.Units.SI.Time waitAfterFill = 10;
  parameter Modelica.Units.SI.Time waitAfterTransfer = 12;
  parameter Modelica.Units.SI.Time waitAfterDrain = 8;

  Modelica.Blocks.Interfaces.BooleanInput startButton annotation (Placement(transformation(extent={{-120,70},{-100,90}}), iconTransformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation (Placement(transformation(extent={{-120,30},{-100,50}}), iconTransformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation (Placement(transformation(extent={{-120,-10},{-100,10}}), iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput level1 annotation (Placement(transformation(extent={{-120,-50},{-100,-30}}), iconTransformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput level2 annotation (Placement(transformation(extent={{-120,-90},{-100,-70}}), iconTransformation(extent={{-120,-90},{-100,-70}})));

  Modelica.Blocks.Interfaces.BooleanOutput valve1Open annotation (Placement(transformation(extent={{100,60},{120,80}}), iconTransformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2Open annotation (Placement(transformation(extent={{100,20},{120,40}}), iconTransformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3Open annotation (Placement(transformation(extent={{100,-20},{120,0}}), iconTransformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state_id annotation (Placement(transformation(extent={{100,-60},{120,-40}}), iconTransformation(extent={{100,-60},{120,-40}})));
  Modelica.Blocks.Interfaces.RealOutput wait_remaining_s annotation (Placement(transformation(extent={{100,-100},{120,-80}}), iconTransformation(extent={{100,-100},{120,-80}})));

protected 
  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real storedWaitRemaining(start=0, fixed=true);
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

  activeWaitDuration = if mode == Mode.WAIT_AFTER_FILL then waitAfterFill else if mode == Mode.WAIT_AFTER_TRANSFER then waitAfterTransfer else if mode == Mode.WAIT_AFTER_DRAIN then waitAfterDrain else 0;
  waitElapsed = if mode == Mode.PAUSED then 0 else time - pre(tEnter);

  valve1Open = mode == Mode.FILL_T1;
  valve2Open = (mode == Mode.TRANSFER_T1_T2) or (mode == Mode.SHUTDOWN);
  valve3Open = (mode == Mode.DRAIN_T2) or (mode == Mode.SHUTDOWN);
  controller_state_id = if mode == Mode.IDLE then 0 else if mode == Mode.FILL_T1 then 1 else if mode == Mode.WAIT_AFTER_FILL then 2 else if mode == Mode.TRANSFER_T1_T2 then 3 else if mode == Mode.WAIT_AFTER_TRANSFER then 4 else if mode == Mode.DRAIN_T2 then 5 else if mode == Mode.WAIT_AFTER_DRAIN then 6 else if mode == Mode.PAUSED then 7 else 8;
  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL then max(0, waitAfterFill - (time - pre(tEnter))) else if mode == Mode.WAIT_AFTER_TRANSFER then max(0, waitAfterTransfer - (time - pre(tEnter))) else if mode == Mode.WAIT_AFTER_DRAIN then max(0, waitAfterDrain - (time - pre(tEnter))) else if mode == Mode.PAUSED and (resumeMode == Mode.WAIT_AFTER_FILL or resumeMode == Mode.WAIT_AFTER_TRANSFER or resumeMode == Mode.WAIT_AFTER_DRAIN) then storedWaitRemaining else 0;

algorithm 
  when {initial(), shutPulse, stopPulse, startPulse, pre(mode) == Mode.FILL_T1 and level1 >= T1_High, pre(mode) == Mode.WAIT_AFTER_FILL and time - pre(tEnter) >= waitAfterFill, pre(mode) == Mode.TRANSFER_T1_T2 and level1 <= T1_Low, pre(mode) == Mode.WAIT_AFTER_TRANSFER and time - pre(tEnter) >= waitAfterTransfer, pre(mode) == Mode.DRAIN_T2 and level2 <= T2_Low, pre(mode) == Mode.WAIT_AFTER_DRAIN and time - pre(tEnter) >= waitAfterDrain, pre(mode) == Mode.SHUTDOWN and level1 <= T1_Low and level2 <= T2_Low} then
    if initial() then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      tEnter := 0;
      storedWaitRemaining := 0;
    elseif shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.IDLE;
      storedWaitRemaining := 0;
      tEnter := time;
    elseif stopPulse and (pre(mode) == Mode.FILL_T1 or pre(mode) == Mode.WAIT_AFTER_FILL or pre(mode) == Mode.TRANSFER_T1_T2 or pre(mode) == Mode.WAIT_AFTER_TRANSFER or pre(mode) == Mode.DRAIN_T2 or pre(mode) == Mode.WAIT_AFTER_DRAIN) then
      resumeMode := pre(mode);
      if pre(mode) == Mode.WAIT_AFTER_FILL then
        storedWaitRemaining := max(0, waitAfterFill - (time - pre(tEnter)));
      elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER then
        storedWaitRemaining := max(0, waitAfterTransfer - (time - pre(tEnter)));
      elseif pre(mode) == Mode.WAIT_AFTER_DRAIN then
        storedWaitRemaining := max(0, waitAfterDrain - (time - pre(tEnter)));
      else
        storedWaitRemaining := 0;
      end if;
      mode := Mode.PAUSED;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif startPulse and pre(mode) == Mode.PAUSED then
      if pre(resumeMode) == Mode.FILL_T1 then
        mode := Mode.FILL_T1;
        tEnter := time;
      elseif pre(resumeMode) == Mode.WAIT_AFTER_FILL then
        mode := Mode.WAIT_AFTER_FILL;
        tEnter := time - (waitAfterFill - pre(storedWaitRemaining));
      elseif pre(resumeMode) == Mode.TRANSFER_T1_T2 then
        mode := Mode.TRANSFER_T1_T2;
        tEnter := time;
      elseif pre(resumeMode) == Mode.WAIT_AFTER_TRANSFER then
        mode := Mode.WAIT_AFTER_TRANSFER;
        tEnter := time - (waitAfterTransfer - pre(storedWaitRemaining));
      elseif pre(resumeMode) == Mode.DRAIN_T2 then
        mode := Mode.DRAIN_T2;
        tEnter := time;
      elseif pre(resumeMode) == Mode.WAIT_AFTER_DRAIN then
        mode := Mode.WAIT_AFTER_DRAIN;
        tEnter := time - (waitAfterDrain - pre(storedWaitRemaining));
      end if;
    elseif pre(mode) == Mode.FILL_T1 and level1 >= T1_High then
      mode := Mode.WAIT_AFTER_FILL;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and time - pre(tEnter) >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and level1 <= T1_Low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and time - pre(tEnter) >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.DRAIN_T2 and level2 <= T2_Low then
      mode := Mode.WAIT_AFTER_DRAIN;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and time - pre(tEnter) >= waitAfterDrain then
      mode := Mode.FILL_T1;
      tEnter := time;
      storedWaitRemaining := 0;
    elseif pre(mode) == Mode.SHUTDOWN and level1 <= T1_Low and level2 <= T2_Low then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      tEnter := time;
      storedWaitRemaining := 0;
    end if;
  end when;

  annotation (Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255}, fillColor={235,235,235}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-90,40},{90,80}}, textString="PLC-101"),Text(extent={{-90,0},{90,30}}, textString="START STOP SHUT"),Text(extent={{-90,-40},{90,-10}}, textString="LT-101 LT-102")}), Diagram(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,255})}));
end TwoTankController;
