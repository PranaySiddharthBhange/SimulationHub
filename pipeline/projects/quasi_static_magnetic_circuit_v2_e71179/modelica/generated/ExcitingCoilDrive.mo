model ExcitingCoilDrive
  parameter Integer N_exc = 600;

  Modelica.Blocks.Interfaces.RealInput I_rms_A
    annotation (Placement(transformation(extent={{-120,-20},{-100,20}}), iconTransformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput mmf_At
    annotation (Placement(transformation(extent={{100,30},{120,50}}), iconTransformation(extent={{100,30},{120,50}})));

equation
  mmf_At = N_exc*I_rms_A;

  annotation (
    Icon(graphics={
      Rectangle(extent={{-60,60},{60,-60}}, lineColor={0,0,255}, fillColor={255,255,200}, fillPattern=FillPattern.Solid),
      Ellipse(extent={{-40,40},{-10,10}}, lineColor={0,0,255}),
      Ellipse(extent={{-5,40},{25,10}}, lineColor={0,0,255}),
      Ellipse(extent={{30,40},{60,10}}, lineColor={0,0,255}),
      Ellipse(extent={{-40,-10},{-10,-40}}, lineColor={0,0,255}),
      Ellipse(extent={{-5,-10},{25,-40}}, lineColor={0,0,255}),
      Ellipse(extent={{30,-10},{60,-40}}, lineColor={0,0,255}),
      Text(extent={{-100,90},{100,120}}, textString="%name"),
      Text(extent={{-80,-84},{80,-112}}, textString="ExcitingCoil")}),
    Diagram(graphics={Text(extent={{-94,82},{92,64}}, textString="mmf_At = N_exc * I_rms_A")})
  );
end ExcitingCoilDrive;
