model CO2RoomController
  type Mode = enumeration(AUTO_MIN, AUTO_CO2, AUTO_MAX, SENSOR_FAULT);
  Modelica.Blocks.Interfaces.RealInput normalized_co2_feedback annotation(Placement(transformation(extent={{-120,50},{-100,70}}), iconTransformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.BooleanInput sensor_valid annotation(Placement(transformation(extent={{-120,-70},{-100,-50}}), iconTransformation(extent={{-120,-70},{-100,-50}})));
  Modelica.Blocks.Interfaces.RealOutput ach_command_1_per_h annotation(Placement(transformation(extent={{100,50},{120,70}}), iconTransformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_mode annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Interfaces.BooleanOutput sensor_fault_indication annotation(Placement(transformation(extent={{100,-70},{120,-50}}), iconTransformation(extent={{100,-70},{120,-50}})));
  parameter Real Kp = 6.0;
  parameter Real bias = 3.5;
  parameter Real uMin = 0.2;
  parameter Real uMax = 6.0;
  parameter Real sensorFaultOutput = 4.0;
  parameter Modelica.Units.SI.Time sensorFaultDelay = 60;
  Real requested_ach_1_per_h;
  discrete Mode mode(start=Mode.AUTO_MIN, fixed=true);
  discrete Real invalidStartTime(start=0, fixed=true);
equation
  requested_ach_1_per_h = bias + Kp*(normalized_co2_feedback - 1.0);
  if mode == Mode.SENSOR_FAULT then
    ach_command_1_per_h = sensorFaultOutput;
    sensor_fault_indication = true;
  elseif requested_ach_1_per_h <= uMin then
    ach_command_1_per_h = uMin;
    sensor_fault_indication = false;
  elseif requested_ach_1_per_h >= uMax then
    ach_command_1_per_h = uMax;
    sensor_fault_indication = false;
  else
    ach_command_1_per_h = requested_ach_1_per_h;
    sensor_fault_indication = false;
  end if;

  controller_mode = Integer(mode) - 1;
algorithm
  when {change(sensor_valid), pre(mode) <> Mode.SENSOR_FAULT and not sensor_valid and time - pre(invalidStartTime) > sensorFaultDelay, pre(mode) == Mode.SENSOR_FAULT and sensor_valid, pre(mode) <> Mode.SENSOR_FAULT and requested_ach_1_per_h <= uMin, pre(mode) <> Mode.SENSOR_FAULT and requested_ach_1_per_h >= uMax, pre(mode) <> Mode.SENSOR_FAULT and requested_ach_1_per_h > uMin and requested_ach_1_per_h < uMax} then
    if change(sensor_valid) and not sensor_valid then
      invalidStartTime := time;
    end if;

    if pre(mode) <> Mode.SENSOR_FAULT and not sensor_valid and time - pre(invalidStartTime) > sensorFaultDelay then
      mode := Mode.SENSOR_FAULT;
    elseif pre(mode) == Mode.SENSOR_FAULT and sensor_valid then
      if requested_ach_1_per_h <= uMin then
        mode := Mode.AUTO_MIN;
      elseif requested_ach_1_per_h >= uMax then
        mode := Mode.AUTO_MAX;
      else
        mode := Mode.AUTO_CO2;
      end if;
    elseif sensor_valid then
      if requested_ach_1_per_h <= uMin then
        mode := Mode.AUTO_MIN;
      elseif requested_ach_1_per_h >= uMax then
        mode := Mode.AUTO_MAX;
      else
        mode := Mode.AUTO_CO2;
      end if;
    end if;
  end when;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={255,127,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name"), Text(extent={{-92,62},{-28,42}}, textString="nCO2"), Text(extent={{-94,-58},{-24,-78}}, textString="valid"), Text(extent={{24,62},{96,42}}, textString="ACH"), Text(extent={{20,2},{96,-18}}, textString="mode"), Text(extent={{6,-58},{96,-78}}, textString="fault")}), Diagram);
end CO2RoomController;
