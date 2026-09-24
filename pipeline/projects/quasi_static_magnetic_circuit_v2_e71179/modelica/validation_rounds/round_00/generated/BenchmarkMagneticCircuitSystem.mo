model BenchmarkMagneticCircuitSystem
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.Length a_m = 0.025;
  parameter Modelica.Units.SI.Length l_m = 0.150;
  parameter Modelica.Units.SI.Length delta_m = 0.00150;
  parameter Real mu_r = 1200;
  parameter Real sigma(min=0, max=1) = 0.08;
  parameter Integer N_exc = 600;
  parameter Integer N_meas = 50;
  parameter Modelica.Units.SI.Frequency f_Hz = 50;
  parameter Modelica.Units.SI.Permeability mu0_H_per_m = Modelica.Constants.mu_0;
  parameter Modelica.Units.SI.Area A_m2 = a_m*a_m;
  parameter Modelica.Units.SI.Length l_core_m = 3*(l_m - a_m) + (l_m - a_m - delta_m);
  parameter Modelica.Units.SI.Reluctance R_coreL_A_per_Wb = (l_m - a_m)/(mu0_H_per_m*mu_r*A_m2);
  parameter Modelica.Units.SI.Reluctance R_coreU_A_per_Wb = (l_m - a_m)/(mu0_H_per_m*mu_r*A_m2);
  parameter Modelica.Units.SI.Reluctance R_coreR_A_per_Wb = (l_m - a_m - delta_m)/(mu0_H_per_m*mu_r*A_m2);
  parameter Modelica.Units.SI.Reluctance R_coreD_A_per_Wb = (l_m - a_m)/(mu0_H_per_m*mu_r*A_m2);
  parameter Modelica.Units.SI.Reluctance R_core_A_per_Wb = l_core_m/(mu0_H_per_m*mu_r*A_m2);
  parameter Modelica.Units.SI.Reluctance R_gap_A_per_Wb = delta_m/(mu0_H_per_m*A_m2);
  parameter Modelica.Units.SI.Reluctance R_leak_A_per_Wb = R_gap_A_per_Wb*(1 - sigma)/sigma;
  parameter Modelica.Units.SI.Reluctance R_par_A_per_Wb = 1/(1/R_gap_A_per_Wb + 1/R_leak_A_per_Wb);
  parameter Modelica.Units.SI.Reluctance R_total_A_per_Wb = R_core_A_per_Wb + R_par_A_per_Wb;

  CurrentRamp currentRamp(offset=0, height=2.0, startTime=0.10, duration=0.40) annotation(Placement(transformation(extent={{-180,60},{-140,100}})));
  Modelica.Electrical.Analog.Sources.SignalCurrent excitingCurrent annotation(Placement(transformation(extent={{-130,20},{-110,40}})));
  Modelica.Electrical.Analog.Basic.Ground electricGround annotation(Placement(transformation(extent={{-140,-20},{-120,0}})));
  Modelica.Magnetic.FluxTubes.Basic.ElectroMagneticConverter excitingCoil(N=N_exc) annotation(Placement(transformation(extent={{-70,10},{-30,50}})));
  Modelica.Magnetic.FluxTubes.Basic.Ground magneticGround annotation(Placement(transformation(extent={{160,-120},{180,-100}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance coreL(R_m=R_coreL_A_per_Wb) annotation(Placement(transformation(extent={{-10,10},{20,40}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance coreU(R_m=R_coreU_A_per_Wb) annotation(Placement(transformation(extent={{40,10},{70,40}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance coreR(R_m=R_coreR_A_per_Wb) annotation(Placement(transformation(extent={{90,10},{120,40}})));
  Modelica.Magnetic.FluxTubes.Sensors.MagneticFluxSensor fluxSensor annotation(Placement(transformation(extent={{90,-40},{120,-10}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance gap1(R_m=R_gap_A_per_Wb) annotation(Placement(transformation(extent={{140,-40},{170,-10}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance leak1(R_m=R_leak_A_per_Wb) annotation(Placement(transformation(extent={{140,-90},{170,-60}})));
  Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance coreD(R_m=R_coreD_A_per_Wb) annotation(Placement(transformation(extent={{190,10},{220,40}})));
  Modelica.Magnetic.FluxTubes.Basic.ElectroMagneticConverter measuringCoil(N=N_meas) annotation(Placement(transformation(extent={{140,-140},{180,-100}})));
  Modelica.Electrical.Analog.Basic.Ground measuringElectricGround annotation(Placement(transformation(extent={{80,-180},{100,-160}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor excitingVoltageSensor annotation(Placement(transformation(extent={{-20,70},{0,90}})));
  Modelica.Electrical.Analog.Sensors.VoltageSensor measuringVoltageSensor annotation(Placement(transformation(extent={{80,-140},{100,-120}})));

  Modelica.Units.SI.Time time_s;
  Modelica.Units.SI.Current I_rms_A;
  Real mmf_At(unit="A.Turn");
  Modelica.Units.SI.MagneticFlux Phi_core_Wb;
  Modelica.Units.SI.MagneticFlux Phi_gap_Wb;
  Modelica.Units.SI.MagneticFlux Phi_leak_Wb;
  Real Phi_gap_over_Phi_core;
  Modelica.Units.SI.MagneticFluxDensity B_core_T;
  Modelica.Units.SI.MagneticFluxDensity B_gap_T;
  Modelica.Units.SI.MagneticFieldStrength H_core_A_m;
  Modelica.Units.SI.MagneticFieldStrength H_gap_A_m;
  Real Vm_core_At(unit="A.Turn");
  Real Vm_gap_At(unit="A.Turn");
  Modelica.Units.SI.Voltage U_exc_induced_V_rms;
  Modelica.Units.SI.Voltage U_meas_induced_signed_V_rms;
equation
  connect(currentRamp.y, excitingCurrent.i) annotation(Line(points={{-139,80},{-136,80},{-136,30},{-130,30}}, color={0,0,127}));
  connect(excitingCurrent.n, electricGround.p) annotation(Line(points={{-120,20},{-120,0},{-130,0}}, color={0,127,255}));
  connect(excitingCurrent.p, excitingCoil.p) annotation(Line(points={{-110,30},{-70,30}}, color={0,127,255}));
  connect(excitingCoil.n, electricGround.p) annotation(Line(points={{-70,18},{-90,18},{-90,0},{-130,0}}, color={0,127,255}));
  connect(excitingCoil.port_p, coreL.port_p) annotation(Line(points={{-34,50},{-34,60},{-20,60},{-20,25},{-10,25}}, color={0,127,255}));
  connect(coreL.port_n, coreU.port_p) annotation(Line(points={{20,25},{40,25}}, color={0,127,255}));
  connect(coreU.port_n, coreR.port_p) annotation(Line(points={{70,25},{90,25}}, color={0,127,255}));
  connect(coreR.port_n, fluxSensor.port_p) annotation(Line(points={{120,25},{130,25},{130,-25},{90,-25}}, color={0,127,255}));
  connect(fluxSensor.port_n, gap1.port_p) annotation(Line(points={{120,-25},{140,-25}}, color={0,127,255}));
  connect(coreR.port_n, leak1.port_p) annotation(Line(points={{120,25},{130,25},{130,-75},{140,-75}}, color={0,127,255}));
  connect(gap1.port_n, coreD.port_p) annotation(Line(points={{170,-25},{180,-25},{180,25},{190,25}}, color={0,127,255}));
  connect(leak1.port_n, coreD.port_p) annotation(Line(points={{170,-75},{180,-75},{180,25},{190,25}}, color={0,127,255}));
  connect(coreD.port_n, magneticGround.port) annotation(Line(points={{220,25},{230,25},{230,-110},{170,-110}}, color={0,127,255}));
  connect(measuringCoil.port_p, gap1.port_n) annotation(Line(points={{176,-100},{184,-100},{184,-25},{170,-25}}, color={0,127,255}));
  connect(measuringCoil.port_n, gap1.port_p) annotation(Line(points={{176,-140},{132,-140},{132,-25},{140,-25}}, color={0,127,255}));
  connect(measuringCoil.n, measuringElectricGround.p) annotation(Line(points={{140,-132},{120,-132},{120,-160},{90,-160}}, color={0,127,255}));
  connect(measuringCoil.p, measuringVoltageSensor.p) annotation(Line(points={{140,-120},{120,-120},{120,-130},{80,-130}}, color={0,127,255}));
  connect(measuringCoil.n, measuringVoltageSensor.n) annotation(Line(points={{140,-132},{120,-132},{120,-130},{100,-130}}, color={0,127,255}));
  connect(excitingVoltageSensor.p, excitingCoil.p) annotation(Line(points={{-20,80},{-80,80},{-80,30},{-70,30}}, color={0,127,255}));
  connect(excitingVoltageSensor.n, excitingCoil.n) annotation(Line(points={{0,80},{10,80},{10,18},{-70,18}}, color={0,127,255}));

  time_s = time;
  I_rms_A = currentRamp.y;
  mmf_At = N_exc*I_rms_A;
  Phi_gap_Wb = fluxSensor.Phi;
  Phi_core_Wb = Phi_gap_Wb/(1 - sigma);
  Phi_leak_Wb = sigma*Phi_core_Wb;
  Phi_gap_over_Phi_core = if abs(Phi_core_Wb) > Modelica.Constants.eps then Phi_gap_Wb/Phi_core_Wb else 1 - sigma;
  B_core_T = Phi_core_Wb/A_m2;
  B_gap_T = Phi_gap_Wb/A_m2;
  H_core_A_m = B_core_T/(mu0_H_per_m*mu_r);
  H_gap_A_m = B_gap_T/mu0_H_per_m;
  Vm_core_At = R_core_A_per_Wb*Phi_core_Wb;
  Vm_gap_At = R_gap_A_per_Wb*Phi_gap_Wb;
  U_exc_induced_V_rms = abs(excitingVoltageSensor.v);
  U_meas_induced_signed_V_rms = -abs(measuringVoltageSensor.v);

  annotation(
    Diagram(coordinateSystem(extent={{-200,-200},{260,120}})),
    experiment(StartTime=0, StopTime=1.0, Tolerance=1e-6, Interval=0.001));
end BenchmarkMagneticCircuitSystem;
