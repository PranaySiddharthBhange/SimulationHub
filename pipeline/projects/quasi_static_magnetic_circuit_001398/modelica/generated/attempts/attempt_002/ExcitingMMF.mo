model ExcitingMMF
  extends Modelica.Blocks.Icons.Block;
  parameter Integer N_exc = 600;
  Modelica.Blocks.Interfaces.RealInput I_rms_A annotation(Placement(transformation(extent={{-120,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput mmf_At annotation(Placement(transformation(extent={{100,-10},{120,10}})));
equation
  mmf_At = N_exc*I_rms_A;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,127}),Text(extent={{-90,20},{90,60}}, textString="N*I"),Text(extent={{-100,-20},{100,20}}, textString="MMF"),Text(extent={{-100,100},{100,140}}, textString="%name")}));
end ExcitingMMF;
