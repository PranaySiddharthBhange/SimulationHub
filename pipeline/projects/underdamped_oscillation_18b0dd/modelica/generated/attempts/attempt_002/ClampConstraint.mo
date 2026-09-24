model ClampConstraint
  parameter Modelica.Units.SI.Position heldPosition = 0.10;
  Modelica.Mechanics.Translational.Interfaces.Flange_b flange
    annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Interfaces.BooleanInput engaged
    annotation(Placement(transformation(extent={{-120,-10},{-100,10}}), iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput clamp_engaged
    annotation(Placement(transformation(extent={{100,40},{120,60}}), iconTransformation(extent={{100,40},{120,60}})));
  Modelica.Mechanics.Translational.Sources.Position positionSource(exact=true)
    annotation(Placement(transformation(extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.BooleanToReal engagedToReal(realTrue=1.0, realFalse=0.0)
    annotation(Placement(transformation(extent={{40,40},{60,60}})));
  Modelica.Blocks.Sources.RealExpression xClamp(y=if engaged then heldPosition else flange.s)
    annotation(Placement(transformation(extent={{-60,-10},{-40,10}})));
equation
  connect(xClamp.y, positionSource.s_ref)
    annotation(Line(points={{-39,0},{-12,0}}, color={0,0,127}));
  connect(positionSource.flange, flange)
    annotation(Line(points={{10,0},{110,0}}, color={0,127,255}));
  connect(engaged, engagedToReal.u)
    annotation(Line(points={{-110,0},{20,0},{20,50},{38,50}}, color={255,0,255}));
  connect(engagedToReal.y, clamp_engaged)
    annotation(Line(points={{61,50},{110,50}}, color={0,0,127}));
annotation(
  Icon(graphics={
    Rectangle(extent={{-100,-60},{100,60}}, lineColor={0,0,0}, fillColor={230,230,230}, fillPattern=FillPattern.Solid),
    Line(points={{-80,0},{20,0}}, color={0,0,0}, thickness=1),
    Polygon(points={{20,20},{60,0},{20,-20},{20,20}}, lineColor={0,0,0}, fillColor={180,180,180}, fillPattern=FillPattern.Solid),
    Text(extent={{-100,70},{100,100}}, textString="%name"),
    Text(extent={{-90,-100},{90,-70}}, textString="Clamp")
  }));
end ClampConstraint;
