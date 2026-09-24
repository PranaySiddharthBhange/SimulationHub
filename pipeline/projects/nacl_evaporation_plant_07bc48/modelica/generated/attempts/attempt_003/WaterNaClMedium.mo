within ;
package WaterNaClMedium
  extends Modelica.Icons.Package;
  constant Integer nXi = 1;
  constant Integer NaCl = 1;
  constant Modelica.Units.SI.Density rho_default = 1000;
  constant Modelica.Units.SI.SpecificHeatCapacity cp_default = 4180;
  constant Modelica.Units.SI.Temperature T_default = 293.15;
  constant Modelica.Units.SI.DynamicViscosity eta_default = 1e-3;

  function rho_Tpw
    input Modelica.Units.SI.Temperature T;
    input Modelica.Units.SI.Pressure p;
    input Real w(unit="kg/kg");
    output Modelica.Units.SI.Density rho;
  algorithm
    rho := rho_default;
  end rho_Tpw;

  function cp_Tw
    input Modelica.Units.SI.Temperature T;
    input Real w(unit="kg/kg");
    output Modelica.Units.SI.SpecificHeatCapacity cp;
  algorithm
    cp := cp_default;
  end cp_Tw;

  function h_Tpw
    input Modelica.Units.SI.Temperature T;
    input Modelica.Units.SI.Pressure p;
    input Real w(unit="kg/kg");
    output Modelica.Units.SI.SpecificEnthalpy h;
  algorithm
    h := cp_default*(T - 273.15);
  end h_Tpw;

  function p_sat_Tw
    input Modelica.Units.SI.Temperature T;
    input Real w(unit="kg/kg");
    output Modelica.Units.SI.Pressure p_sat;
  algorithm
    p_sat := 2339;
  end p_sat_Tw;

  function eta_Tw
    input Modelica.Units.SI.Temperature T;
    input Real w(unit="kg/kg");
    output Modelica.Units.SI.DynamicViscosity eta;
  algorithm
    eta := exp(-6.83241e-07*T^3 + 0.000765676*T^2 - 0.297018665*T - 0.299730079 + 2.065267182*w + 1.546491257*w^2 + 31.57571595*w^3);
  end eta_Tw;

  annotation(Icon(graphics={
    Rectangle(extent={{-90,-70},{90,70}}, lineColor={0,0,255}, fillColor={230,230,255}, fillPattern=FillPattern.Solid),
    Rectangle(extent={{-84,-70},{84,-10}}, lineColor={0,127,255}, fillColor={0,127,255}, fillPattern=FillPattern.Solid),
    Line(points={{-90,0},{90,0}}, color={0,0,255}),
    Text(extent={{-100,80},{100,120}}, textString="%name"),
    Text(extent={{-80,20},{80,-20}}, textString="Water\nNaCl")
  }));
end WaterNaClMedium;
