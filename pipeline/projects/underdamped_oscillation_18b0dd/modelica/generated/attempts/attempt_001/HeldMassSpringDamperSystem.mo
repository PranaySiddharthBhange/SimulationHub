model HeldMassSpringDamperSystem
  parameter Modelica.Units.SI.Mass mass_kg = 1.0;
  parameter Modelica.Units.SI.TranslationalSpringConstant stiffness_N_per_m = 1.0;
  parameter Modelica.Units.SI.TranslationalDampingConstant damping_coefficient_N_s_per_m = 0.2;
  parameter Modelica.Units.SI.Position held_position_m = 0.10;
  parameter Modelica.Units.SI.Time clamp_release_time_s = 5.0;

  Modelica.Mechanics.Translational.Components.Mass mass(m=mass_kg, s(start=held_position_m, fixed=true), v(start=0, fixed=true))
    annotation(Placement(transformation(extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Translational.Components.Spring spring(c=stiffness_N_per_m, s_rel0=0)
    annotation(Placement(transformation(extent={{-10,40},{10,60}})));
  Modelica.Mechanics.Translational.Components.Damper damper(d=damping_coefficient_N_s_per_m)
    annotation(Placement(transformation(extent={{-10,-60},{10,-40}})));
  Modelica.Mechanics.Translational.Components.Fixed fixedWall
    annotation(Placement(transformation(extent={{60,-10},{80,10}})));
  ClampConstraint clamp(heldPosition=held_position_m)
    annotation(Placement(transformation(extent={{-60,-10},{-40,10}})));
  ReleaseCommand releaseCommand(releaseTime=clamp_release_time_s)
    annotation(Placement(transformation(extent={{-100,40},{-80,60}})));

  Real position_m;
  Real velocity_m_s;
  Real clamp_engaged;
equation
  connect(clamp.flange, mass.flange_a)
    annotation(Line(points={{-40,0},{-10,0}}, color={0,127,255}));
  connect(mass.flange_b, spring.flange_a)
    annotation(Line(points={{10,0},{20,0},{20,50},{-10,50}}, color={0,127,255}));
  connect(spring.flange_b, fixedWall.flange)
    annotation(Line(points={{10,50},{40,50},{40,0},{60,0}}, color={0,127,255}));
  connect(mass.flange_b, damper.flange_a)
    annotation(Line(points={{10,0},{20,0},{20,-50},{-10,-50}}, color={0,127,255}));
  connect(damper.flange_b, fixedWall.flange)
    annotation(Line(points={{10,-50},{40,-50},{40,0},{60,0}}, color={0,127,255}));
  connect(releaseCommand.engaged, clamp.engaged)
    annotation(Line(points={{20,50},{-70,50},{-70,0},{-60,0}}, color={255,0,255}));

  position_m = mass.s;
  velocity_m_s = mass.v;
  clamp_engaged = clamp.clamp_engaged;

annotation(
  experiment(StartTime=0, StopTime=150, Tolerance=1e-6, Interval=0.1),
  Diagram(graphics={
    Text(extent={{-100,90},{100,110}}, textString="Held mass released onto spring-damper")
  }));
end HeldMassSpringDamperSystem;
