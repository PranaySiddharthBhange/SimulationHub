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
  discrete Boolean invalidLatched(start=false, fixed=true);
equation
  requested_ach_1_per_h = bias + Kp*(normalized_co2_feedback - 1.0);
  ach_command_1_per_h = if mode == Mode.SENSOR_FAULT then sensorFaultOutput else if requested_ach_1_per_h <= uMin then uMin else if requested_ach_1_per_h >= uMax then uMax else requested_ach_1_per_h;
  controller_mode = Integer(mode) - 1;
  sensor_fault_indication = mode == Mode.SENSOR_FAULT;
algorithm
  when initial() then
    mode := Mode.AUTO_MIN;
    invalidLatched := not sensor_valid;
    invalidStartTime := if not sensor_valid then time else 0;
  elsewhen change(sensor_valid) or (pre(invalidLatched) and not sensor_valid and time - pre(invalidStartTime) > sensorFaultDelay) or (pre(mode) == Mode.SENSOR_FAULT and sensor_valid) or (pre(mode) <> Mode.SENSOR_FAULT and (requested_ach_1_per_h <= uMin or requested_ach_1_per_h >= uMax or (requested_ach_1_per_h > uMin and requested_ach_1_per_h < uMax))) then
    if change(sensor_valid) then
      invalidLatched := not sensor_valid;
      if not sensor_valid then
        invalidStartTime := time;
      end if;
    end if;
    if (not sensor_valid) and (if pre(invalidLatched) then time - pre(invalidStartTime) > sensorFaultDelay else false) then
      mode := Mode.SENSOR_FAULT;
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
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={255,127,0}, fillColor={255,255,170}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name"), Text(extent={{-92,62},{-28,42}}, textString="nCO2"), Text(extent={{-94,-58},{-24,-78}}, textString="valid"), Text(extent={{24,62},{96,42}}, textString="ACH"), Text(extent={{20,2},{96,-18}}, textString="mode"), Text(extent={{6,-58},{96,-78}}, textString="fault")}), Diagram(graphics={}));
end CO2RoomController;
