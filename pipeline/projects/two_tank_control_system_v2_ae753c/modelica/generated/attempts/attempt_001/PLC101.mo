model PLC101
  type Mode = enumeration(IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, SHUTDOWN);

  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  parameter Modelica.Units.SI.Height T1_low = 0.05;
  parameter Modelica.Units.SI.Height T2_low = 0.05;
  parameter Modelica.Units.SI.Height T1_high = 0.80;
  parameter Modelica.Units.SI.Time waitAfterFill = 10;
  parameter Modelica.Units.SI.Time waitAfterTransfer = 12;
  parameter Modelica.Units.SI.Time waitAfterDrain = 8;

  Modelica.Blocks.Interfaces.RealInput observed_tank1_level_m annotation(Placement(transformation(extent={{-120,50},{-100,70}}), iconTransformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput observed_tank2_level_m annotation(Placement(transformation(extent={{-120,10},{-100,30}}), iconTransformation(extent={{-120,10},{-100,30}})));
  Modelica.Blocks.Interfaces.BooleanInput cmd_start annotation(Placement(transformation(extent={{-120,-30},{-100,-10}}), iconTransformation(extent={{-120,-30},{-100,-10}})));
  Modelica.Blocks.Interfaces.BooleanInput cmd_stop annotation(Placement(transformation(extent={{-120,-60},{-100,-40}}), iconTransformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.BooleanInput cmd_shut annotation(Placement(transformation(extent={{-120,-90},{-100,-70}}), iconTransformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve1_open_cmd annotation(Placement(transformation(extent={{100,50},{120,70}}), iconTransformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2_open_cmd annotation(Placement(transformation(extent={{100,10},{120,30}}), iconTransformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3_open_cmd annotation(Placement(transformation(extent={{100,-30},{120,-10}}), iconTransformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput wait_remaining_s annotation(Placement(transformation(extent={{100,-70},{120,-50}}), iconTransformation(extent={{100,-70},{120,-50}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_state_code annotation(Placement(transformation(extent={{100,-110},{120,-90}}), iconTransformation(extent={{100,-110},{120,-90}})));

protected 
  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.IDLE, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real pausedWaitRemaining(start=0, fixed=true);
  Real activeWaitDuration;
  Real currentWaitElapsed;

equation
  activeWaitDuration = if mode == Mode.WAIT_AFTER_FILL then waitAfterFill elseif mode == Mode.WAIT_AFTER_TRANSFER then waitAfterTransfer elseif mode == Mode.WAIT_AFTER_DRAIN then waitAfterDrain else 0;
  currentWaitElapsed = time - pre(tEnter);
  wait_remaining_s = if mode == Mode.WAIT_AFTER_FILL or mode == Mode.WAIT_AFTER_TRANSFER or mode == Mode.WAIT_AFTER_DRAIN then max(0, activeWaitDuration - currentWaitElapsed) else 0;

  valve1_open_cmd = mode == Mode.FILL_T1;
  valve2_open_cmd = mode == Mode.TRANSFER_T1_T2 or mode == Mode.SHUTDOWN;
  valve3_open_cmd = mode == Mode.DRAIN_T2 or mode == Mode.SHUTDOWN;
  controller_state_code = Integer(mode) - 1;

algorithm
  when {initial(), change(cmd_start), change(cmd_stop), change(cmd_shut), pre(mode) == Mode.FILL_T1 and observed_tank1_level_m >= T1_high, pre(mode) == Mode.WAIT_AFTER_FILL and currentWaitElapsed >= waitAfterFill, pre(mode) == Mode.TRANSFER_T1_T2 and observed_tank1_level_m <= T1_low, pre(mode) == Mode.WAIT_AFTER_TRANSFER and currentWaitElapsed >= waitAfterTransfer, pre(mode) == Mode.DRAIN_T2 and observed_tank2_level_m <= T2_low, pre(mode) == Mode.WAIT_AFTER_DRAIN and currentWaitElapsed >= waitAfterDrain, pre(mode) == Mode.SHUTDOWN and observed_tank1_level_m <= T1_low and observed_tank2_level_m <= T2_low} then
    if initial() then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      tEnter := 0;
      pausedWaitRemaining := 0;
    elseif edge(cmd_shut) and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    elseif edge(cmd_stop) and (pre(mode) == Mode.FILL_T1 or pre(mode) == Mode.WAIT_AFTER_FILL or pre(mode) == Mode.TRANSFER_T1_T2 or pre(mode) == Mode.WAIT_AFTER_TRANSFER or pre(mode) == Mode.DRAIN_T2 or pre(mode) == Mode.WAIT_AFTER_DRAIN) then
      resumeMode := pre(mode);
      if pre(mode) == Mode.WAIT_AFTER_FILL then
        pausedWaitRemaining := max(0, waitAfterFill - (time - pre(tEnter)));
      elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER then
        pausedWaitRemaining := max(0, waitAfterTransfer - (time - pre(tEnter)));
      elseif pre(mode) == Mode.WAIT_AFTER_DRAIN then
        pausedWaitRemaining := max(0, waitAfterDrain - (time - pre(tEnter)));
      else
        pausedWaitRemaining := 0;
      end if;
      mode := Mode.PAUSED;
      tEnter := time;
    elseif edge(cmd_start) and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    elseif edge(cmd_start) and pre(mode) == Mode.PAUSED then
      if pre(resumeMode) == Mode.WAIT_AFTER_FILL then
        mode := Mode.WAIT_AFTER_FILL;
        tEnter := time - (waitAfterFill - pre(pausedWaitRemaining));
      elseif pre(resumeMode) == Mode.WAIT_AFTER_TRANSFER then
        mode := Mode.WAIT_AFTER_TRANSFER;
        tEnter := time - (waitAfterTransfer - pre(pausedWaitRemaining));
      elseif pre(resumeMode) == Mode.WAIT_AFTER_DRAIN then
        mode := Mode.WAIT_AFTER_DRAIN;
        tEnter := time - (waitAfterDrain - pre(pausedWaitRemaining));
      else
        mode := pre(resumeMode);
        tEnter := time;
      end if;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
    elseif pre(mode) == Mode.FILL_T1 and observed_tank1_level_m >= T1_high then
      mode := Mode.WAIT_AFTER_FILL;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and currentWaitElapsed >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
      tEnter := time;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and observed_tank1_level_m <= T1_low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and currentWaitElapsed >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
      tEnter := time;
    elseif pre(mode) == Mode.DRAIN_T2 and observed_tank2_level_m <= T2_low then
      mode := Mode.WAIT_AFTER_DRAIN;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and currentWaitElapsed >= waitAfterDrain then
      mode := Mode.FILL_T1;
      tEnter := time;
    elseif pre(mode) == Mode.SHUTDOWN and observed_tank1_level_m <= T1_low and observed_tank2_level_m <= T2_low then
      mode := Mode.IDLE;
      resumeMode := Mode.IDLE;
      pausedWaitRemaining := 0;
      tEnter := time;
    end if;
  end when;

  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name"),
      Text(extent={{-88,54},{82,20}}, textString="PLC-101"),
      Text(extent={{-94,-6},{94,-38}}, textString="START STOP SHUT")}),
    Diagram(graphics={
      Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,0})}));
end PLC101;
