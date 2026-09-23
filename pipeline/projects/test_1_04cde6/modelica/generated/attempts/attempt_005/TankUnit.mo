model TankUnit
  Modelica.Blocks.Interfaces.RealInput inflow annotation(Placement(transformation(extent={{-120,30},{-100,50}}), iconTransformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput outflowDemand annotation(Placement(transformation(extent={{-120,-50},{-100,-30}}), iconTransformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,30},{120,50}}), iconTransformation(extent={{100,30},{120,50}})));
  parameter Modelica.Units.SI.Volume level_start = 0;
  parameter Modelica.Units.SI.Volume capacity = 1;
protected
  Modelica.Units.SI.Volume storedVolume(start=level_start, fixed=true);
equation
  der(storedVolume) = (if storedVolume >= capacity and inflow > min(outflowDemand, storedVolume) then min(outflowDemand, storedVolume) else inflow) - (if storedVolume <= 0 then 0 else min(outflowDemand, storedVolume));
  level = storedVolume;
  annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={Rectangle(extent={{-60,-80},{60,80}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid), Rectangle(extent={{-58,-80},{58,0}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name"), Text(extent={{-50,-10},{50,20}}, textString="level")}), Diagram(coordinateSystem(extent={{-100,-100},{100,100}})));
end TankUnit;
