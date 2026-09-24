model SimpleVessel
  parameter Modelica.Units.SI.Area area=1;
  parameter Modelica.Units.SI.Height level_start=0;
  Modelica.Blocks.Interfaces.RealInput qIn annotation(Placement(transformation(extent={{-120,30},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput qOut annotation(Placement(transformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput level annotation(Placement(transformation(extent={{100,-10},{120,10}})));
protected 
  Modelica.Units.SI.Height h(start=level_start);
equation 
  der(h) = (qIn-qOut)/area;
  level = h;
end SimpleVessel;