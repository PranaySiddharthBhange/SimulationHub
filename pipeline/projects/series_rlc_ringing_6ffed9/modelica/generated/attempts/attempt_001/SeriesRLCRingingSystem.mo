model SeriesRLCRingingSystem
  parameter Modelica.Units.SI.Capacitance C = 1;
  parameter Modelica.Units.SI.Resistance R = 0.2;
  parameter Modelica.Units.SI.Inductance L = 1;
  parameter Modelica.Units.SI.Voltage V0 = 10;
  parameter Modelica.Units.SI.Current I0 = 0;
  parameter Modelica.Units.SI.Time switchCloseTime = 5.0;

  Modelica.Electrical.Analog.Basic.Capacitor capacitor(C=C, v(start=V0, fixed=true)) annotation(Placement(transformation(extent={{-10,50},{10,70}})));
  Modelica.Electrical.Analog.Basic.Resistor resistor(R=R) annotation(Placement(transformation(extent={{20,-10},{40,10}})));
  Modelica.Electrical.Analog.Basic.Inductor inductor(L=L, i(start=I0, fixed=true)) annotation(Placement(transformation(extent={{60,-10},{80,10}})));
  IdealClosingSwitch switch(closeTime=switchCloseTime) annotation(Placement(transformation(extent={{-40,-10},{-20,10}})));

  Modelica.Blocks.Interfaces.RealOutput capacitor_voltage_V annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput loop_current_A annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.RealOutput switch_closed annotation(Placement(transformation(extent={{100,-10},{120,10}})));

equation
  connect(switch.n, resistor.p) annotation(Line(points={{-20,0},{20,0}}, color={0,127,255}));
  connect(resistor.n, inductor.p) annotation(Line(points={{40,0},{60,0}}, color={0,127,255}));
  connect(inductor.n, capacitor.p) annotation(Line(points={{80,0},{90,0},{90,60},{10,60}}, color={0,127,255}));
  connect(capacitor.n, switch.p) annotation(Line(points={{-10,60},{-90,60},{-90,0},{-40,0}}, color={0,127,255}));

  capacitor_voltage_V = capacitor.v;
  loop_current_A = inductor.i;
  switch_closed = if switch.closed then 1.0 else 0.0;

  annotation(
    experiment(StartTime=0, StopTime=150, Tolerance=1e-6, Interval=0.15),
    Icon(graphics={Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-94,88},{86,98}}, textString="Pre-charged capacitor released into series R-L at t=5 s")})
  );
end SeriesRLCRingingSystem;
