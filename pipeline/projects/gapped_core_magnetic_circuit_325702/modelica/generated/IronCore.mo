model IronCore
  parameter Modelica.Units.SI.Length mean_path_length_m = 0.4 "Core mean path length";
  parameter Modelica.Units.SI.Area cross_section_m2 = 0.0004 "Cross-section";
  parameter Real relative_permeability_nominal = 2000.0 "Relative permeability nominal";
  Modelica.Blocks.Interfaces.RealInput Phi_Wb annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput B_core_T annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput Vm_core_At annotation(Placement(transformation(extent={{100,-70},{120,-50}})));
protected 
  constant Real mu0 = Modelica.Constants.mu_0;
  final parameter Real R_core = mean_path_length_m/(mu0*relative_permeability_nominal*cross_section_m2);
equation
  B_core_T = Phi_Wb/cross_section_m2;
  Vm_core_At = Phi_Wb*R_core;
  assert(cross_section_m2 > 0, "cross_section_m2 must be positive");
  assert(relative_permeability_nominal > 0, "relative_permeability_nominal must be positive");
 annotation(
  Icon(graphics={
    Rectangle(extent={{-80,-60},{80,60}}, lineColor={95,95,95}, fillColor={215,215,215}, fillPattern=FillPattern.Solid),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-70,-10},{70,20}}, textString="iron core")}),
  Diagram(graphics={
    Rectangle(extent={{-80,-60},{80,60}}, lineColor={95,95,95}, fillColor={215,215,215}, fillPattern=FillPattern.Solid)}));
end IronCore;
