model BearingFrictionLoss
  parameter Real b(unit="N.m.s/rad") = 0.01 "bearing friction coefficient from 01_fan_nonideal_spinup.txt";

  Modelica.Blocks.Interfaces.RealInput omega(unit="rad/s")
    annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput torqueLoss(unit="N.m")
    annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  torqueLoss = b*omega;
  annotation(
    Icon(graphics={
      Rectangle(extent={{-100,-80},{100,80}}, lineColor={120,60,0}, fillColor={255,230,170}, fillPattern=FillPattern.Solid),
      Text(extent={{-90,10},{90,50}}, textString="Bearing"),
      Text(extent={{-90,-30},{90,10}}, textString="Tb=b*omega"),
      Text(extent={{-100,100},{100,140}}, textString="%name")}));
end BearingFrictionLoss;
