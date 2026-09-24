model FlowSource
  parameter Modelica.Units.SI.MassFlowRate m_flow = 0;
  parameter Real w_NaCl = 0;
  parameter Modelica.Units.SI.Temperature T_K = 293.15;
  Modelica.Blocks.Interfaces.RealOutput m_flow_out annotation(Placement(transformation(extent={{100,50},{120,70}})));
  Modelica.Blocks.Interfaces.RealOutput w_out annotation(Placement(transformation(extent={{100,0},{120,20}})));
  Modelica.Blocks.Interfaces.RealOutput T_out annotation(Placement(transformation(extent={{100,-50},{120,-30}})));
equation
  m_flow_out = m_flow;
  w_out = w_NaCl;
  T_out = T_K;
  annotation(
    Icon(graphics={
      Ellipse(extent={{-80,-80},{80,80}}, lineColor={0,127,255}, fillColor={215,235,255}, fillPattern=FillPattern.Solid),
      Text(extent={{-50,20},{50,60}}, textString="src"),
      Text(extent={{-100,100},{100,140}}, textString="%name")
    })
  );
end FlowSource;
