model MagneticCorePath
  parameter Modelica.Units.SI.Length a_m = 0.025;
  parameter Modelica.Units.SI.Length l_m = 0.150;
  parameter Modelica.Units.SI.Length delta_m = 0.00150;
  parameter Real mu_r = 1200;
  parameter Real sigma = 0.08;
  parameter Modelica.Units.SI.Permeability mu0_H_per_m = 1.2566370614359173e-6;

  parameter Modelica.Units.SI.Area A_m2 = a_m*a_m;
  parameter Modelica.Units.SI.Length l_left_m = l_m - a_m;
  parameter Modelica.Units.SI.Length l_upper_m = l_m - a_m;
  parameter Modelica.Units.SI.Length l_lower_m = l_m - a_m;
  parameter Modelica.Units.SI.Length l_right_m = l_m - a_m - delta_m;
  parameter Modelica.Units.SI.Length l_core_m = 3*(l_m - a_m) + (l_m - a_m - delta_m);

  Modelica.Blocks.Interfaces.RealInput mmf_At
    annotation (Placement(transformation(extent={{-120,-20},{-100,20}}), iconTransformation(extent={{-120,-20},{-100,20}})));

  Modelica.Blocks.Interfaces.RealOutput Phi_core_Wb
    annotation (Placement(transformation(extent={{100,70},{120,90}}), iconTransformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_gap_Wb
    annotation (Placement(transformation(extent={{100,40},{120,60}}), iconTransformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_leak_Wb
    annotation (Placement(transformation(extent={{100,10},{120,30}}), iconTransformation(extent={{100,10},{120,30}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_gap_over_Phi_core
    annotation (Placement(transformation(extent={{100,-20},{120,0}}), iconTransformation(extent={{100,-20},{120,0}})));
  Modelica.Blocks.Interfaces.RealOutput B_core_T
    annotation (Placement(transformation(extent={{100,-50},{120,-30}}), iconTransformation(extent={{100,-50},{120,-30}})));
  Modelica.Blocks.Interfaces.RealOutput B_gap_T
    annotation (Placement(transformation(extent={{100,-80},{120,-60}}), iconTransformation(extent={{100,-80},{120,-60}})));
  Modelica.Blocks.Interfaces.RealOutput H_core_A_m
    annotation (Placement(transformation(extent={{100,-110},{120,-90}}), iconTransformation(extent={{100,-110},{120,-90}})));
  Modelica.Blocks.Interfaces.RealOutput H_gap_A_m
    annotation (Placement(transformation(extent={{100,-140},{120,-120}}), iconTransformation(extent={{100,-140},{120,-120}})));
  Modelica.Blocks.Interfaces.RealOutput Vm_core_At
    annotation (Placement(transformation(extent={{100,-170},{120,-150}}), iconTransformation(extent={{100,-170},{120,-150}})));
  Modelica.Blocks.Interfaces.RealOutput Vm_gap_At
    annotation (Placement(transformation(extent={{100,-200},{120,-180}}), iconTransformation(extent={{100,-200},{120,-180}})));
  Modelica.Blocks.Interfaces.RealOutput R_core_A_per_Wb
    annotation (Placement(transformation(extent={{100,-230},{120,-210}}), iconTransformation(extent={{100,-230},{120,-210}})));
  Modelica.Blocks.Interfaces.RealOutput R_gap_A_per_Wb
    annotation (Placement(transformation(extent={{100,-260},{120,-240}}), iconTransformation(extent={{100,-260},{120,-240}})));
  Modelica.Blocks.Interfaces.RealOutput R_leak_A_per_Wb
    annotation (Placement(transformation(extent={{100,-290},{120,-270}}), iconTransformation(extent={{100,-290},{120,-270}})));
  Modelica.Blocks.Interfaces.RealOutput R_par_A_per_Wb
    annotation (Placement(transformation(extent={{100,-320},{120,-300}}), iconTransformation(extent={{100,-320},{120,-300}})));
  Modelica.Blocks.Interfaces.RealOutput R_total_A_per_Wb
    annotation (Placement(transformation(extent={{100,-350},{120,-330}}), iconTransformation(extent={{100,-350},{120,-330}})));

equation
  R_core_A_per_Wb = l_core_m/(mu0_H_per_m*mu_r*A_m2);
  R_gap_A_per_Wb = delta_m/(mu0_H_per_m*A_m2);
  R_leak_A_per_Wb = R_gap_A_per_Wb*(1 - sigma)/sigma;
  R_par_A_per_Wb = 1/(1/R_gap_A_per_Wb + 1/R_leak_A_per_Wb);
  R_total_A_per_Wb = R_core_A_per_Wb + R_par_A_per_Wb;

  Phi_core_Wb = mmf_At/R_total_A_per_Wb;
  Phi_gap_Wb = (1 - sigma)*Phi_core_Wb;
  Phi_leak_Wb = sigma*Phi_core_Wb;
  Phi_gap_over_Phi_core = Phi_gap_Wb/max(Phi_core_Wb, 1e-30);
  B_core_T = Phi_core_Wb/A_m2;
  B_gap_T = Phi_gap_Wb/A_m2;
  H_core_A_m = B_core_T/(mu0_H_per_m*mu_r);
  H_gap_A_m = B_gap_T/mu0_H_per_m;
  Vm_core_At = H_core_A_m*l_core_m;
  Vm_gap_At = H_gap_A_m*delta_m;

  assert(sigma > 0 and sigma < 1, "sigma must remain between 0 and 1 for released benchmark branch split");
  assert(mu_r > 0, "mu_r must be positive");
  assert(A_m2 > 0, "cross-sectional area must be positive");
  assert(delta_m > 0, "air-gap length must be positive");
  assert(Phi_gap_Wb >= 0, "useful flux magnitude became negative");
  assert(Phi_leak_Wb >= 0, "leakage flux magnitude became negative");

  annotation (
    Icon(graphics={
      Rectangle(extent={{-100,60},{-40,-60}}, lineColor={0,0,255}, fillColor={230,230,230}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{-40,20},{40,60}}, lineColor={0,0,255}, fillColor={230,230,230}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{-40,-60},{40,-20}}, lineColor={0,0,255}, fillColor={230,230,230}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{40,20},{100,60}}, lineColor={0,0,255}, fillColor={230,230,230}, fillPattern=FillPattern.Solid),
      Rectangle(extent={{40,-60},{100,-20}}, lineColor={0,0,255}, fillColor={255,255,255}, fillPattern=FillPattern.Solid),
      Line(points={{70,20},{70,-20}}, color={0,0,255}),
      Line(points={{55,-20},{85,-20}}, color={0,0,255}),
      Text(extent={{-100,90},{100,120}}, textString="%name"),
      Text(extent={{-96,-88},{98,-116}}, textString="CORE/GAP/LEAK")}),
    Diagram(graphics={Text(extent={{-96,90},{94,74}}, textString="Analytic reluctance network: CORE-L -> CORE-U -> CORE-R -> (GAP-1 || LEAK-1) -> CORE-D")})
  );
end MagneticCorePath;
