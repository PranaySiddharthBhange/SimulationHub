model RM201Room
  parameter Modelica.Units.SI.Volume V = 100 "Room volume";
  parameter Real rho(unit="kg/m3") = 1.2 "Nominal air density";
  parameter Real C_out(unit="kg/kg") = 4.557e-4 "Outdoor CO2 mass fraction";
  parameter Real C_start(unit="kg/kg") = 4.557e-4 "Initial room CO2 mass fraction";
  Modelica.Blocks.Interfaces.RealInput physical_supply_m_flow_kg_s annotation(Placement(transformation(extent={{-120,50},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput actual_co2_generation_kg_s annotation(Placement(transformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput room_co2_mass_fraction_kgkg annotation(Placement(transformation(extent={{100,-10},{120,10}})));
protected 
  parameter Real m_air(unit="kg") = V*rho;
  Real mCO2(unit="kg", start=m_air*C_start, fixed=true);
equation 
  der(mCO2) = physical_supply_m_flow_kg_s*C_out + actual_co2_generation_kg_s - physical_supply_m_flow_kg_s*room_co2_mass_fraction_kgkg;
  room_co2_mass_fraction_kgkg = mCO2/m_air;
  assert(room_co2_mass_fraction_kgkg >= 0, "room CO2 mass fraction below zero");
  annotation(
    Icon(graphics={Rectangle(extent={{-80,-80},{80,80}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),Text(extent={{-100,100},{100,140}}, textString="%name"),Text(extent={{-70,-10},{70,30}}, textString="RM")}),
    Diagram(graphics={Rectangle(extent={{-80,-80},{80,80}}, lineColor={0,0,255})}));
end RM201Room;
