model SeriesRLCRingingSystem
  parameter Modelica.Units.SI.Capacitance C = 1;
  parameter Modelica.Units.SI.Resistance R = 0.2;
  parameter Modelica.Units.SI.Inductance L = 1;
  parameter Modelica.Units.SI.Voltage V0 = 10;
  parameter Modelica.Units.SI.Current I0 = 0;
  parameter Modelica.Units.SI.Time switchCloseTime = 5.0;

  ScheduledSwitch scheduledSwitch(closeTime=switchCloseTime)
    annotation(Placement(transformation(extent={{-80,40},{-40,80}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor(R=R)
    annotation(Placement(transformation(extent={{-10,10},{10,30}})));
  Modelica.Electrical.Analog.Basic.Inductor inductor(L=L, i(start=I0, fixed=true))
    annotation(Placement(transformation(extent={{30,10},{50,30}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(C=C, v(start=V0, fixed=true))
    annotation(Placement(transformation(extent={{-10,-30},{10,-10}})));
  Modelica.Electrical.Analog.Ideal.IdealClosingSwitch idealSwitch(Ron=1e-6, Goff=1e-6)
    annotation(Placement(transformation(extent={{-50,10},{-30,30}})));
  Modelica.Electrical.Analog.Basic.Ground ground
    annotation(Placement(transformation(extent={{-10,-70},{10,-50}})));

  Modelica.Units.SI.Voltage capacitor_voltage_V;
  Modelica.Units.SI.Current loop_current_A;
  Real switch_closed;
  parameter Real damping_ratio_zeta = 0.1;
  parameter Real natural_frequency_omega_n_rad_per_s = 1.0;
equation
  connect(idealSwitch.n, resistor.p) annotation(Line(points={{-30,20},{-10,20}}, color={0,127,255}));
  connect(resistor.n, inductor.p) annotation(Line(points={{10,20},{30,20}}, color={0,127,255}));
  connect(inductor.n, capacitor.p) annotation(Line(points={{50,20},{70,20},{70,-20},{10,-20}}, color={0,127,255}));
  connect(capacitor.n, idealSwitch.p) annotation(Line(points={{-10,-20},{-70,-20},{-70,20},{-50,20}}, color={0,127,255}));
  connect(capacitor.n, ground.p) annotation(Line(points={{-10,-20},{0,-20},{0,-50}}, color={0,127,255}));
  connect(scheduledSwitch.closed, idealSwitch.control) annotation(Line(points={{-39,60},{-20,60},{-20,32},{-40,32}}, color={255,0,255}));

  capacitor_voltage_V = capacitor.v;
  loop_current_A = inductor.i;
  switch_closed = if scheduledSwitch.closed then 1 else 0;

annotation(
  experiment(StartTime=0, StopTime=150, Interval=0.15),
  Diagram(graphics={
    Text(extent={{-100,94},{100,110}}, textString="Pre-charged capacitor released into series R-L loop at t=5 s")
  }));
end SeriesRLCRingingSystem;
