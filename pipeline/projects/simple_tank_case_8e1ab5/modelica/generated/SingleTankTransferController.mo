model SingleTankTransferController
  type Mode = enumeration(Idle, Fill_Tank_1, Wait_1, Transfer_To_Tank_2, Wait_2, Drain_Tank_2, Paused, Shutdown_Emptying);
  Modelica.Blocks.Interfaces.BooleanInput startButton annotation(Placement(transformation(extent={{-120,70},{-100,90}})));
  Modelica.Blocks.Interfaces.BooleanInput stopButton annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.BooleanInput shutButton annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.BooleanInput highLevelTank1 annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelTank1 annotation(Placement(transformation(extent={{-120,-90},{-100,-70}})));
  Modelica.Blocks.Interfaces.BooleanInput lowLevelTank2 annotation(Placement(transformation(extent={{-120,-130},{-100,-110}})));
  Modelica.Blocks.Interfaces.BooleanOutput inletOpen annotation(Placement(transformation(extent={{100,60},{120,80}})));
  Modelica.Blocks.Interfaces.BooleanOutput transferOpen annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput drainOpen annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.IntegerOutput activeState annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
  parameter Modelica.Units.SI.Time waitDuration = 10;
  parameter Modelica.Units.SI.Time scanPeriod = 0.1;
  discrete Mode mode(start=Mode.Idle, fixed=true);
  discrete Mode resumeMode(start=Mode.Idle, fixed=true);
  discrete Real tEnter(start=0, fixed=true);
  discrete Real waitRemaining(start=0, fixed=true);
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
  startPulse = startSample and not pre(startSample);
  stopPulse = stopSample and not pre(stopSample);
  shutPulse = shutSample and not pre(shutSample);
  waitElapsed = time - pre(tEnter);
  inletOpen = mode == Mode.Fill_Tank_1;
  transferOpen = mode == Mode.Transfer_To_Tank_2 or mode == Mode.Shutdown_Emptying;
  drainOpen = mode == Mode.Drain_Tank_2 or mode == Mode.Shutdown_Emptying;
  activeState = if mode == Mode.Idle then 0 else if mode == Mode.Fill_Tank_1 then 1 else if mode == Mode.Wait_1 then 2 else if mode == Mode.Transfer_To_Tank_2 then 3 else if mode == Mode.Wait_2 then 4 else if mode == Mode.Drain_Tank_2 then 5 else if mode == Mode.Paused then 6 else 7;
algorithm
  when {startPulse, stopPulse, shutPulse, pre(mode) == Mode.Fill_Tank_1 and highLevelTank1, pre(mode) == Mode.Wait_1 and waitElapsed >= waitDuration, pre(mode) == Mode.Transfer_To_Tank_2 and lowLevelTank1, pre(mode) == Mode.Wait_2 and waitElapsed >= waitDuration, pre(mode) == Mode.Drain_Tank_2 and lowLevelTank2, pre(mode) == Mode.Shutdown_Emptying and lowLevelTank1 and lowLevelTank2} then
    if shutPulse and pre(mode) <> Mode.Shutdown_Emptying then
      mode := Mode.Shutdown_Emptying;
    elseif stopPulse and pre(mode) <> Mode.Idle and pre(mode) <> Mode.Paused and pre(mode) <> Mode.Shutdown_Emptying then
      resumeMode := pre(mode);
      if pre(mode) == Mode.Wait_1 or pre(mode) == Mode.Wait_2 then
        waitRemaining := max(0, waitDuration - (time - pre(tEnter)));
      end if;
      mode := Mode.Paused;
    elseif startPulse and pre(mode) == Mode.Paused then
      mode := pre(resumeMode);
      if pre(resumeMode) == Mode.Wait_1 or pre(resumeMode) == Mode.Wait_2 then
        tEnter := time - (waitDuration - pre(waitRemaining));
      end if;
    elseif startPulse and pre(mode) == Mode.Idle then
      mode := Mode.Fill_Tank_1;
    elseif pre(mode) == Mode.Fill_Tank_1 and highLevelTank1 then
      mode := Mode.Wait_1;
      tEnter := time;
    elseif pre(mode) == Mode.Wait_1 and waitElapsed >= waitDuration then
      mode := Mode.Transfer_To_Tank_2;
    elseif pre(mode) == Mode.Transfer_To_Tank_2 and lowLevelTank1 then
      mode := Mode.Wait_2;
      tEnter := time;
    elseif pre(mode) == Mode.Wait_2 and waitElapsed >= waitDuration then
      mode := Mode.Drain_Tank_2;
    elseif pre(mode) == Mode.Drain_Tank_2 and lowLevelTank2 then
      mode := Mode.Idle;
    elseif pre(mode) == Mode.Shutdown_Emptying and lowLevelTank1 and lowLevelTank2 then
      mode := Mode.Idle;
    end if;
  end when;
  annotation(
    Icon(graphics={Rectangle(extent={{-80,-80},{80,80}}, lineColor={0,0,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid),Text(extent={{-70,20},{70,60}}, textString="Controller"),Text(extent={{-96,100},{104,140}}, textString="%name")}));
end SingleTankTransferController;
