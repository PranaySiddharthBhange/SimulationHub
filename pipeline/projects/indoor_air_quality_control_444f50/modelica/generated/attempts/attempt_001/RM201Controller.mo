model RM201Controller
  type Mode = enumeration(AUTO_MIN, AUTO_CO2, AUTO_MAX, SENSOR_FAULT);
  parameter Real C_nominal(unit="kg/kg") = 1.519e-3;
  parameter Real Kp(unit="1/h") = 6.0 "ACH per normalized concentration error";
  parameter Real bias(unit="1/h") = 3.5;
  parameter Real uMin(unit="1/h") = 0.2;
  parameter Real uMax(unit="1/h") = 6.0;
  parameter Real sensorFaultOutput(unit="1/h") = 4.0;
  parameter Modelica.Units.SI.Time faultDelay = 60;
  Modelica.Blocks.Interfaces.RealInput room_co2_mass_fraction_kgkg annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.BooleanInput sensor_valid annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealOutput normalized_co2_feedback annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput ach_command_1_per_h annotation(Placement(transformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.IntegerOutput controller_mode annotation(Placement(transformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.BooleanOutput sensor_fault_indication annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
protected 
  Real requested_ach_1_per_h;
  Real invalidTimer(start=0, fixed=true);
  Mode mode(start=Mode.AUTO_MIN, fixed=true);
equation 
  normalized_co2_feedback = room_co2_mass_fraction_kgkg/C_nominal;
  requested_ach_1_per_h = bias + Kp*(normalized_co2_feedback - 1.0);
  der(invalidTimer) = if sensor_valid then 0 else 1;
  ach_command_1_per_h = if mode == Mode.SENSOR_FAULT then sensorFaultOutput else if requested_ach_1_per_h <= uMin then uMin else if requested_ach_1_per_h >= uMax then uMax else requested_ach_1_per_h;
  sensor_fault_indication = mode == Mode.SENSOR_FAULT;
  controller_mode = if mode == Mode.AUTO_MIN then 0 else if mode == Mode.AUTO_CO2 then 1 else if mode == Mode.AUTO_MAX then 2 else 3;
algorithm 
  when {initial(), (not sensor_valid) and pre(invalidTimer) > faultDelay, sensor_valid, requested_ach_1_per_h <= uMin, requested_ach_1_per_h >= uMax, (requested_ach_1_per_h > uMin) and (requested_ach_1_per_h < uMax)} then
    if initial() then
      if requested_ach_1_per_h <= uMin then
        mode := Mode.AUTO_MIN;
      elseif requested_ach_1_per_h >= uMax then
        mode := Mode.AUTO_MAX;
      else
        mode := Mode.AUTO_CO2;
      end if;
    elseif not sensor_valid and pre(invalidTimer) > faultDelay then
      mode := Mode.SENSOR_FAULT;
    elseif sensor_valid then
      reinit(invalidTimer, 0);
      if requested_ach_1_per_h <= uMin then
        mode := Mode.AUTO_MIN;
      elseif requested_ach_1_per_h >= uMax then
        mode := Mode.AUTO_MAX;
      else
        mode := Mode.AUTO_CO2;
      end if;
    elseif pre(mode) <> Mode.SENSOR_FAULT then
      if requested_ach_1_per_h <= uMin then
        mode := Mode.AUTO_MIN;
      elseif requested_ach_1_per_h >= uMax then
        mode := Mode.AUTO_MAX;
      else
        mode := Mode.AUTO_CO2;
      end if;
    end if;
  end when;
  annotation(
    Icon(graphics={Rectangle(extent={{-100,-80},{100,80}}, lineColor={255,0,255}, fillColor={255,240,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-90,20},{90,60}}, textString="CO2 CTRL"),Text(extent={{-90,-10},{90,10}}, textString="kg/kg->ACH")}),
    Diagram(graphics={Rectangle(extent={{-100,-80},{100,80}}, lineColor={255,0,255})}));
end RM201Controller;
