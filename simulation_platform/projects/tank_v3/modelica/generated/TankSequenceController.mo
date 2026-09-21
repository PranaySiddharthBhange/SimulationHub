model TankSequenceController
  extends Modelica.Blocks.Icons.Block;
  type Mode = enumeration(IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, SHUTDOWN);
  parameter Real h1High(unit="m") = 0.80;
  parameter Real h1Low(unit="m") = 0.05;
  parameter Real h2Low(unit="m") = 0.05;
  parameter Real waitAfterFill(unit="s") = 10.0;
  parameter Real waitAfterTransfer(unit="s") = 12.0;
  parameter Real waitAfterDrain(unit="s") = 8.0;
  Modelica.Blocks.Interfaces.RealInput h1(unit="m") annotation(Placement(transformation(extent={{-120,60},{-80,100}})));
  Modelica.Blocks.Interfaces.RealInput h2(unit="m") annotation(Placement(transformation(extent={{-120,10},{-80,50}})));
  Modelica.Blocks.Interfaces.BooleanInput pbStart annotation(Placement(transformation(extent={{-120,-40},{-80,0}})));
  Modelica.Blocks.Interfaces.BooleanInput pbStop annotation(Placement(transformation(extent={{-120,-90},{-80,-50}})));
  Modelica.Blocks.Interfaces.BooleanInput pbShut annotation(Placement(transformation(extent={{-120,-140},{-80,-100}})));
  Modelica.Blocks.Interfaces.BooleanOutput u1 annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.BooleanOutput u2 annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput u3 annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput wait_remaining_s annotation(Placement(transformation(extent={{100,-80},{120,-60}})));
  Modelica.Blocks.Interfaces.RealOutput state_is_IDLE annotation(Placement(transformation(extent={{100,-120},{120,-100}})));
  Modelica.Blocks.Interfaces.RealOutput state_is_PAUSED annotation(Placement(transformation(extent={{100,-150},{120,-130}})));
  Modelica.Blocks.Interfaces.RealOutput state_is_SHUTDOWN annotation(Placement(transformation(extent={{100,-180},{120,-160}})));
  output Mode mode(start=Mode.IDLE);
protected 
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  Real remainingTimer(start=0, fixed=true);
  Real timerElapsed(start=0, fixed=true);
  Boolean startCmd;
  Boolean stopCmd;
  Boolean shutCmd;
  Boolean startPulse;
  Boolean stopPulse;
  Boolean shutPulse;
equation 
  der(timerElapsed) = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then 1 else 0;
  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL then max(0, waitAfterFill - timerElapsed)
                     else if mode == Mode.WAIT_AFTER_TRANSFER then max(0, waitAfterTransfer - timerElapsed)
                     else if mode == Mode.WAIT_AFTER_DRAIN then max(0, waitAfterDrain - timerElapsed)
                     else if mode == Mode.PAUSED then remainingTimer else 0;
  startCmd = pbStart;
  stopCmd = pbStop;
  shutCmd = pbShut;
  startPulse = startCmd and not pre(startCmd);
  stopPulse = stopCmd and not pre(stopCmd);
  shutPulse = shutCmd and not pre(shutCmd);
  u1 = mode == Mode.FILL_T1;
  u2 = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  u3 = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;
  state_is_IDLE = if mode == Mode.IDLE then 1.0 else 0.0;
  state_is_PAUSED = if mode == Mode.PAUSED then 1.0 else 0.0;
  state_is_SHUTDOWN = if mode == Mode.SHUTDOWN then 1.0 else 0.0;
  when mode == Mode.WAIT_AFTER_FILL and pre(mode) <> Mode.WAIT_AFTER_FILL then
    reinit(timerElapsed, 0.0);
  end when;
  when mode == Mode.WAIT_AFTER_TRANSFER and pre(mode) <> Mode.WAIT_AFTER_TRANSFER then
    reinit(timerElapsed, 0.0);
  end when;
  when mode == Mode.WAIT_AFTER_DRAIN and pre(mode) <> Mode.WAIT_AFTER_DRAIN then
    reinit(timerElapsed, 0.0);
  end when;
