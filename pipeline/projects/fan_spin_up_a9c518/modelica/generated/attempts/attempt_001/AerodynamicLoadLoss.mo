model AerodynamicLoadLoss
  parameter Real k_fan(unit="N.m.s2/rad2") = 0.0004 "aerodynamic load coefficient from 01_fan_nonideal_spinup.txt";

  Modelica.Blocks.Interfaces.RealInput omega(unit="rad/s")
    annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput torqueLoss(unit="N.m")
    annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  torqueLoss = k_fan*omega*omega;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,-80},{100,80}}, lineColor={0,90,180}, fillColor={200,235,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-90,10},{90,50}}, textString="Aero"),
      Text(extent={{-90,-30},{90,10}}, textString="Ta=k*w^2"),
      Text(extent={{-100,100},{100,140}}, textString="%name")}));
end AerodynamicLoadLoss;
