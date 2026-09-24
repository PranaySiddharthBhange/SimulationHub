model GappedCoreMagneticCircuitSystem
  extends Modelica.Icons.Example;

  parameter Integer turns_nominal = 500;
  parameter Modelica.Units.SI.Length core_mean_path_length_m = 0.4;
  parameter Modelica.Units.SI.Area cross_section_m2 = 0.0004;
  parameter Real core_relative_permeability_nominal = 2000.0;
  parameter Modelica.Units.SI.Length gap_length_m = 0.002;
  parameter Modelica.Units.SI.Time simulation_duration_s = 1.0;
  parameter Integer output_intervals = 1000;

  Modelica.Blocks.Sources.Ramp excitationCurrent(
    height=2,
    duration=0.1,
    offset=0,
    startTime=0) annotation(Placement(transformation(extent={{-180,40},{-160,60}})));
  ExcitationCoil Excitation_coil(N=turns_nominal) annotation(Placement(transformation(extent={{-130,30},{-90,70}})));
  IronCore Core_iron_path(
    mean_path_length_m=core_mean_path_length_m,
    cross_section_m2=cross_section_m2,
    relative_permeability_nominal=core_relative_permeability_nominal) annotation(Placement(transformation(extent={{-20,20},{20,80}})));
  AirGap Air_gap(
    length_m=gap_length_m,
    cross_section_m2=cross_section_m2) annotation(Placement(transformation(extent={{60,20},{100,80}})));
  MagneticReference Magnetic_reference annotation(Placement(transformation(extent={{130,20},{170,80}})));
  MagneticGroundUnit magnetic_ground annotation(Placement(transformation(extent={{190,30},{230,70}})));

  Real mmf_At;
  Real Phi_core_Wb;
  Real B_core_T;
  Real B_gap_T;
  Real Vm_core_At;
  Real Vm_gap_At;
protected 
  constant Real mu0 = Modelica.Constants.mu_0;
  final parameter Real R_core = core_mean_path_length_m/(mu0*core_relative_permeability_nominal*cross_section_m2);
  final parameter Real R_gap = gap_length_m/(mu0*cross_section_m2);
equation
  connect(excitationCurrent.y, Excitation_coil.current_A) annotation(Line(points={{-159,50},{-130,50}}, color={0,0,127}));

  Phi_core_Wb = Excitation_coil.mmf_At/(R_core + R_gap);
  Core_iron_path.Phi_Wb = Phi_core_Wb;
  Air_gap.Phi_Wb = Phi_core_Wb;
  Magnetic_reference.Phi_Wb = Phi_core_Wb;
  connect(Magnetic_reference.reference_At, magnetic_ground.reference_At) annotation(Line(points={{170,-50},{180,-50},{180,50},{190,50}}, color={0,0,127}));

  mmf_At = Excitation_coil.mmf_At;
  B_core_T = Core_iron_path.B_core_T;
  Vm_core_At = Core_iron_path.Vm_core_At;
  B_gap_T = Air_gap.B_gap_T;
  Vm_gap_At = Air_gap.Vm_gap_At;

  annotation(
    experiment(StartTime=0, StopTime=1, Tolerance=1e-6, Interval=0.001),
    Diagram(graphics={Text(extent={{-220,100},{220,120}}, textString="Gapped Core Magnetic Circuit — Ramped Excitation")}));
end GappedCoreMagneticCircuitSystem;
