model ExcitationCoil
  parameter Integer N = 500 "Turns nominal";
  Modelica.Blocks.Interfaces.RealInput current_A annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput mmf_At annotation(Placement(transformation(extent={{100,-10},{120,10}})));
 equation
  mmf_At = N*current_A;
 annotation(
  Icon(graphics={
    Rectangle(extent={{-80,-50},{80,50}}, lineColor={0,0,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-70,-10},{70,20}}, textString="N=%N")}),
  Diagram(graphics={Rectangle(extent={{-80,-50},{80,50}}, lineColor={0,0,255})}));
end ExcitationCoil;