algorithm 
  when {startPulse, stopPulse, shutPulse,
        pre(mode) == Mode.FILL_T1 and h1 >= h1High,
        pre(mode) == Mode.WAIT_AFTER_FILL and timerElapsed >= waitAfterFill,
        pre(mode) == Mode.TRANSFER_T1_T2 and h1 <= h1Low,
        pre(mode) == Mode.WAIT_AFTER_TRANSFER and timerElapsed >= waitAfterTransfer,
        pre(mode) == Mode.DRAIN_T2 and h2 <= h2Low,
        pre(mode) == Mode.WAIT_AFTER_DRAIN and timerElapsed >= waitAfterDrain,
        pre(mode) == Mode.SHUTDOWN and h1 <= h1Low and h2 <= h2Low} then
    if pre(mode) == Mode.SHUTDOWN and h1 <= h1Low and h2 <= h2Low then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      remainingTimer := 0.0;
    elseif shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.SHUTDOWN;
      remainingTimer := 0.0;
    elseif pre(mode) == Mode.SHUTDOWN then
      mode := pre(mode);
      resumeMode := pre(resumeMode);
      remainingTimer := pre(remainingTimer);
    elseif stopPulse and pre(mode) <> Mode.IDLE and pre(mode) <> Mode.PAUSED then
      mode := Mode.PAUSED;
      if pre(mode) == Mode.WAIT_AFTER_FILL then
        resumeMode := Mode.WAIT_AFTER_FILL;
        remainingTimer := max(0.0, waitAfterFill - timerElapsed);
      elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER then
        resumeMode := Mode.WAIT_AFTER_TRANSFER;
        remainingTimer := max(0.0, waitAfterTransfer - timerElapsed);
      elseif pre(mode) == Mode.WAIT_AFTER_DRAIN then
        resumeMode := Mode.WAIT_AFTER_DRAIN;
        remainingTimer := max(0.0, waitAfterDrain - timerElapsed);
      else
        resumeMode := pre(mode);
        remainingTimer := 0.0;
      end if;
    elseif startPulse and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      resumeMode := Mode.FILL_T1;
      remainingTimer := 0.0;
    elseif startPulse and pre(mode) == Mode.PAUSED then
      mode := pre(resumeMode);
      resumeMode := pre(resumeMode);
      remainingTimer := pre(remainingTimer);
    elseif pre(mode) == Mode.FILL_T1 and h1 >= h1High then
      mode := Mode.WAIT_AFTER_FILL;
      resumeMode := Mode.WAIT_AFTER_FILL;
      remainingTimer := waitAfterFill;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and timerElapsed >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
      resumeMode := Mode.TRANSFER_T1_T2;
      remainingTimer := 0.0;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and h1 <= h1Low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      resumeMode := Mode.WAIT_AFTER_TRANSFER;
      remainingTimer := waitAfterTransfer;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and timerElapsed >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
      resumeMode := Mode.DRAIN_T2;
      remainingTimer := 0.0;
    elseif pre(mode) == Mode.DRAIN_T2 and h2 <= h2Low then
      mode := Mode.WAIT_AFTER_DRAIN;
      resumeMode := Mode.WAIT_AFTER_DRAIN;
      remainingTimer := waitAfterDrain;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and timerElapsed >= waitAfterDrain then
      mode := Mode.FILL_T1;
      resumeMode := Mode.FILL_T1;
      remainingTimer := 0.0;
    else
      mode := pre(mode);
      resumeMode := pre(resumeMode);
      remainingTimer := pre(remainingTimer);
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,0,0}, fillColor={255,248,220}, fillPattern=FillPattern.Solid),
                           Text(extent={{-90,60},{90,20}}, textString="PLC-101"),
                           Text(extent={{-94,6},{94,-26}}, textString="Seq"),
                           Ellipse(extent={{-20,-60},{20,-100}}, lineColor={0,0,0}, fillColor={255,255,255}, fillPattern=FillPattern.Solid)}),
             Diagram(graphics={Text(extent={{-100,112},{102,94}}, textString="Two-tank sequence controller with pause/resume and shutdown")}) );
end TankSequenceController;
