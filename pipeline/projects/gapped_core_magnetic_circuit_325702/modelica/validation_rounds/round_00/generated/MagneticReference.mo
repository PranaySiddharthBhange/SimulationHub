model MagneticReference
  Modelica.Blocks.Interfaces.RealInput Phi_Wb annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealOutput Phi_out_Wb annotation(Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.RealOutput reference_At annotation(Placement(transformation(extent={{100,-60},{120,-40}})));
equation
  Phi_out_Wb = Phi_Wb;
  reference_At = 0;
 annotation(
  Icon(graphics={
    Ellipse(extent={{-70,-70},{70,70}}, lineColor={0,0,0}),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-50,-10},{50,20}}, textString="ref")}),
  Diagram(graphics={Ellipse(extent={{-70,-70},{70,70}}, lineColor={0,0,0})}));
end MagneticReference;
