model OccupancySchedule
  Modelica.Blocks.Interfaces.RealOutput occupants_person annotation(Placement(transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},{120,10}})));
equation
  occupants_person = if time < 25200 then 0 else if time < 28800 then 2 else if time < 36000 then 8 else if time < 43200 then 12 else if time < 46800 then 4 else if time < 54000 then 15 else if time < 61200 then 10 else if time < 64800 then 3 else 0;
  annotation(Icon(graphics={Rectangle(extent={{-100,-100},{100,100}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid), Text(extent={{-100,100},{100,140}}, textString="%name"), Text(extent={{-80,20},{80,-20}}, textString="OCC")}), Diagram(coordinateSystem(extent={{-100,-100},{100,100}})));
end OccupancySchedule;
