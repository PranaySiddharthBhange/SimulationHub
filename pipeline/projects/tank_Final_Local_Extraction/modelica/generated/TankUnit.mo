model TankUnit
  import Modelica.Units.SI;
  parameter SI.Area crossArea;
  parameter SI.Height level_start;
  parameter SI.Height levelMin = 0;
  Modelica.Blocks.Interfaces.RealInput inflow annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput outflowCmd annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput levelOut annotation(Placement(transformation(extent={{100,-10},{120,10}})));
  SI.Height level(start=level_start, fixed=true);
  SI.VolumeFlowRate qOut;
equation
  qOut = if level <= levelMin and outflowCmd > inflow then inflow else outflowCmd;
  der(level) = (inflow - qOut)/crossArea;
  levelOut = level;
  annotation(
    Icon(graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}), Rectangle(extent={{-56,-80},{56,0}}, fillColor={85,170,255}, fillPattern=FillPattern.Solid, lineColor={85,170,255}), Text(extent={{-100,100},{100,140}}, textString="%name")}),
    Diagram(graphics={Text(extent={{-90,86},{90,60}}, textString="Tank")})
  );
end TankUnit;
