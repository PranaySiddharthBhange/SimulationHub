model IdealOnOffValve
  parameter Modelica.Units.SI.VolumeFlowRate nominalFlow=0.001;
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealOutput flow_m3s annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  flow_m3s = if openCmd then nominalFlow else 0.0;
  annotation(
    Icon(graphics={Polygon(points={{-80,0},{-20,40},{-20,-40},{-80,0}}, lineColor={0,0,0}, fillColor={192,192,192}, fillPattern=FillPattern.Solid),Polygon(points={{80,0},{20,40},{20,-40},{80,0}}, lineColor={0,0,0}, fillColor={192,192,192}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end IdealOnOffValve;
