model Tank003System
  parameter String startCommandBehaviorInInitialCondition = "initiates automatic operation";  // Requirement bound (START command.behavior in initial condition == None ) preserved as a Modelica parameter.
  parameter String v1StateDuringNormalOperation = "open";  // Requirement bound (V1.state during normal operation == None ) preserved as a Modelica parameter.
  parameter String v1StateAtTank1HighLevelLimit = "closed";  // Requirement bound (V1.state at Tank 1 high-level limit == None ) preserved as a Modelica parameter.
  parameter Real waitAfterTank1HighDuration(unit="s") = 10.0;  // Requirement bound (wait after Tank 1 high.duration == None s) preserved as a Modelica parameter.
  parameter String v2StateAfterWaitFollowingTank1High = "open";  // Requirement bound (V2.state after wait following Tank 1 high == None ) preserved as a Modelica parameter.
  parameter String v2StateAtTank1MinimumOperatingLevel = "closed";  // Requirement bound (V2.state at Tank 1 minimum operating level == None ) preserved as a Modelica parameter.
  parameter Real waitAfterTank1LowDuration(unit="s") = 10.0;  // Requirement bound (wait after Tank 1 low.duration == None s) preserved as a Modelica parameter.
  parameter String v3StateAfterWaitFollowingTank1Low = "open";  // Requirement bound (V3.state after wait following Tank 1 low == None ) preserved as a Modelica parameter.
  parameter String v3StateAtTank2MinimumOperatingLevel = "closed";  // Requirement bound (V3.state at Tank 2 minimum operating level == None ) preserved as a Modelica parameter.
  parameter Real waitAfterTank2LowDuration(unit="s") = 10.0;  // Requirement bound (wait after Tank 2 low.duration == None s) preserved as a Modelica parameter.
  parameter String automaticProcessContinuationMode = "cyclic";  // Requirement bound (automatic process.continuation mode == None ) preserved as a Modelica parameter.
  parameter String stopCommandStateOfAllThreeValves = "closed";  // Requirement bound (STOP command.state of all three valves == None ) preserved as a Modelica parameter.
  parameter String stopCommandAutomaticOperation = "suspended";  // Requirement bound (STOP command.automatic operation == None ) preserved as a Modelica parameter.
  parameter String startAfterSTOPProcessOperationMode = "continue existing process";  // Requirement bound (START after STOP.process operation mode == None ) preserved as a Modelica parameter.
  parameter String startAfterSTOPInitializationMode = "not force new empty-cycle initialization";  // Requirement bound (START after STOP.initialization mode == None ) preserved as a Modelica parameter.
  parameter String shutCommandTank1AndTank2State = "empty";  // Requirement bound (SHUT command.Tank 1 and Tank 2 state == None ) preserved as a Modelica parameter.
  parameter String shutCommandV2State = "open";  // Requirement bound (SHUT command.V2 state == None ) preserved as a Modelica parameter.
  parameter String shutCommandV3State = "open";  // Requirement bound (SHUT command.V3 state == None ) preserved as a Modelica parameter.
  parameter String shutCommandV1State = "inhibited";  // Requirement bound (SHUT command.V1 state == None ) preserved as a Modelica parameter.
  parameter String v2AndV3StateAfterShutdownEmptyingIsAchieved = "closed";  // Requirement bound (V2 and V3.state after shutdown emptying is achieved == None ) preserved as a Modelica parameter.
  parameter String controllerStateAfterShutdownEmptyingIsAchieved = "start configuration";  // Requirement bound (controller.state after shutdown emptying is achieved == None ) preserved as a Modelica parameter.
  parameter Real tank1InitialLevelValue(unit="m") = 0.05;  // Requirement bound (Tank 1 initial level.value == None m) preserved as a Modelica parameter.
  parameter Real tank2InitialLevelValue(unit="m") = 0.05;  // Requirement bound (Tank 2 initial level.value == None m) preserved as a Modelica parameter.
  parameter Real tank1HighLimitValue(unit="m") = 0.78;  // Requirement bound (Tank 1 high limit.value == None m) preserved as a Modelica parameter.
  parameter Real tank1LowLimitValue(unit="m") = 0.05;  // Requirement bound (Tank 1 low limit.value == None m) preserved as a Modelica parameter.
  parameter Real tank2LowLimitValue(unit="m") = 0.05;  // Requirement bound (Tank 2 low limit.value == None m) preserved as a Modelica parameter.
  parameter Real waitAfterT1HighValue(unit="s") = 10.0;  // Requirement bound (Wait after T1 high.value == None s) preserved as a Modelica parameter.
  parameter Real waitAfterT1LowValue(unit="s") = 10.0;  // Requirement bound (Wait after T1 low.value == None s) preserved as a Modelica parameter.
  parameter Real waitAfterT2LowValue(unit="s") = 10.0;  // Requirement bound (Wait after T2 low.value == None s) preserved as a Modelica parameter.
  parameter String actuatorsPowerLossFailSafeState = "closed";  // Requirement bound (actuators.power-loss fail-safe state == None ) preserved as a Modelica parameter.
  parameter String controllerAutomaticFillTransferDrainSequenceStartCondition = "valid START command when the process is idle or paused";  // Requirement bound (controller.automatic fill-transfer-drain sequence start condition == None ) preserved as a Modelica parameter.
  parameter String automaticSequenceInletValve = "V1";  // Requirement bound (automatic sequence.inlet valve == None ) preserved as a Modelica parameter.
  parameter Real controllerWaitTimeAfterTank1ReachesHighLevelLimitBeforeOpeningV2(unit="s") = 10.0;  // Requirement bound (controller.wait time after Tank 1 reaches high-level limit before opening V2 == None s) preserved as a Modelica parameter.
  parameter String v2TransferLiquidUntilTank1LowLevelLimitIsReached = "Tank 1 reaches its low-level limit";  // Requirement bound (V2.transfer liquid until Tank 1 low-level limit is reached == None ) preserved as a Modelica parameter.
  parameter Real controllerWaitTimeAfterTank1ReachesLowLevelLimitBeforeOpeningV3(unit="s") = 10.0;  // Requirement bound (controller.wait time after Tank 1 reaches low-level limit before opening V3 == None s) preserved as a Modelica parameter.
  parameter String v3DrainTank2Until = "Tank 2 reaches its low-level limit";  // Requirement bound (V3.drain Tank 2 until == None ) preserved as a Modelica parameter.
  parameter Real controllerReturnToTank1FillingOperationWaitTimeAfterTank2ReachesLowLevelLimit(unit="s") = 10.0;  // Requirement bound (controller.return to Tank 1 filling operation wait time after Tank 2 reaches low-level limit == None s) preserved as a Modelica parameter.
  parameter String controllerSTOPCommandEffect = "close V1, V2 and V3 and place the controller in a paused condition";  // Requirement bound (controller.STOP command effect == None ) preserved as a Modelica parameter.
  parameter String controllerSTARTAfterSTOPBehavior = "continue the sequence from the point at which STOP was accepted";  // Requirement bound (controller.START after STOP behavior == None ) preserved as a Modelica parameter.
  parameter String controllerSHUTCommandEffect = "command V2 and V3 open to drain both tanks and inhibit V1";  // Requirement bound (controller.SHUT command effect == None ) preserved as a Modelica parameter.
  parameter String controllerPostShutdownState = "all three valves closed and initial idle configuration";  // Requirement bound (controller.post-shutdown state == None ) preserved as a Modelica parameter.
  parameter String processValvesPositionOnControllerPowerLoss = "closed";  // Requirement bound (process valves.position on controller power loss == None ) preserved as a Modelica parameter.
  parameter String commandPriorityOrdering = "SHUT > STOP > START";  // Requirement bound (command priority.ordering == None ) preserved as a Modelica parameter.
  parameter String v1CommandedOpenWhileV2IsOpen = "never";  // Requirement bound (V1.commanded open while V2 is open == None ) preserved as a Modelica parameter.
  parameter String v2AndV3SimultaneousOpenStateDuringNormalAutomaticOperation = "not allowed";  // Requirement bound (V2 and V3.simultaneous open state during normal automatic operation == None ) preserved as a Modelica parameter.
  parameter String v2AndV3SimultaneousOpenState = "allowed";  // Requirement bound (V2 and V3.simultaneous open state == None ) preserved as a Modelica parameter.
  parameter Real tank1HighLevelSetpointValue(unit="m") = 0.8;  // Requirement bound (Tank 1 high-level setpoint.value == None m) preserved as a Modelica parameter.
  parameter Real tank1LowLevelSetpointValue(unit="m") = 0.05;  // Requirement bound (Tank 1 low-level setpoint.value == None m) preserved as a Modelica parameter.
  parameter Real tank2LowLevelSetpointValue(unit="m") = 0.05;  // Requirement bound (Tank 2 low-level setpoint.value == None m) preserved as a Modelica parameter.
  parameter Real postTransferWaitingTimeValue(unit="s") = 12.0;  // Requirement bound (post-transfer waiting time.value == None s) preserved as a Modelica parameter.
  parameter Real interCycleWaitingTimeAfterTank2ReachesLowLevelValue(unit="s") = 8.0;  // Requirement bound (inter-cycle waiting time after Tank 2 reaches low level.value == None s) preserved as a Modelica parameter.
  parameter Real controllerNumberOfAnalogLevelMeasurementsReceived= 2.0;  // Requirement bound (controller.number of analog level measurements received == None ) preserved as a Modelica parameter.
  parameter Real controllerNumberOfMomentaryDigitalCommandsReceived= 3.0;  // Requirement bound (controller.number of momentary digital commands received == None ) preserved as a Modelica parameter.
  parameter Real controllerNumberOfDiscreteValveOpenCommandsProvided= 3.0;  // Requirement bound (controller.number of discrete valve-open commands provided == None ) preserved as a Modelica parameter.
  parameter String waitTimerBehaviorOnSTOPDuringWaitState = "freeze rather than restart";  // Requirement bound (wait timer.behavior on STOP during wait state == None ) preserved as a Modelica parameter.
  parameter String startCommandsBehaviorWhileAlreadyRunning = "ignored";  // Requirement bound (START commands.behavior while already running == None ) preserved as a Modelica parameter.
  parameter String stopCommandsBehaviorDuringSHUTMode = "ignored until shutdown is complete";  // Requirement bound (STOP commands.behavior during SHUT mode == None ) preserved as a Modelica parameter.
  parameter String startCommandsBehaviorDuringSHUTMode = "ignored until shutdown is complete";  // Requirement bound (START commands.behavior during SHUT mode == None ) preserved as a Modelica parameter.
  parameter String shutdownCompletionTankLevelCondition = "Tank 1 and Tank 2 both at or below their low-level setpoints";  // Requirement bound (shutdown completion.tank level condition == None ) preserved as a Modelica parameter.
  parameter Real demonstrationRunSimulationDuration(unit="s") = 900.0;  // Requirement bound (demonstration run.simulation duration RANGE 900.0 s) preserved as a Modelica parameter.
  parameter Real demonstrationRunEventScheduleSTARTTime(unit="s") = 20.0;  // Requirement bound (demonstration run.event schedule START time == None s) preserved as a Modelica parameter.
  parameter Real demonstrationRunEventScheduleSTOPTime(unit="s") = 220.0;  // Requirement bound (demonstration run.event schedule STOP time == None s) preserved as a Modelica parameter.
  parameter Real demonstrationRunEventScheduleSTARTTime_2(unit="s") = 280.0;  // Requirement bound (demonstration run.event schedule START time == None s) preserved as a Modelica parameter.
  parameter Real demonstrationRunEventScheduleSTOPTime_2(unit="s") = 650.0;  // Requirement bound (demonstration run.event schedule STOP time == None s) preserved as a Modelica parameter.
  parameter Real demonstrationRunEventScheduleSHUTTime(unit="s") = 700.0;  // Requirement bound (demonstration run.event schedule SHUT time == None s) preserved as a Modelica parameter.
  parameter String levelValuesInternalRepresentationUnits = "metres";  // Requirement bound (level values.internal representation units == None ) preserved as a Modelica parameter.
  parameter Real levelValuesNominalValidRange(unit="m") = 1.0;  // Requirement bound (level values.nominal valid range RANGE 1.0 m) preserved as a Modelica parameter.
  parameter String valveCommandsRepresentation = "Boolean open/closed commands";  // Requirement bound (valve commands.representation == None ) preserved as a Modelica parameter.
  parameter Real tk101CrossSectionArea(unit="m2") = 1.2;  // Requirement bound (TK-101.cross-section area == None m^2) preserved as a Modelica parameter.
  parameter Real tk101Height(unit="m") = 1.0;  // Requirement bound (TK-101.height == None m) preserved as a Modelica parameter.
  parameter Real tk101MaxWorkingLevel(unit="m") = 0.9;  // Requirement bound (TK-101.max working level == None m) preserved as a Modelica parameter.
  parameter Real tk102CrossSectionArea(unit="m2") = 1.4;  // Requirement bound (TK-102.cross-section area == None m^2) preserved as a Modelica parameter.
  parameter Real tk102Height(unit="m") = 1.0;  // Requirement bound (TK-102.height == None m) preserved as a Modelica parameter.
  parameter Real tk102MaxWorkingLevel(unit="m") = 0.9;  // Requirement bound (TK-102.max working level == None m) preserved as a Modelica parameter.
  parameter Real xv101NominalFlow(unit="m3/s") = 0.006;  // Requirement bound (XV-101.nominal flow == None m^3/s) preserved as a Modelica parameter.
  parameter String xv101FailPosition = "Closed";  // Requirement bound (XV-101.fail position == None ) preserved as a Modelica parameter.
  parameter Real xv101FullOpenTime(unit="s") = 0.8;  // Requirement bound (XV-101.full-open time == None s) preserved as a Modelica parameter.
  parameter Real xv102NominalFlow(unit="m3/s") = 0.0045;  // Requirement bound (XV-102.nominal flow == None m^3/s) preserved as a Modelica parameter.
  parameter String xv102FailPosition = "Closed";  // Requirement bound (XV-102.fail position == None ) preserved as a Modelica parameter.
  parameter Real xv103NominalFlow(unit="m3/s") = 0.005;  // Requirement bound (XV-103.nominal flow == None m^3/s) preserved as a Modelica parameter.
  parameter String xv103FailPosition = "Closed";  // Requirement bound (XV-103.fail position == None ) preserved as a Modelica parameter.
  parameter String lt101SignalMapping = "4-20 mA mapped 0.0-1.0 m";  // Requirement bound (LT-101.signal mapping == None ) preserved as a Modelica parameter.
  parameter String lt102SignalMapping = "4-20 mA mapped 0.0-1.0 m";  // Requirement bound (LT-102.signal mapping == None ) preserved as a Modelica parameter.
  parameter Real plc101ScanTime(unit="ms") = 100.0;  // Requirement bound (PLC-101.scan time == None ms) preserved as a Modelica parameter.
  parameter Real di101EngineeringRange= 1.0;  // Requirement bound (DI-101.engineering range RANGE 1.0 ) preserved as a Modelica parameter.
  parameter Real di102EngineeringRange= 1.0;  // Requirement bound (DI-102.engineering range RANGE 1.0 ) preserved as a Modelica parameter.
  parameter Real di103EngineeringRange= 1.0;  // Requirement bound (DI-103.engineering range RANGE 1.0 ) preserved as a Modelica parameter.
  parameter Real ai101EngineeringRange(unit="m") = 1.0;  // Requirement bound (AI-101.engineering range RANGE 1.0 m) preserved as a Modelica parameter.
  parameter Real ai101NormalState(unit="m") = 0.05;  // Requirement bound (AI-101.normal state == None m) preserved as a Modelica parameter.
  parameter Real ai101UpdatePeriod(unit="ms") = 100.0;  // Requirement bound (AI-101.update period == None ms) preserved as a Modelica parameter.
  parameter Real ai102EngineeringRange(unit="m") = 1.0;  // Requirement bound (AI-102.engineering range RANGE 1.0 m) preserved as a Modelica parameter.
  parameter Real ai102NormalState(unit="m") = 0.05;  // Requirement bound (AI-102.normal state == None m) preserved as a Modelica parameter.
  parameter Real ai102UpdatePeriod(unit="ms") = 100.0;  // Requirement bound (AI-102.update period == None ms) preserved as a Modelica parameter.
  parameter Real do101EngineeringRange= 1.0;  // Requirement bound (DO-101.engineering range RANGE 1.0 ) preserved as a Modelica parameter.
  parameter Real do101NormalState= 0.0;  // Requirement bound (DO-101.normal state == None ) preserved as a Modelica parameter.
  parameter Real do101UpdatePeriod(unit="ms") = 100.0;  // Requirement bound (DO-101.update period == None ms) preserved as a Modelica parameter.
  parameter Real do102EngineeringRange= 1.0;  // Requirement bound (DO-102.engineering range RANGE 1.0 ) preserved as a Modelica parameter.
  parameter Real do102NormalState= 0.0;  // Requirement bound (DO-102.normal state == None ) preserved as a Modelica parameter.
  parameter Real do102UpdatePeriod(unit="ms") = 100.0;  // Requirement bound (DO-102.update period == None ms) preserved as a Modelica parameter.
  parameter Real do103EngineeringRange= 1.0;  // Requirement bound (DO-103.engineering range RANGE 1.0 ) preserved as a Modelica parameter.
  parameter Real do103NormalState= 0.0;  // Requirement bound (DO-103.normal state == None ) preserved as a Modelica parameter.
  parameter Real do103UpdatePeriod(unit="ms") = 100.0;  // Requirement bound (DO-103.update period == None ms) preserved as a Modelica parameter.
  parameter Real simulationStopTimeValue(unit="s") = 900.0;  // Requirement bound (simulation stop time.value == None s) preserved as a Modelica parameter.
  parameter Real controllerInitialLevelForTK101(unit="m") = 0.05;  // Requirement bound (controller.initial level for TK-101 == None m) preserved as a Modelica parameter.
  parameter Real controllerInitialLevelForTK102(unit="m") = 0.05;  // Requirement bound (controller.initial level for TK-102 == None m) preserved as a Modelica parameter.
  parameter Real tank1HighLevelLimitValue(unit="m") = 0.8;  // Requirement bound (Tank 1 high-level limit.value == None m) preserved as a Modelica parameter.
  parameter Real tank1LowLevelLimitValue(unit="m") = 0.05;  // Requirement bound (Tank 1 low-level limit.value == None m) preserved as a Modelica parameter.
  parameter Real tank2LowLevelLimitValue(unit="m") = 0.05;  // Requirement bound (Tank 2 low-level limit.value == None m) preserved as a Modelica parameter.
  parameter Real controllerWaitAfterTank1High(unit="s") = 10.0;  // Requirement bound (controller.wait after Tank 1 high == None s) preserved as a Modelica parameter.
  parameter Real controllerWaitAfterTank1Low(unit="s") = 12.0;  // Requirement bound (controller.wait after Tank 1 low == None s) preserved as a Modelica parameter.
  parameter Real controllerWaitAfterTank2Low(unit="s") = 8.0;  // Requirement bound (controller.wait after Tank 2 low == None s) preserved as a Modelica parameter.
  parameter Real controllerNominalInletFlow(unit="m3/s") = 0.006;  // Requirement bound (controller.nominal inlet flow == None m^3/s) preserved as a Modelica parameter.
  parameter Real controllerNominalTransferFlow(unit="m3/s") = 0.0045;  // Requirement bound (controller.nominal transfer flow == None m^3/s) preserved as a Modelica parameter.
  parameter Real controllerNominalDrainFlow(unit="m3/s") = 0.005;  // Requirement bound (controller.nominal drain flow == None m^3/s) preserved as a Modelica parameter.
  parameter Real plc101ControllerScanTime(unit="s") = 0.1;  // Requirement bound (PLC-101.controller scan time == None s) preserved as a Modelica parameter.
  parameter Real tank1LevelDefaultValue(unit="g") = 0.05;  // Requirement bound (tank1.level.default value == None g) preserved as a Modelica parameter.
  parameter Real tank2LevelDefaultValue(unit="g") = 0.05;  // Requirement bound (tank2.level.default value == None g) preserved as a Modelica parameter.
  parameter String controllerCommandPriorityOfSHUT = "highest";  // Requirement bound (controller.command priority of SHUT == None ) preserved as a Modelica parameter.
  parameter String controllerCommandPriorityOfSTOP = "next after SHUT";  // Requirement bound (controller.command priority of STOP == None ) preserved as a Modelica parameter.
  parameter String controllerCommandPriorityOfSTART = "lowest";  // Requirement bound (controller.command priority of START == None ) preserved as a Modelica parameter.
  parameter String controllerStateOnValidSHUTEdge = "SHUTDOWN";  // Requirement bound (controller.state on valid SHUT edge == None ) preserved as a Modelica parameter.
  parameter String controllerStateOnSTOPCommand = "PAUSED";  // Requirement bound (controller.state on STOP command == None ) preserved as a Modelica parameter.
  parameter String controllerValveOutputsDuringPAUSEDAfterSTOP = "false";  // Requirement bound (controller.valve outputs during PAUSED after STOP == None ) preserved as a Modelica parameter.
  parameter String controllerStateOnSTARTFromIDLE = "FILL_T1";  // Requirement bound (controller.state on START from IDLE == None ) preserved as a Modelica parameter.
  parameter String controllerStateOnSTARTFromPAUSED = "stored interrupted state";  // Requirement bound (controller.state on START from PAUSED == None ) preserved as a Modelica parameter.
  parameter String controllerSTARTWhileAlreadyRunningBehavior = "ignored";  // Requirement bound (controller.START while already running behavior == None ) preserved as a Modelica parameter.
  parameter String controllerCommandsDuringSHUTDOWNBehavior = "do not interrupt shutdown sequence";  // Requirement bound (controller.commands during SHUTDOWN behavior == None ) preserved as a Modelica parameter.
  parameter String controllerCommandRequiredAfterShutdownCompletes = "START";  // Requirement bound (controller.command required after shutdown completes == None ) preserved as a Modelica parameter.
  parameter String controllerRemainingDelayAfterSTOPInWaitStates = "retained";  // Requirement bound (controller.remaining delay after STOP in wait states == None ) preserved as a Modelica parameter.
  parameter String controllerResumeTimerBehaviorAfterSTART = "resume with remaining delay";  // Requirement bound (controller.resume timer behavior after START == None ) preserved as a Modelica parameter.
  parameter String v1AndV2SimultaneousOpenState = "not allowed";  // Requirement bound (V1 and V2.simultaneous open state == None ) preserved as a Modelica parameter.
  parameter String v2AndV3SimultaneousOpenState_2 = "not allowed";  // Requirement bound (V2 and V3.simultaneous open state == None ) preserved as a Modelica parameter.
  parameter String v2AndV3SimultaneousOpenRestriction = "waived";  // Requirement bound (V2 and V3.simultaneous open restriction == None ) preserved as a Modelica parameter.
  parameter String valvesActuationMode = "de-energize-to-close";  // Requirement bound (valves.actuation mode == None ) preserved as a Modelica parameter.
  parameter String controllerOutputCommandsStateOnControllerPowerLoss = "false";  // Requirement bound (controller output commands.state on controller power loss == None ) preserved as a Modelica parameter.
  parameter String levelThresholdComparisonsComparisonIncludesEquality = "true";  // Requirement bound (level threshold comparisons.comparison includes equality == None ) preserved as a Modelica parameter.
  parameter String fillT1TransitionGuardLT101ThresholdRelation = "T1_High";  // Requirement bound (FILL_T1 transition guard.LT-101 threshold relation >= None ) preserved as a Modelica parameter.
  parameter String transferT1T2TransitionGuardLT101ThresholdRelation = "T1_Low";  // Requirement bound (TRANSFER_T1_T2 transition guard.LT-101 threshold relation <= None ) preserved as a Modelica parameter.
  parameter String drainT2TransitionGuardLT102ThresholdRelation = "T2_Low";  // Requirement bound (DRAIN_T2 transition guard.LT-102 threshold relation <= None ) preserved as a Modelica parameter.
  parameter String waitAFTERDRAINAutomaticNextStateAfterTimerExpiry = "FILL_T1";  // Requirement bound (WAIT_AFTER_DRAIN.automatic next state after timer expiry == None ) preserved as a Modelica parameter.
  parameter String shutdownExitCondition = "IDLE";  // Requirement bound (SHUTDOWN.exit condition == None ) preserved as a Modelica parameter.
  parameter String commandPrecedencePriorityOrder = "SHUT > STOP > START";  // Requirement bound (command precedence.priority order == None ) preserved as a Modelica parameter.
  parameter String stopCommandValveCommandState = "all valves closed";  // Requirement bound (STOP command.valve command state == None ) preserved as a Modelica parameter.
  parameter String stopCommandInterruptedState = "stored";  // Requirement bound (STOP command.interrupted state == None ) preserved as a Modelica parameter.
  parameter String stopDuringAnyDelayRemainingDelay = "frozen";  // Requirement bound (STOP during any delay.remaining delay == None ) preserved as a Modelica parameter.
  parameter String startCommandRemainingDelay = "resumed";  // Requirement bound (START command.remaining delay == None ) preserved as a Modelica parameter.
  parameter String automaticSequenceBehaviorOnSTART = "ignored";  // Requirement bound (automatic sequence.behavior on START == None ) preserved as a Modelica parameter.
  parameter String startCommandBehaviorDuringActiveSHUT = "ignored";  // Requirement bound (START command.behavior during active SHUT == None ) preserved as a Modelica parameter.
  parameter String stopCommandBehaviorDuringActiveSHUT = "ignored";  // Requirement bound (STOP command.behavior during active SHUT == None ) preserved as a Modelica parameter.
  parameter String shutCompletionCriterion = "LT-101 and LT-102 at or below their low-level setpoints";  // Requirement bound (SHUT.completion criterion == None ) preserved as a Modelica parameter.
  parameter String afterShutdownCompletionValveCommandState = "all valves closed";  // Requirement bound (after shutdown completion.valve command state == None ) preserved as a Modelica parameter.
  parameter String sequenceContextState = "IDLE";  // Requirement bound (sequence context.state == None ) preserved as a Modelica parameter.
  parameter String v1AndV2CommandedOpenTogether = "never";  // Requirement bound (V1 and V2.commanded open together == None ) preserved as a Modelica parameter.
  parameter String v2AndV3CommandedOpenTogetherInNormalAutoOperation = "not allowed";  // Requirement bound (V2 and V3.commanded open together in normal auto operation == None ) preserved as a Modelica parameter.
  parameter Real t1HighSetpoint(unit="m") = 0.8;  // Requirement bound (T1 high.setpoint == None m) preserved as a Modelica parameter.
  parameter Real postTransferDelayDuration(unit="s") = 12.0;  // Requirement bound (post-transfer delay.duration == None s) preserved as a Modelica parameter.
  parameter Real interCycleDelayAfterTank2LowDuration(unit="s") = 8.0;  // Requirement bound (inter-cycle delay after Tank 2 low.duration == None s) preserved as a Modelica parameter.
  parameter Real t1FillTargetTargetLevel(unit="m") = 0.8;  // Requirement bound (T1 fill target.target level == None m) preserved as a Modelica parameter.
  parameter Real controlsWaitAfterT1LowDeadTime(unit="s") = 12.0;  // Requirement bound (controls wait after T1 low.dead time == None s) preserved as a Modelica parameter.
  parameter Real newFillAfterT2LowDelay(unit="s") = 8.0;  // Requirement bound (new fill after T2 low.delay == None s) preserved as a Modelica parameter.
  parameter Real systemIdleDurationAfterShutdownFinishes(unit="s") = 900.0;  // Requirement bound (system.idle duration after shutdown finishes == None s) preserved as a Modelica parameter.
  parameter Real t1HighLimitEffectiveValue(unit="m") = 0.8;  // Requirement bound (T1 high limit.effective value == None m) preserved as a Modelica parameter.
  parameter Real timeAfterT1ReachesLowLevelBeforeOpeningTheDrainValveDelay(unit="s") = 12.0;  // Requirement bound (time after T1 reaches low level before opening the drain valve.delay == None s) preserved as a Modelica parameter.
  parameter Real timeAfterT2ReachesLowBeforeTheNextFillStartsDelay(unit="s") = 8.0;  // Requirement bound (time after T2 reaches low before the next fill starts.delay == None s) preserved as a Modelica parameter.
  parameter String shutStatePriorityRelativeToSTOPPriorityRelationship = "higher than";  // Requirement bound (SHUT state priority relative to STOP.priority relationship == None ) preserved as a Modelica parameter.
  parameter String v2AndV3CommandedStateDuringSHUTCommandedState = "open";  // Requirement bound (V2 and V3 commanded state during SHUT.commanded state == None ) preserved as a Modelica parameter.
  parameter String startCommandHandlingDuringSHUTEffect = "ignored";  // Requirement bound (START command handling during SHUT.effect == None ) preserved as a Modelica parameter.
  parameter Real modelTankDemoRev12StoppedStateOnStartCmdEdge= 0.0;  // Requirement bound (model TankDemo_Rev12.stopped state on startCmd edge == None ) preserved as a Modelica parameter. (user-approved)
  parameter Real modelTankDemoRev12StoppedStateOnStopCmdEdge= 0.0;  // Requirement bound (model TankDemo_Rev12.stopped state on stopCmd edge == None ) preserved as a Modelica parameter. (user-approved)
  parameter String valve1CommandState = "(seq == StepState.FILL) and not stopped";  // Requirement bound (valve1.command state == None ) preserved as a Modelica parameter.
  parameter String valve2CommandState = "(seq == StepState.TRANSFER) and not stopped";  // Requirement bound (valve2.command state == None ) preserved as a Modelica parameter.
  parameter String valve3CommandState = "(seq == StepState.DRAIN) and not stopped";  // Requirement bound (valve3.command state == None ) preserved as a Modelica parameter.
  parameter String vxs24ValveForProjectTagXV101DeEnergizedPosition = "Closed";  // Requirement bound (VXS-24 valve for project tag XV-101.de-energized position == None ) preserved as a Modelica parameter.
  parameter String vxs24ValveForProjectTagXV102DeEnergizedPosition = "Closed";  // Requirement bound (VXS-24 valve for project tag XV-102.de-energized position == None ) preserved as a Modelica parameter.
  parameter String vxs24ValveForProjectTagXV103DeEnergizedPosition = "Closed";  // Requirement bound (VXS-24 valve for project tag XV-103.de-energized position == None ) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV101NominalDemoFlowCoefficientEquivalent(unit="m3/s") = 0.006;  // Requirement bound (VXS-24 valve for project tag XV-101.nominal demo flow coefficient equivalent == None m^3/s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV102NominalDemoFlowCoefficientEquivalent(unit="m3/s") = 0.0045;  // Requirement bound (VXS-24 valve for project tag XV-102.nominal demo flow coefficient equivalent == None m^3/s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV103NominalDemoFlowCoefficientEquivalent(unit="m3/s") = 0.005;  // Requirement bound (VXS-24 valve for project tag XV-103.nominal demo flow coefficient equivalent == None m^3/s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV101FullOpenStrokeTime(unit="s") = 0.8;  // Requirement bound (VXS-24 valve for project tag XV-101.full open stroke time == None s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV102FullOpenStrokeTime(unit="s") = 0.8;  // Requirement bound (VXS-24 valve for project tag XV-102.full open stroke time == None s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV103FullOpenStrokeTime(unit="s") = 0.8;  // Requirement bound (VXS-24 valve for project tag XV-103.full open stroke time == None s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV101FullCloseStrokeTime(unit="s") = 0.6;  // Requirement bound (VXS-24 valve for project tag XV-101.full close stroke time == None s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV102FullCloseStrokeTime(unit="s") = 0.6;  // Requirement bound (VXS-24 valve for project tag XV-102.full close stroke time == None s) preserved as a Modelica parameter.
  parameter Real vxs24ValveForProjectTagXV103FullCloseStrokeTime(unit="s") = 0.6;  // Requirement bound (VXS-24 valve for project tag XV-103.full close stroke time == None s) preserved as a Modelica parameter.
  parameter String vxs24ValveActuatorForProjectTagXV101Command = "24 VDC energized=open";  // Requirement bound (VXS-24 valve actuator for project tag XV-101.command == None ) preserved as a Modelica parameter.
  parameter String vxs24ValveActuatorForProjectTagXV102Command = "24 VDC energized=open";  // Requirement bound (VXS-24 valve actuator for project tag XV-102.command == None ) preserved as a Modelica parameter.
  parameter String vxs24ValveActuatorForProjectTagXV103Command = "24 VDC energized=open";  // Requirement bound (VXS-24 valve actuator for project tag XV-103.command == None ) preserved as a Modelica parameter.
  parameter Real t1InitialLevel(unit="m") = 0.05;  // Requirement bound (T1.initial level == None m) preserved as a Modelica parameter.
  parameter Real t2InitialLevel(unit="m") = 0.05;  // Requirement bound (T2.initial level == None m) preserved as a Modelica parameter.
  parameter Real simulationDuration(unit="s") = 900.0;  // Requirement bound (simulation.duration == None s) preserved as a Modelica parameter.
  parameter Real loggingInterval(unit="s") = 1.0;  // Requirement bound (logging.interval == None s) preserved as a Modelica parameter.
  parameter Real t1EffectiveHighLevelSetpoint(unit="m") = 0.8;  // Requirement bound (T1.effective high-level setpoint == None m) preserved as a Modelica parameter.
  parameter String allValvesCommandState = "closed";  // Requirement bound (all valves.command state == None ) preserved as a Modelica parameter.
  parameter String controllerOperationAfterSTARTAt280S = "resume interrupted transfer";  // Requirement bound (controller.operation after START at 280 s == None ) preserved as a Modelica parameter.
  parameter Real controllerInterCycleDelay(unit="s") = 8.0;  // Requirement bound (controller.inter-cycle delay == None s) preserved as a Modelica parameter.
  parameter String allValvesCommandState_2 = "closed";  // Requirement bound (all valves.command state == None ) preserved as a Modelica parameter.
  parameter String v1CommandState = "closed";  // Requirement bound (V1.command state == None ) preserved as a Modelica parameter.
  parameter String v2AndV3CommandState = "open";  // Requirement bound (V2 and V3.command state == None ) preserved as a Modelica parameter.
  parameter String controllerState = "IDLE";  // Requirement bound (controller.state == None ) preserved as a Modelica parameter.
  parameter String allValvesCommandState_3 = "closed";  // Requirement bound (all valves.command state == None ) preserved as a Modelica parameter.
  parameter String controllerCommandCompatibility = "V1 and V2 never simultaneously; V2 and V3 never simultaneously in normal automatic operation";  // Requirement bound (controller.command compatibility == None ) preserved as a Modelica parameter.
  parameter Real stateBoundaryComparisonToleranceTolerance(unit="s") = 2.0;  // Requirement bound (state-boundary comparison tolerance.tolerance == None s) preserved as a Modelica parameter.
  inner Modelica.Fluid.System system;
  Modelica.Fluid.Vessels.OpenTank openTank(redeclare package Medium = Modelica.Media.Water.StandardWater, height = 1.0, crossArea = 1.2, use_portsData = false, nPorts = 3);  // Tank TK-101 is a liquid storage vessel with free surface, directly matching the provided library candidate. Evidence supports tank geometry and operating level constraints. (placeholder values, proposed pending confirmation: crossArea, height, use_portsData)
  Modelica.Fluid.Vessels.OpenTank openTank_2(redeclare package Medium = Modelica.Media.Water.StandardWater, height = 1.0, crossArea = 1.4, use_portsData = false, nPorts = 3);  // Tank TK-102 is the same storage role as TK-101, matching the open-tank candidate with free liquid surface behavior. Evidence includes tank-specific level/geometry constraints. (placeholder values, proposed pending confirmation: crossArea, height, use_portsData)
  Modelica.Fluid.Valves.ValveIncompressible valveIncompressible(redeclare package Medium = Modelica.Media.Water.StandardWater, dp_nominal = 100000, m_flow_nominal = 0.006, opening = 1.0);  // XV-101 is an actuated isolation valve; the incompressible valve library component fits a flow-restricting fluid valve. Nominal flow and actuator-related evidence are provided. (placeholder values, proposed pending confirmation: dp_nominal, m_flow_nominal, opening)
  Modelica.Fluid.Valves.ValveIncompressible valveIncompressible_2(redeclare package Medium = Modelica.Media.Water.StandardWater, dp_nominal = 100000, m_flow_nominal = 0.0045, opening = 1.0);  // XV-102 is an actuated isolation valve in the tank transfer path, matching the incompressible valve component. Evidence supports nominal flow and actuation behavior. (placeholder values, proposed pending confirmation: dp_nominal, m_flow_nominal, opening)
  Modelica.Fluid.Valves.ValveIncompressible valveIncompressible_3(redeclare package Medium = Modelica.Media.Water.StandardWater, dp_nominal = 100000, m_flow_nominal = 0.005, opening = 1.0);  // XV-103 is an actuated isolation valve for draining Tank 2, so the incompressible valve library component is appropriate. Evidence supports valve function and actuator response. (placeholder values, proposed pending confirmation: dp_nominal, m_flow_nominal, opening)
  tankController tankController_instance;
  LT101 lt101;
  LT102 lt102;
  Tank_Filling_Emptying_System tank_Filling_Emptying_System;
