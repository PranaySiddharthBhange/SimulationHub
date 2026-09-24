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
  ach_command_1_per_h = if mode == Mode.SENSOR_FAULT then sensorFaultOutput else if requested_ach_1_per_h <= uMin then uMin else if requested_ach_1_per_h >= uMax then uMax else requested_ach_1_per_h;
  sensor_fault_indication = mode == Mode.SENSOR_FAULT;
  controller_mode = Integer(mode) - 1;
algorithm
  when change(sensor_valid) then
    if not sensor_valid then
      invalidStartTime := time;
    end if;
  end when;

  when {pre(mode) <> Mode.SENSOR_FAULT and not sensor_valid and time - pre(invalidStartTime) > sensorFaultDelay,
        pre(mode) == Mode.SENSOR_FAULT and sensor_valid,
        pre(mode) <> Mode.SENSOR_FAULT and sensor_valid and requested_ach_1_per_h <= uMin,
        pre(mode) <> Mode.SENSOR_FAULT and sensor_valid and requested_ach_1_per_h >= uMax,
        pre(mode) <> Mode.SENSOR_FAULT and sensor_valid and requested_ach_1_per_h > uMin and requested_ach_1_per_h < uMax} then
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
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={255,127,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name"), Text(extent={{-90,60},{-20,40}}, textString="nCO2"), Text(extent={{-90,-80},{-20,-60}}, textString="valid"), Text(extent={{20,60},{90,40}}, textString="ACH"), Text(extent={{20,0},{90,-20}}, textString="mode"), Text(extent={{10,-80},{90,-60}}, textString="fault")}), Diagram(coordinateSystem(extent={{-100,-100},{100,100}})));
end CO2RoomController;
