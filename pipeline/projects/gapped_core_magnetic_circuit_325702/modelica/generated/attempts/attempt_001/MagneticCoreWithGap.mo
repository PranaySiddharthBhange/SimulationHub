model MagneticCoreWithGap
  parameter Integer N = 500;
  parameter Modelica.Units.SI.Length l_core = 0.4 "Core mean path length";
  parameter Modelica.Units.SI.Area A = 0.0004 "Cross-section";
  parameter Real mu_r = 2000 "Relative permeability nominal";
  parameter Modelica.Units.SI.Length l_gap = 0.002 "Air gap length";
  final parameter Real mu0 = Modelica.Constants.mu_0;
  final parameter Real R_core = l_core/(mu0*mu_r*A);
  final parameter Real R_gap = l_gap/(mu0*A);
  Modelica.Blocks.Interfaces.RealInput current_A annotation(Placement(transformation(extent={{-120,60},{-100,80}})));
  Modelica.Blocks.Interfaces.RealInput mmf_At annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_core_Wb annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput B_core_T annotation(Placement(transformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Interfaces.RealOutput B_gap_T annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Interfaces.RealOutput Vm_core_At annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
  Modelica.Blocks.Interfaces.RealOutput Vm_gap_At annotation(Placement(transformation(extent={{100,-90},{120,-70}})));
 equation
  Phi_core_Wb = mmf_At/(R_core + R_gap);
  B_core_T = Phi_core_Wb/A;
  B_gap_T = Phi_core_Wb/A;
  Vm_core_At = Phi_core_Wb*R_core;
  Vm_gap_At = Phi_core_Wb*R_gap;
 annotation(
  Icon(graphics={
    Rectangle(extent={{-90,-60},{-20,60}}, lineColor={95,95,95}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
    Rectangle(extent={{20,-60},{90,60}}, lineColor={95,95,95}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
    Rectangle(extent={{-20,-60},{20,60}}, lineColor={255,255,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-60,-10},{60,20}}, textString="core+gap")}),
  Diagram(graphics={
    Rectangle(extent={{-90,-60},{-20,60}}, lineColor={95,95,95}),
    Rectangle(extent={{20,-60},{90,60}}, lineColor={95,95,95}),
    Rectangle(extent={{-20,-60},{20,60}}, lineColor={0,0,0})}));
end MagneticCoreWithGap;