equation
  // connect: plC_101 -> lT_101  (requires)
  // connect: plC_101 -> lT_102  (requires)
  // connect: xV_101 -> tK_101  (serves)
  // connect: xV_102 -> tK_101  (serves)
  // connect: xV_102 -> tK_102  (serves)
  // connect: xV_103 -> tK_102  (serves)
  // connect: plC_101 -> xV_101  (controls)
  // connect: plC_101 -> xV_102  (controls)
  // connect: plC_101 -> xV_103  (controls)
  // connect: lT_101 -> tK_101  (serves)
  // connect: lT_102 -> tK_102  (serves)
  // connect: tank_Filling_Emptying_System -> plC_101  (contains)
  // connect: tank_Filling_Emptying_System -> tK_101  (contains)
  // connect: tank_Filling_Emptying_System -> tK_102  (contains)
  // connect: tank_Filling_Emptying_System -> xV_101  (contains)
  // connect: tank_Filling_Emptying_System -> xV_102  (contains)
  // connect: tank_Filling_Emptying_System -> xV_103  (contains)
  // connect: tank_Filling_Emptying_System -> lT_101  (contains)
  // connect: tank_Filling_Emptying_System -> lT_102  (contains)
  // connect: tank_Filling_Emptying_System -> pB_START  (contains)
  // connect: tank_Filling_Emptying_System -> pB_STOP  (contains)
  // connect: tank_Filling_Emptying_System -> pB_SHUT  (contains)
  // connect: tank_Filling_Emptying_System -> srC_101  (contains)
  // connect: tank_Filling_Emptying_System -> drN_101  (contains)
  // connect: tK_101 -> lT_101  (connected_to)
  // connect: tK_102 -> lT_102  (connected_to)
  // connect: srC_101 -> xV_101  (connected_to)
  // connect: xV_101 -> tK_101  (connected_to)
  // connect: tK_101 -> xV_102  (connected_to)
  // connect: xV_102 -> tK_102  (connected_to)
  // connect: tK_102 -> xV_103  (connected_to)
  // connect: xV_103 -> drN_101  (connected_to)
  // connect: lT_101 -> plC_101  (connected_to)
  // connect: lT_102 -> plC_101  (connected_to)
  // connect: pB_START -> plC_101  (connected_to)
  // connect: pB_STOP -> plC_101  (connected_to)
  // connect: pB_SHUT -> plC_101  (connected_to)
  // connect: plC_101 -> xV_101  (connected_to)
  // connect: plC_101 -> xV_102  (connected_to)
  // connect: plC_101 -> xV_103  (connected_to)
  // connect: xV_101 -> tK_101  (supplies)
  // connect: xV_102 -> tK_102  (supplies)
  // connect: xV_103 -> drN_101  (supplies)
  // connect: srC_101 -> xV_101  (supplies)
  // connect: plC_101 -> xV_101  (controls)
  // connect: plC_101 -> xV_102  (controls)
  // connect: plC_101 -> xV_103  (controls)
  // connect: pB_START -> plC_101  (signal_flow)
  // connect: pB_STOP -> plC_101  (signal_flow)
  // connect: pB_SHUT -> plC_101  (signal_flow)
  // connect: lT_101 -> plC_101  (signal_flow)
  // connect: lT_102 -> plC_101  (signal_flow)
  // connect: plC_101 -> xV_101  (signal_flow)
  // connect: plC_101 -> xV_102  (signal_flow)
  // connect: plC_101 -> xV_103  (signal_flow)
  // connect: xV_101 -> tK_101  (depends_on)
  // connect: xV_102 -> tK_102  (depends_on)
  // connect: xV_103 -> drN_101  (depends_on)
  // connect: pB_START -> plC_101  (triggers)
  // connect: pB_STOP -> plC_101  (triggers)
  // connect: pB_SHUT -> plC_101  (triggers)
  // connect: lT_101 -> plC_101  (responds_to)
  // connect: lT_102 -> plC_101  (responds_to)
  // connect: plC_101 -> xV_101  (controls)
  // connect: plC_101 -> xV_102  (controls)
  // connect: plC_101 -> xV_103  (controls)
  // connect: source -> valve1  (connected_to)
  // connect: valve1 -> tank1  (connected_to)
  // connect: tank1 -> valve2  (connected_to)
  // connect: valve2 -> tank2  (connected_to)
  // connect: tank2 -> valve3  (connected_to)
  // connect: ambient1 -> valve3  (connected_to)
  // connect: tankController -> valve1  (connected_to)
  // connect: tankController -> valve2  (connected_to)
  // connect: tankController -> valve3  (connected_to)
  // connect: src -> v1  (connected_to)
  // connect: v1 -> t1  (connected_to)
  // connect: t1 -> v2  (connected_to)
  // connect: v2 -> t2  (connected_to)
  // connect: t2 -> v3  (connected_to)
  // connect: v3 -> drn  (connected_to)
  // connect: src -> drn  (connected_to)
  // connect: v1 -> v2  (regulates)
  // connect: v2 -> v3  (regulates)
  // connect: t1 -> lT_101  (depends_on)
  // connect: t2 -> lT_102  (depends_on)
  // connect: stop -> start  (depends_on)
  // connect: stop -> shut  (depends_on)
  // connect: stop -> start  (requires)
  // connect: shut -> v1  (controls)
  // connect: shut -> v2  (controls)
  // connect: shut -> v3  (controls)
  // connect: lT_101 -> t1  (connected_to)
  // connect: lT_102 -> tank2  (connected_to)
  // connect: xV_101 -> tK_101  (serves)
  // connect: xV_102 -> tK_102  (serves)
  // connect: xV_103 -> tK_101  (serves)
  // connect: shut -> stop  (controls)
  // connect: shut -> v2  (controls)
  // connect: shut -> v3  (controls)
  // connect: start -> shut  (controls)
  // connect: tankDemo_Rev12 -> tankDemo_Rev12  (contains)
  // connect: vxS_24_spring_return_two_position_liquid_isolation_valve -> _24_VDC_actuator  (composed_of)
  // connect: xV_101 -> vxS_24_spring_return_two_position_liquid_isolation_valve  (part_of)
  // connect: xV_102 -> vxS_24_spring_return_two_position_liquid_isolation_valve  (part_of)
  // connect: xV_103 -> vxS_24_spring_return_two_position_liquid_isolation_valve  (part_of)
  // connect: _24_VDC_actuator -> vxS_24_spring_return_two_position_liquid_isolation_valve  (serves)
  // connect: _24_VDC_actuator -> xV_101  (controls)
  // connect: _24_VDC_actuator -> xV_102  (controls)
  // connect: _24_VDC_actuator -> xV_103  (controls)
  // connect: xV_101 -> _24_VDC_actuator  (depends_on)
  // connect: xV_102 -> _24_VDC_actuator  (depends_on)
  // connect: xV_103 -> _24_VDC_actuator  (depends_on)
  // connect: plC_101 -> v1  (controls)
  // connect: plC_101 -> v2  (controls)
  // connect: plC_101 -> v3  (controls)
  // connect: plC_101 -> t1  (serves)
  // connect: plC_101 -> t2  (serves)
  // connect: v2 -> v3  (mutually_exclusive)
  // connect: controller -> valve1  (controls)
  // connect: controller -> valve2  (controls)
  // connect: controller -> valve3  (controls)
  // connect: tank1 -> valve1  (connected_to)
  // connect: tank1 -> valve2  (connected_to)
  // connect: tank2 -> valve2  (connected_to)
  // connect: tank2 -> valve3  (connected_to)
  connect(valveIncompressible.port_a, openTank.ports[1]);
  connect(valveIncompressible_2.port_a, openTank.ports[2]);
  connect(valveIncompressible_2.port_b, openTank_2.ports[1]);
  connect(valveIncompressible_3.port_a, openTank_2.ports[2]);
  connect(valveIncompressible.port_b, openTank.ports[3]);
  connect(openTank_2.ports[3], valveIncompressible_3.port_b);
  // assert-candidate: BEH-0022 -- This is an interlock forbidding simultaneous opening of V1 and V2 in normal operation; assertions are appropriate for safety constraints.
  // assert-candidate: BEH-0023 -- This is a normal-operation interlock forbidding simultaneous opening of V2 and V3, which should be enforced as an assertion constraint.
  // assert-candidate: BEH-0039 -- This is an explicit safety prohibition on simultaneous opening, appropriate as an assertion/interlock.
  // assert-candidate: BEH-0040 -- This is an explicit normal-operation interlock, best mapped as an assertion.
  // assert-candidate: BEH-0048 -- This is an explicit prohibition against an unsafe simultaneous open command combination, so assertion is appropriate.
  // assert-candidate: BEH-0049 -- This is a normal-operation interlock forbidding simultaneous open commands, best modeled as an assertion.
  // assert-candidate: BEH-0055 -- This is a bounded effective high limit constraint on the tank setpoint value, suitable as an assertion.
  // assert-candidate: CON-0001 -- The initial level is a fixed bounded value, best expressed as an assertion/parameter constraint on the tank state.
  // assert-candidate: CON-0002 -- The initial level is a fixed bounded value, best expressed as an assertion/parameter constraint on the tank state.
  // assert-candidate: CON-0003 -- The high limit is a fixed bound on the tank level used by the controller, appropriate as an assertion-style constraint.
  // assert-candidate: CON-0004 -- The low limit is a fixed bound on the tank level, best represented as a constraint/assertion.
  // assert-candidate: CON-0005 -- The low limit is a fixed bound on the tank level, best represented as a constraint/assertion.
  // assert-candidate: CON-0006 -- The waiting time after T1 high is a fixed duration constraint, appropriate as an assertion on a delay parameter.
  // assert-candidate: CON-0007 -- The waiting time after T1 low is a fixed duration constraint, appropriate as an assertion on a delay parameter.
  // assert-candidate: CON-0008 -- The waiting time after T2 low is a fixed duration constraint, appropriate as an assertion on a delay parameter.
  // assert-candidate: CON-0009 -- This is the Tank 1 high-level setpoint used by the controller, a fixed bounded level constraint.
  // assert-candidate: CON-0010 -- This is the Tank 1 low-level setpoint, a fixed level constraint.
  // assert-candidate: CON-0011 -- This is the Tank 2 low-level setpoint, a fixed level constraint.
  // assert-candidate: CON-0012 -- A fixed post-transfer waiting time is a timing constraint, best represented as an assertion on the parameter value.
  // assert-candidate: CON-0013 -- A fixed inter-cycle waiting time is a timing constraint, best represented as an assertion on the parameter value.
  // assert-candidate: CON-0014 -- Controller scan time is a fixed timing constraint on discrete evaluation, appropriate as an assertion/parameter constraint.
  // assert-candidate: CON-0015 -- Simulation duration is a fixed run constraint and should be preserved as an assertion-like parameter constraint.
  // assert-candidate: CON-0016 -- The measurement engineering range is a bounded property suitable for an assertion constraint.
  // assert-candidate: CON-0017 -- Fixed initial level constraint on Tank 1, best preserved as an assertion/parameter constraint.
  // assert-candidate: CON-0018 -- Fixed initial level constraint on Tank 2, best preserved as an assertion/parameter constraint.
  // assert-candidate: CON-0019 -- Maximum working level is a bounded tank limit and fits naturally as an assertion constraint.
  // assert-candidate: CON-0020 -- Tank cross-section area is a fixed physical parameter; preserving it as a constraint/assertion is appropriate for the OpenTank instantiation.
  // assert-candidate: CON-0021 -- Tank cross-section area is a fixed physical parameter; preserving it as a constraint/assertion is appropriate for the OpenTank instantiation.
  // assert-candidate: CON-0022 -- Tank height is a required fixed physical dimension, best represented as a constraint/parameter assertion.
  // assert-candidate: CON-0023 -- Tank height is a required fixed physical dimension, best represented as a constraint/parameter assertion.
  // assert-candidate: CON-0024 -- The nominal flow is a fixed sizing constraint for the valve, appropriate as an assertion/parameter bound.
  // assert-candidate: CON-0025 -- The nominal flow is a fixed sizing constraint for the valve, appropriate as an assertion/parameter bound.
  // assert-candidate: CON-0026 -- The nominal flow is a fixed sizing constraint for the valve, appropriate as an assertion/parameter bound.
  // assert-candidate: CON-0027 -- Default initial level is a fixed start constraint that should be preserved on reuse.
  // assert-candidate: CON-0028 -- Default initial level is a fixed start constraint that should be preserved on reuse.
  // assert-candidate: CON-0029 -- Simultaneous open status is an explicit forbidden boolean condition, suitable as an assertion.
  // assert-candidate: CON-0030 -- This is an explicit normal-operation mutual-exclusion constraint, best modeled as an assertion.
  // assert-candidate: CON-0031 -- Simultaneous opening is allowed in SHUTDOWN, so this is a permitted boolean condition to preserve as an assertion-style constraint.
  // assert-candidate: CON-0032 -- This documents inclusive comparison semantics for the high threshold, which should be preserved as an assertional condition on controller logic.
  // assert-candidate: CON-0033 -- This documents inclusive comparison semantics for the low threshold, which should be preserved as an assertional condition on controller logic.
  // assert-candidate: CON-0034 -- This preserves the baseline-relative lower bound on the T1 high limit as a fixed constraint.
  // assert-candidate: CON-0035 -- This is an upper bound on the T1 high threshold, best retained as a constraint/assertion.
  // assert-candidate: CON-0036 -- The post-transfer delay is a fixed waiting time, suitable as a constraint assertion.
  // assert-candidate: CON-0037 -- The inter-cycle delay is a fixed waiting time, suitable as a constraint assertion.
  // assert-candidate: CON-0038 -- The fill target is a fixed level setpoint, naturally represented as a constraint/assertion.
  // assert-candidate: CON-0039 -- The low-level wait time is a fixed dead time constraint, best expressed as an assertion.
  // assert-candidate: CON-0040 -- The low-to-fill delay is a fixed dead time constraint, best expressed as an assertion.
  // assert-candidate: CON-0041 -- The effective high limit is bounded above by 0.8 m, so an assertion captures the constraint directly.
  // assert-candidate: CON-0042 -- This is a fixed waiting-time constraint, suitable as an assertion.
  // assert-candidate: CON-0043 -- This is a fixed waiting-time constraint, suitable as an assertion.
  // assert-candidate: CON-0044 -- The tank1Level signal is identified but no numeric bounds are provided, so keeping it as a generic assertion placeholder is safest.
  // assert-candidate: CON-0045 -- The tank2Level signal is identified but no numeric bounds are provided, so keeping it as a generic assertion placeholder is safest.
  // assert-candidate: CON-0046 -- The nominal demo flow coefficient equivalent constrains the valve sizing and can be preserved as an assertion/parameter bound.
  // assert-candidate: CON-0047 -- The nominal demo flow coefficient equivalent constrains the valve sizing and can be preserved as an assertion/parameter bound.
  // assert-candidate: CON-0048 -- The nominal demo flow coefficient equivalent constrains the valve sizing and can be preserved as an assertion/parameter bound.
  // assert-candidate: CON-0049 -- Full open stroke time is a fixed actuator timing constraint, suitable as an assertion.
  // assert-candidate: CON-0050 -- Full open stroke time is a fixed actuator timing constraint, suitable as an assertion.
  // assert-candidate: CON-0051 -- Full open stroke time is a fixed actuator timing constraint, suitable as an assertion.
  // assert-candidate: CON-0052 -- Full close stroke time is a fixed actuator timing constraint, suitable as an assertion.
  // assert-candidate: CON-0053 -- Full close stroke time is a fixed actuator timing constraint, suitable as an assertion.
  // assert-candidate: CON-0054 -- Full close stroke time is a fixed actuator timing constraint, suitable as an assertion.
  // assert-candidate: CON-0055 -- Starting tank level is a fixed initial condition and should be preserved as a constraint assertion.
  // assert-candidate: CON-0056 -- Starting tank level is a fixed initial condition and should be preserved as a constraint assertion.
  // assert-candidate: CON-0057 -- The simulation horizon is a fixed run constraint suitable as an assertion on the experiment setup.
  // assert-candidate: CON-0058 -- Logging interval is a fixed experiment constraint, best represented as an assertion/parameter value.
  // assert-candidate: CON-0059 -- This is a bounded simulation-time variable, so an assertion captures the allowable range.
  // assert-candidate: CON-0060 -- The command value is a bounded discrete signal, appropriate as an assertion constraint.
  // assert-candidate: CON-0061 -- The command value is a bounded discrete signal, appropriate as an assertion constraint.
  // assert-candidate: CON-0062 -- The command value is a bounded discrete signal, appropriate as an assertion constraint.
  // assert-candidate: CON-0063 -- The tank1_level_m variable is explicitly bounded, so an assertion is appropriate.
  // assert-candidate: CON-0064 -- The tank2_level_m variable is explicitly bounded, so an assertion is appropriate.
  // assert-candidate: CON-0065 -- Valve opening is a bounded Boolean-like command signal; preserving the range as an assertion is appropriate.
  // assert-candidate: CON-0066 -- Valve opening is a bounded Boolean-like command signal; preserving the range as an assertion is appropriate.
  // assert-candidate: CON-0067 -- Valve opening is a bounded Boolean-like command signal; preserving the range as an assertion is appropriate.
  // assert-candidate: CON-0068 -- The remaining wait time is a bounded timer state, appropriate as an assertion.
end Tank003System;
