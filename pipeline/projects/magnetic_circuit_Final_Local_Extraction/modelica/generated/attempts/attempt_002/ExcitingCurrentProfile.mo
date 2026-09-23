model ExcitingCurrentProfile
  Modelica.Blocks.Interfaces.RealOutput I_rms_A annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  I_rms_A = if time < 0.10 then 0 else if time <= 0.50 then 2.0*(time - 0.10)/0.40 else 2.0;
  annotation(
    Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),Line(points={{-80,-60},{-20,-60},{20,40},{80,40}}, color={0,0,255}, thickness=1),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-90,-90},{90,-70}}, textString="I_rms(t)")}),
    Diagram(graphics={Text(extent={{-100,80},{100,40}}, textString="0 A before 0.10 s; ramp to 2 A at 0.50 s; hold to 1.0 s")})
  );
end ExcitingCurrentProfile;
