within ;
model PumpActuator
  import Modelica.Units.SI;
  parameter SI.MassFlowRate m_flow_nominal = 0.30;
  parameter SI.Density rho_nominal = 1000;
  parameter SI.VolumeFlowRate qNominal = m_flow_nominal/rho_nominal;
  Modelica.Blocks.Interfaces.BooleanInput onCmd annotation(Placement(transformation(extent={{-120,-20},{-100,0}}), iconTransformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealOutput qOut annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
equation
  qOut = if onCmd then qNominal else 0;
  annotation(
    Icon(graphics={Ellipse(extent={{-60,-60},{60,60}}, lineColor={0,0,255}),Polygon(points={{-20,-20},{30,0},{-20,20},{-20,-20}}, lineColor={0,0,255}, fillColor={0,0,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end PumpActuator;
