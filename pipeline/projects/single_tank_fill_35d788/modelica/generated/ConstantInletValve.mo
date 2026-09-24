model ConstantInletValve
  parameter Modelica.Units.SI.VolumeFlowRate nominalInflow = 0.01 "Constant inflow while valve is open";
  Modelica.Blocks.Interfaces.RealInput supply_flow_m3_s annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.BooleanInput openCmd annotation(Placement(transformation(extent={{-120,40},{-100,80}})));
  Modelica.Blocks.Interfaces.RealOutput outflow_m3_s annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Interfaces.RealOutput valve_open_cmd annotation(Placement(transformation(extent={{100,50},{120,70}})));
annotation(
  Icon(graphics={
    Polygon(points={{-60,20},{-10,0},{-60,-20},{-60,20}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),
    Polygon(points={{60,20},{10,0},{60,-20},{60,20}}, lineColor={0,0,255}, fillColor={200,200,200}, fillPattern=FillPattern.Solid),
    Line(points={{-100,0},{-60,0}}, color={0,127,255}),
    Line(points={{60,0},{100,0}}, color={0,127,255}),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-90,-70},{90,-40}}, textString="Qnom")
  }));
equation
  outflow_m3_s = if openCmd then min(supply_flow_m3_s, nominalInflow) else 0;
  valve_open_cmd = if openCmd then 1.0 else 0.0;
end ConstantInletValve;
