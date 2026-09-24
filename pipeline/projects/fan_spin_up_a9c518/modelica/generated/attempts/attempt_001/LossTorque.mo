model LossTorque
  parameter Modelica.Units.SI.RotationalDampingConstant b = 0.01;
  parameter Real k_fan(unit="N.m.s2/rad2") = 0.0004;
  Modelica.Mechanics.Rotational.Interfaces.Flange_b shaft
    annotation(Placement(transformation(extent={{90,-10},{110,10}})));
  Modelica.Blocks.Interfaces.RealOutput loss_torque_Nm
    annotation(Placement(transformation(extent={{100,50},{120,70}})));
protected 
  Modelica.Units.SI.AngularVelocity w;
  Modelica.Units.SI.Torque tau;
equation
  w = der(shaft.phi);
  tau = b*w + k_fan*w*abs(w);
  shaft.tau = tau;
  loss_torque_Nm = tau;
  annotation(
    Icon(graphics={
      Polygon(points={{-60,0},{0,40},{0,-40},{-60,0}}, lineColor={0,0,0}, fillColor={255,170,170}, fillPattern=FillPattern.Solid),
      Polygon(points={{60,0},{0,40},{0,-40},{60,0}}, lineColor={0,0,0}, fillColor={255,170,170}, fillPattern=FillPattern.Solid),
      Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={}));
end LossTorque;
