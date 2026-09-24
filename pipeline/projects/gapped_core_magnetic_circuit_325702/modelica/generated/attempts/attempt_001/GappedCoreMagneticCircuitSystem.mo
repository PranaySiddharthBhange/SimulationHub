model GappedCoreMagneticCircuitSystem
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.Time simulation_duration_s = 1.0;
  parameter Integer output_intervals = 1000;

  Modelica.Blocks.Sources.Ramp excitationCurrent(
    height=2,
    duration=0.1,
    offset=0,
    startTime=0) annotation(Placement(transformation(extent={{-100,30},{-80,50}})));
  ExcitationCoil excitationCoil(N=500) annotation(Placement(transformation(extent={{-50,20},{-10,60}})));
  MagneticCoreWithGap magneticCoreWithGap(
    N=500,
    l_core=0.4,
    A=0.0004,
    mu_r=2000,
    l_gap=0.002) annotation(Placement(transformation(extent={{20,-10},{80,70}})));

  Real mmf_At;
  Real Phi_core_Wb;
  Real B_core_T;
  Real B_gap_T;
  Real Vm_core_At;
  Real Vm_gap_At;
 equation
  connect(excitationCurrent.y, excitationCoil.current_A) annotation(Line(points={{-79,40},{-50,40}}, color={0,0,127}));
  connect(excitationCurrent.y, magneticCoreWithGap.current_A) annotation(Line(points={{-79,40},{-60,40},{-60,74},{20,74}}, color={0,0,127}));
  connect(excitationCoil.mmf_At, magneticCoreWithGap.mmf_At) annotation(Line(points={{-10,40},{20,40}}, color={0,0,127}));

  mmf_At = excitationCoil.mmf_At;
  Phi_core_Wb = magneticCoreWithGap.Phi_core_Wb;
  B_core_T = magneticCoreWithGap.B_core_T;
  B_gap_T = magneticCoreWithGap.B_gap_T;
  Vm_core_At = magneticCoreWithGap.Vm_core_At;
  Vm_gap_At = magneticCoreWithGap.Vm_gap_At;

 annotation(
  experiment(StartTime=0, StopTime=1, Tolerance=1e-6, Interval=0.001),
  Diagram(graphics={Text(extent={{-140,90},{140,110}}, textString="Gapped Core Magnetic Circuit — Ramped Excitation")}));
end GappedCoreMagneticCircuitSystem;
