model CurrentRamp
  extends Modelica.Blocks.Icons.Block;
  parameter Modelica.Units.SI.Current I_final = 2.0;
  parameter Modelica.Units.SI.Time rampStart = 0.10;
  parameter Modelica.Units.SI.Time rampEnd = 0.50;
  Modelica.Blocks.Interfaces.RealOutput I_rms_A annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  I_rms_A = if time < rampStart then 0 else if time < rampEnd then I_final*(time - rampStart)/(rampEnd - rampStart) else I_final;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,127}),Text(extent={{-100,30},{100,70}}, textString="I_rms"),Text(extent={{-100,-20},{100,20}}, textString="ramp"),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end CurrentRamp;
