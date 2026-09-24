model MeasuringCoilOutput
  parameter Integer N_meas = 50;
  parameter Modelica.Units.SI.Frequency f_Hz = 50;

  Modelica.Blocks.Interfaces.RealInput Phi_gap_Wb
    annotation (Placement(transformation(extent={{-120,-20},{-100,20}}), iconTransformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput U_meas_induced_signed_V_rms
    annotation (Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));

equation
  U_meas_induced_signed_V_rms = -2*Modelica.Constants.pi*f_Hz*N_meas*Phi_gap_Wb;

  annotation (
    Icon(graphics={
      Rectangle(extent={{-60,60},{60,-60}}, lineColor={0,0,255}, fillColor={220,255,220}, fillPattern=FillPattern.Solid),
      Ellipse(extent={{-40,40},{-10,10}}, lineColor={0,0,255}),
      Ellipse(extent={{-5,40},{25,10}}, lineColor={0,0,255}),
      Ellipse(extent={{30,40},{60,10}}, lineColor={0,0,255}),
      Ellipse(extent={{-40,-10},{-10,-40}}, lineColor={0,0,255}),
      Ellipse(extent={{-5,-10},{25,-40}}, lineColor={0,0,255}),
      Ellipse(extent={{30,-10},{60,-40}}, lineColor={0,0,255}),
      Text(extent={{-100,90},{100,120}}, textString="%name"),
      Text(extent={{-90,-84},{90,-112}}, textString="MeasuringCoil")}),
    Diagram(graphics={Text(extent={{-92,80},{94,62}}, textString="Signed polarity is negative for positive useful flux")})
  );
end MeasuringCoilOutput;
