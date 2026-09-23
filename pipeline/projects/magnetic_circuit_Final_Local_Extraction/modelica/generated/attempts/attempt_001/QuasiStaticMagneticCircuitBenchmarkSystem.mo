model QuasiStaticMagneticCircuitBenchmarkSystem
  extends Modelica.Icons.Example;

  parameter Integer N_exc=600;
  parameter Integer N_meas=50;
  parameter Modelica.Units.SI.Frequency f=50;
  parameter Real mu_r=1200;
  parameter Modelica.Units.SI.Permeability mu0=1.2566370614359173e-06;
  parameter Modelica.Units.SI.Length a=0.025;
  parameter Modelica.Units.SI.Length l=0.150;
  parameter Modelica.Units.SI.Length delta=0.00150;
  parameter Real sigma=0.08;
  parameter Modelica.Units.SI.Area A=a*a;
  parameter Modelica.Units.SI.Length l_left=l-a;
  parameter Modelica.Units.SI.Length l_upper=l-a;
  parameter Modelica.Units.SI.Length l_lower=l-a;
  parameter Modelica.Units.SI.Length l_rightIron=l-a-delta;
  parameter Modelica.Units.SI.Length l_core=l_left + l_upper + l_rightIron + l_lower;
  parameter Modelica.Units.SI.Reluctance R_left=l_left/(mu0*mu_r*A);
  parameter Modelica.Units.SI.Reluctance R_upper=l_upper/(mu0*mu_r*A);
  parameter Modelica.Units.SI.Reluctance R_rightIron=l_rightIron/(mu0*mu_r*A);
  parameter Modelica.Units.SI.Reluctance R_lower=l_lower/(mu0*mu_r*A);
  parameter Modelica.Units.SI.Reluctance R_core=l_core/(mu0*mu_r*A);
  parameter Modelica.Units.SI.Reluctance R_gap=delta/(mu0*A);
  parameter Modelica.Units.SI.Reluctance R_leak=R_gap*(1 - sigma)/sigma;
  parameter Modelica.Units.SI.Reluctance R_par=1/(1/R_gap + 1/R_leak);
  parameter Modelica.Units.SI.Reluctance R_total=R_core + R_par;

  ExcitingCurrentProfile currentProfile annotation(Placement(transformation(extent={{-180,100},{-140,140}})));
  Modelica.Blocks.Math.Gain mmfGain(k=N_exc) annotation(Placement(transformation(extent={{-120,100},{-100,120}})));
  Modelica.Magnetic.FluxTubes.Sources.SignalMagneticPotentialDifference excitingCoil annotation(Placement(transformation(extent={{-140,-10},{-120,10}})));
  Modelica.Magnetic.FluxTubes.Basic.Ground magneticGround annotation(Placement(transformation(extent={{-170,-90},{-150,-70}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance leftLeg(R_m=R_left) annotation(Placement(transformation(extent={{-100,-10},{-80,10}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance upperYoke(R_m=R_upper) annotation(Placement(transformation(extent={{-60,-10},{-40,10}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance rightLegIron(R_m=R_rightIron) annotation(Placement(transformation(extent={{-20,-10},{0,10}})));
  LeakageBranchAssembly branchAssembly(R_gap=R_gap, R_leak=R_leak) annotation(Placement(transformation(extent={{20,-40},{80,40}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance lowerYoke(R_m=R_lower) annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor coreFluxSensor annotation(Placement(transformation(extent={{130,-10},{150,10}})));
  Modelica.Electrical.Analog.Basic.Ground electricGround annotation(Placement(transformation(extent={{-20,-110},{0,-90}})));

  Modelica.Units.SI.Current I_rms_A;
  Modelica.Units.SI.MagneticPotentialDifference mmf_At;
  Modelica.Units.SI.MagneticFlux Phi_core;
  Modelica.Units.SI.MagneticFlux Phi_gap;
  Modelica.Units.SI.MagneticFlux Phi_leak;
  Modelica.Units.SI.MagneticFluxDensity B_core;
  Modelica.Units.SI.MagneticFluxDensity B_gap;
  Modelica.Units.SI.MagneticFieldStrength H_iron;
  Modelica.Units.SI.MagneticFieldStrength H_air;
  Modelica.Units.SI.MagneticPotentialDifference Vm_gap;
  Modelica.Units.SI.MagneticPotentialDifference core_drop_At;
  Modelica.Units.SI.MagneticPotentialDifference residual;
  Modelica.Units.SI.Voltage U_exc;
  Modelica.Units.SI.Voltage U_meas;
  Real useful_to_core_flux_ratio;
equation
  connect(currentProfile.I_rms_A, mmfGain.u) annotation(Line(points={{-139,120},{-122,120},{-122,110}}, color={0,0,127}));
  connect(mmfGain.y, excitingCoil.V_m) annotation(Line(points={{-99,110},{-90,110},{-90,40},{-130,40},{-130,12}}, color={0,0,127}));
  connect(excitingCoil.port_n, magneticGround.port) annotation(Line(points={{-140,0},{-160,0},{-160,-70}}, color={0,127,255}));
  connect(excitingCoil.port_p, leftLeg.port_p) annotation(Line(points={{-120,0},{-100,0}}, color={0,127,255}));
  connect(leftLeg.port_n, upperYoke.port_p) annotation(Line(points={{-80,0},{-60,0}}, color={0,127,255}));
  connect(upperYoke.port_n, rightLegIron.port_p) annotation(Line(points={{-40,0},{-20,0}}, color={0,127,255}));
  connect(rightLegIron.port_n, branchAssembly.port_p) annotation(Line(points={{0,0},{20,0}}, color={0,127,255}));
  connect(branchAssembly.port_n, lowerYoke.port_p) annotation(Line(points={{80,0},{100,0}}, color={0,127,255}));
  connect(lowerYoke.port_n, coreFluxSensor.port_p) annotation(Line(points={{120,0},{130,0}}, color={0,127,255}));
  connect(coreFluxSensor.port_n, magneticGround.port) annotation(Line(points={{150,0},{160,0},{160,-60},{-160,-60},{-160,-70}}, color={0,127,255}));

  I_rms_A = currentProfile.I_rms_A;
  mmf_At = N_exc*I_rms_A;
  Phi_core = coreFluxSensor.Phi;
  Phi_gap = branchAssembly.Phi_gap;
  Phi_leak = branchAssembly.Phi_leak;
  B_core = Phi_core/A;
  B_gap = Phi_gap/A;
  H_iron = B_core/(mu0*mu_r);
  H_air = B_gap/mu0;
  Vm_gap = H_air*delta;
  core_drop_At = H_iron*l_core;
  residual = mmf_At - core_drop_At - Vm_gap;
  U_exc = 2*Modelica.Constants.pi*f*N_exc*Phi_core;
  U_meas = -2*Modelica.Constants.pi*f*N_meas*Phi_gap;
  useful_to_core_flux_ratio = Phi_gap/Phi_core;

  annotation(
    experiment(StartTime=0.0, StopTime=1.0, Tolerance=0.005, Interval=0.001),
    Diagram(graphics={Text(extent={{-200,170},{200,150}}, textString="Quasi-static magnetic circuit benchmark: series core, parallel gap/leakage branch")})
  );
end QuasiStaticMagneticCircuitBenchmarkSystem;
