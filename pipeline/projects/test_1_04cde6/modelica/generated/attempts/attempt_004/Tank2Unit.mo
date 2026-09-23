model Tank2Unit
  parameter Modelica.Units.SI.Area crossArea = 1 "Assumed constant cross-sectional area";
  parameter Modelica.Units.SI.Height levelLow = 0.1 "Assumed low switch threshold";
  parameter Modelica.Units.SI.Height level_start = 0 "Assumed initial Tank 2 level";
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealInput qOutCmd annotation(Placement(transformation(extent={{-120,-60},{-100,-40}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.BooleanOutput lowReached annotation(Placement(transformation(extent={{100,-20},{120,0}})));
protected
  Modelica.Units.SI.Height h(start=level_start, fixed=true);
  Modelica.Units.SI.VolumeFlowRate qOutActual;
equation
  qOutActual = if h <= 0 and qOutCmd > qIn then qIn else qOutCmd;
  der(h) = if h <= 0 and qOutCmd > qIn then qIn/crossArea else (qIn - qOutCmd)/crossArea;
  level = h;
  lowReached = h <= levelLow;
annotation(
  Icon(graphics={
    Rectangle(extent={{-60,-100},{60,80}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),
    Rectangle(extent={{-56,-100},{56,-20}}, lineColor={0,128,255}, fillColor={0,128,255}, fillPattern=FillPattern.Solid),
    Text(extent={{-100,100},{100,140}}, textString="%name"),
    Text(extent={{-70,-10},{70,20}}, textString="T2")}),
  Diagram(graphics={Text(extent={{-94,90},{96,108}}, textString="Tank 2 level balance with low switch output")})
);
end Tank2Unit;
