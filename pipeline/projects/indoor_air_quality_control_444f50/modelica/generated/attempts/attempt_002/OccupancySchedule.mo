model OccupancySchedule
  Modelica.Blocks.Interfaces.RealOutput occupants_person annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
  parameter Modelica.Units.SI.Time t1 = 25200;
  parameter Modelica.Units.SI.Time t2 = 28800;
  parameter Modelica.Units.SI.Time t3 = 36000;
  parameter Modelica.Units.SI.Time t4 = 43200;
  parameter Modelica.Units.SI.Time t5 = 46800;
  parameter Modelica.Units.SI.Time t6 = 54000;
  parameter Modelica.Units.SI.Time t7 = 61200;
  parameter Modelica.Units.SI.Time t8 = 64800;
equation
  occupants_person = if time < t1 then 0 else if time < t2 then 2 else if time < t3 then 8 else if time < t4 then 12 else if time < t5 then 4 else if time < t6 then 15 else if time < t7 then 10 else if time < t8 then 3 else 0;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}), Text(extent={{-100,100},{100,140}}, textString="%name"), Text(extent={{-90,20},{90,-20}}, textString="OCC")}), Diagram);
end OccupancySchedule;
