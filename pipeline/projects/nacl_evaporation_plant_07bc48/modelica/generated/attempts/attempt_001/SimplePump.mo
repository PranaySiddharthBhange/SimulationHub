model SimplePump
  parameter Modelica.Units.SI.MassFlowRate nominalFlow = 0.30;
  Modelica.Blocks.Interfaces.BooleanInput cmdOn annotation(Placement(transformation(extent={{-120,20},{-100,40}})));
  Modelica.Blocks.Interfaces.RealInput sourceLevel_m annotation(Placement(transformation(extent={{-120,-20},{-100,0}})));
  Modelica.Blocks.Interfaces.RealOutput flow_kg_s annotation(Placement(transformation(extent={{100,20},{120,40}})));
  Modelica.Blocks.Interfaces.BooleanOutput lowPressureAlarm annotation(Placement(transformation(extent={{100,-20},{120,0}})));
equation
  flow_kg_s = if cmdOn and sourceLevel_m > 0.02 then nominalFlow else 0;
  lowPressureAlarm = false;
  annotation(
    Icon(graphics={Ellipse(extent={{-60,-60},{60,60}}, lineColor={0,0,255}, fillColor={200,200,255}, fillPattern=FillPattern.Solid),Polygon(points={{-80,0},{-20,30},{-20,-30},{-80,0}}, lineColor={0,0,255}, fillColor={0,0,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name")})
  );
end SimplePump;
