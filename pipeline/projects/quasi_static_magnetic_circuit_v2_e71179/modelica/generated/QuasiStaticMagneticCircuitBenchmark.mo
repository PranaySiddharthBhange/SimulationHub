model QuasiStaticMagneticCircuitBenchmark
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.Length a_m = 0.025;
  parameter Modelica.Units.SI.Length l_m = 0.150;
  parameter Modelica.Units.SI.Length delta_m = 0.00150;
  parameter Modelica.Units.SI.Length prototype_gap_m = 0.00158;
  parameter Real prototype_gap_uncertainty_m = 2e-05;
  parameter Real mu_r = 1200;
  parameter Real sigma = 0.08;
  parameter Integer N_exc = 600;
  parameter Integer N_meas = 50;
  parameter Modelica.Units.SI.Frequency f_Hz = 50;
  parameter Modelica.Units.SI.Permeability mu0_H_per_m = 1.2566370614359173e-6;
  parameter Modelica.Units.SI.Time simulation_start_s = 0.0;
  parameter Modelica.Units.SI.Time simulation_stop_s = 1.0;
  parameter Real simulation_tolerance = 1e-6;
  parameter Modelica.Units.SI.Area A_m2 = a_m*a_m;
  parameter Modelica.Units.SI.Length l_core_m = 3*(l_m - a_m) + (l_m - a_m - delta_m);

  Modelica.Blocks.Sources.Ramp currentRamp(
    height=2.0,
    duration=0.40,
    offset=0.0,
    startTime=0.10) annotation (Placement(transformation(extent={{-120,60},{-100,80}})));

  ExcitingCoilDrive excitingCoil(N_exc=N_exc)
    annotation (Placement(transformation(extent={{-70,50},{-30,90}})));
  MagneticCorePath magneticCorePath(
    a_m=a_m,
    l_m=l_m,
    delta_m=delta_m,
    mu_r=mu_r,
    sigma=sigma,
    mu0_H_per_m=mu0_H_per_m)
    annotation (Placement(transformation(extent={{-10,-20},{50,80}})));
  MeasuringCoilOutput measuringCoil(N_meas=N_meas, f_Hz=f_Hz)
    annotation (Placement(transformation(extent={{70,10},{110,50}})));

  Modelica.Blocks.Sources.RealExpression excitingVoltage(y=2*Modelica.Constants.pi*f_Hz*N_exc*magneticCorePath.Phi_core_Wb)
    annotation (Placement(transformation(origin = {2, -4}, extent = {{70, 70}, {90, 90}})));

  Modelica.Electrical.Analog.Basic.Ground electricGround
    annotation (Placement(transformation(extent={{-90,-90},{-70,-70}})));
  Modelica.Magnetic.FluxTubes.Basic.Ground magneticGround
    annotation (Placement(transformation(extent={{-50,-90},{-30,-70}})));

  Real time_s;
  Real I_rms_A;
  Real mmf_At;
  Real Phi_core_Wb;
  Real Phi_gap_Wb;
  Real Phi_leak_Wb;
  Real Phi_gap_over_Phi_core;
  Real B_core_T;
  Real B_gap_T;
  Real H_core_A_m;
  Real H_gap_A_m;
  Real Vm_core_At;
  Real Vm_gap_At;
  Real U_exc_induced_V_rms;
  Real U_meas_induced_signed_V_rms;
  Real R_core_A_per_Wb;
  Real R_gap_A_per_Wb;
  Real R_leak_A_per_Wb;
  Real R_par_A_per_Wb;
  Real R_total_A_per_Wb;

equation
  connect(currentRamp.y, excitingCoil.I_rms_A) annotation(Line(points={{-99,70},{-72,70}}, color={0,0,127}));
  connect(excitingCoil.mmf_At, magneticCorePath.mmf_At) annotation(Line(points={{-29,70},{-12,70}}, color={0,0,127}));
  connect(magneticCorePath.Phi_gap_Wb, measuringCoil.Phi_gap_Wb) annotation(Line(points={{51,50},{60,50},{60,30},{68,30}}, color={0,0,127}));

  time_s = time;
  I_rms_A = currentRamp.y;
  mmf_At = excitingCoil.mmf_At;
  Phi_core_Wb = magneticCorePath.Phi_core_Wb;
  Phi_gap_Wb = magneticCorePath.Phi_gap_Wb;
  Phi_leak_Wb = magneticCorePath.Phi_leak_Wb;
  Phi_gap_over_Phi_core = magneticCorePath.Phi_gap_over_Phi_core;
  B_core_T = magneticCorePath.B_core_T;
  B_gap_T = magneticCorePath.B_gap_T;
  H_core_A_m = magneticCorePath.H_core_A_m;
  H_gap_A_m = magneticCorePath.H_gap_A_m;
  Vm_core_At = magneticCorePath.Vm_core_At;
  Vm_gap_At = magneticCorePath.Vm_gap_At;
  U_exc_induced_V_rms = excitingVoltage.y;
  U_meas_induced_signed_V_rms = measuringCoil.U_meas_induced_signed_V_rms;
  R_core_A_per_Wb = magneticCorePath.R_core_A_per_Wb;
  R_gap_A_per_Wb = magneticCorePath.R_gap_A_per_Wb;
  R_leak_A_per_Wb = magneticCorePath.R_leak_A_per_Wb;
  R_par_A_per_Wb = magneticCorePath.R_par_A_per_Wb;
  R_total_A_per_Wb = magneticCorePath.R_total_A_per_Wb;

  assert(abs(mmf_At - Vm_core_At - Vm_gap_At) <= max(1e-9, 0.01*max(1.0, abs(mmf_At))), "mmf balance deviated by more than 1% during simulation");

  annotation (
    experiment(StartTime=0.0, StopTime=1.0, Tolerance=1e-6, Interval=0.001),
    Diagram(graphics={Text(origin = {-4, 20}, extent = {{-138, 104}, {138, 92}}, textString = "Released nominal quasi-static magnetic benchmark")}),
    Icon(graphics={Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end QuasiStaticMagneticCircuitBenchmark;
