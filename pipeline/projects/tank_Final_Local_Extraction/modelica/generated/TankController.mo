model TankController
  import Modelica.Units.SI;
  extends Modelica.Blocks.Icons.Block;
  type Mode = enumeration(IDLE, FILL_T1, WAIT_AFTER_FILL, TRANSFER_T1_T2, WAIT_AFTER_TRANSFER, DRAIN_T2, WAIT_AFTER_DRAIN, PAUSED, SHUTDOWN);
  parameter SI.Height t1High = 0.80;
  parameter SI.Height t1Low = 0.05;
  parameter SI.Height t2Low = 0.05;
  parameter SI.Time waitAfterFill = 10;
  parameter SI.Time waitAfterTransfer = 10;
  parameter SI.Time waitAfterDrain = 8;
  parameter SI.Time scanPeriod = 0.1;
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput tank1Level annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealInput tank2Level annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve1Cmd annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve2Cmd annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.BooleanOutput valve3Cmd annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  discrete Mode mode(start=Mode.IDLE, fixed=true);
  discrete Mode resumeMode(start=Mode.FILL_T1, fixed=true);
  discrete SI.Time tEnter(start=0, fixed=true);
  discrete SI.Time remainingWait(start=0, fixed=true);
  discrete Boolean startSample(start=false, fixed=true);
  discrete Boolean stopSample(start=false, fixed=true);
  discrete Boolean shutSample(start=false, fixed=true);
  discrete Boolean startPulse(start=false, fixed=true);
  discrete Boolean stopPulse(start=false, fixed=true);
  discrete Boolean shutPulse(start=false, fixed=true);
  SI.Time waitElapsed;
  Integer controller_state;
equation
  waitElapsed = time - pre(tEnter);
  valve1Cmd = mode == Mode.FILL_T1;
  valve2Cmd = (mode == Mode.TRANSFER_T1_T2) or (mode == Mode.SHUTDOWN and not (tank1Level <= t1Low and tank2Level <= t2Low));
  valve3Cmd = (mode == Mode.DRAIN_T2) or (mode == Mode.SHUTDOWN and not (tank1Level <= t1Low and tank2Level <= t2Low));
  controller_state = if mode == Mode.IDLE then 1 else if mode == Mode.FILL_T1 then 2 else if mode == Mode.WAIT_AFTER_FILL then 3 else if mode == Mode.TRANSFER_T1_T2 then 4 else if mode == Mode.WAIT_AFTER_TRANSFER then 5 else if mode == Mode.DRAIN_T2 then 6 else if mode == Mode.WAIT_AFTER_DRAIN then 7 else if mode == Mode.PAUSED then 8 else 9;
algorithm
  when sample(0, scanPeriod) then
    startSample := startButton;
    stopSample := stopButton;
    shutSample := shutButton;
    startPulse := startButton and not pre(startSample);
    stopPulse := stopButton and not pre(stopSample);
    shutPulse := shutButton and not pre(shutSample);
  end when;

  when {shutPulse, stopPulse, startPulse, pre(mode) == Mode.FILL_T1 and tank1Level >= t1High, pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill, pre(mode) == Mode.TRANSFER_T1_T2 and tank1Level <= t1Low, pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer, pre(mode) == Mode.DRAIN_T2 and tank2Level <= t2Low, pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain, pre(mode) == Mode.SHUTDOWN and tank1Level <= t1Low and tank2Level <= t2Low} then
    if shutPulse and pre(mode) <> Mode.SHUTDOWN then
      mode := Mode.SHUTDOWN;
    elseif pre(mode) == Mode.SHUTDOWN and tank1Level <= t1Low and tank2Level <= t2Low then
      mode := Mode.IDLE;
      resumeMode := Mode.FILL_T1;
      remainingWait := 0;
      tEnter := time;
    elseif stopPulse and pre(mode) <> Mode.IDLE and pre(mode) <> Mode.PAUSED and pre(mode) <> Mode.SHUTDOWN then
      resumeMode := pre(mode);
      if pre(mode) == Mode.WAIT_AFTER_FILL then
        remainingWait := max(0, waitAfterFill - waitElapsed);
      elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER then
        remainingWait := max(0, waitAfterTransfer - waitElapsed);
      elseif pre(mode) == Mode.WAIT_AFTER_DRAIN then
        remainingWait := max(0, waitAfterDrain - waitElapsed);
      else
        remainingWait := 0;
      end if;
      mode := Mode.PAUSED;
    elseif startPulse and pre(mode) == Mode.IDLE then
      mode := Mode.FILL_T1;
      tEnter := time;
    elseif startPulse and pre(mode) == Mode.PAUSED then
      if pre(resumeMode) == Mode.WAIT_AFTER_FILL then
        mode := Mode.WAIT_AFTER_FILL;
        tEnter := time - (waitAfterFill - pre(remainingWait));
      elseif pre(resumeMode) == Mode.WAIT_AFTER_TRANSFER then
        mode := Mode.WAIT_AFTER_TRANSFER;
        tEnter := time - (waitAfterTransfer - pre(remainingWait));
      elseif pre(resumeMode) == Mode.WAIT_AFTER_DRAIN then
        mode := Mode.WAIT_AFTER_DRAIN;
        tEnter := time - (waitAfterDrain - pre(remainingWait));
      else
        mode := pre(resumeMode);
      end if;
    elseif pre(mode) == Mode.FILL_T1 and tank1Level >= t1High then
      mode := Mode.WAIT_AFTER_FILL;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_FILL and waitElapsed >= waitAfterFill then
      mode := Mode.TRANSFER_T1_T2;
    elseif pre(mode) == Mode.TRANSFER_T1_T2 and tank1Level <= t1Low then
      mode := Mode.WAIT_AFTER_TRANSFER;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_TRANSFER and waitElapsed >= waitAfterTransfer then
      mode := Mode.DRAIN_T2;
    elseif pre(mode) == Mode.DRAIN_T2 and tank2Level <= t2Low then
      mode := Mode.WAIT_AFTER_DRAIN;
      tEnter := time;
    elseif pre(mode) == Mode.WAIT_AFTER_DRAIN and waitElapsed >= waitAfterDrain then
      mode := Mode.FILL_T1;
    end if;
  end when;
  annotation(
    Icon(graphics={Rectangle(extent={{-80,-80},{80,80}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-74,28},{74,56}}, textString="PLC-101"), Text(extent={{-96,96},{104,136}}, textString="%name"), Text(extent={{-96,72},{-40,84}}, textString="START"), Text(extent={{-96,32},{-44,44}}, textString="STOP"), Text(extent={{-96,-8},{-46,4}}, textString="SHUT"), Text(extent={{40,52},{94,64}}, textString="V1"), Text(extent={{40,12},{94,24}}, textString="V2"), Text(extent={{40,-28},{94,-16}}, textString="V3")})
  );
end TankController;
