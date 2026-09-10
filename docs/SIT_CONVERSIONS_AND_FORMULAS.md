# SIT: Conversions and formulas

Quick guide, SIT 1.4.10.

## System evaluation

CHOOSING METHODS FOR YOUR DATA

A CTD measures electrical conductivity C, temperature T and pressure P. The SD208 calculates salinity S from these measurements using PSS-78. Temperature and pressure are included because both affect how well the water conducts electricity.

Use Convert to choose how SIT calculates results from your measurements. For comparison with earlier SAIV surveys, select the same SIT methods and settings used for those surveys. If your project specifies a method, select that method.

PSS-78 (Practical Salinity Scale 1978) calculates salinity from C, T and P. EOS-80 (Equation of State 1980) calculates density and related seawater properties. TEOS-10 (Thermodynamic Equation of Seawater 2010) includes salt composition and provides a common basis for density, heat-related properties and sound speed.

For work requiring Absolute Salinity and TEOS-10 water properties, select the corresponding GSW choices. GSW is the seawater calculation library used for these options in SIT.

In fjords, fresh surface water and saltier deep water have different densities. A profile-based depth calculation takes account of these layers.

SAIV recommends recording C, T and P. These preserve the measurements needed to calculate salinity and other water properties later. SIT can retain the original columns alongside the calculated results.

## Conversions and formulas

USING CONVERT

Select the file, then follow the Next pages. Each measurement has its own choices and a Quick guide button. Select the required units and calculation methods, review the supporting values, and convert.

Keep original fields selected to retain measurements alongside calculated columns. The export records the selected methods and supplied values, making it possible to repeat a calculation later.

COMMON SYMBOLS

C: conductivity in mS/cm.
T: water temperature in degrees Celsius.
P: water pressure in dbar.
S: Practical Salinity, as shown by the instrument and in your data file.
SA: Absolute Salinity in g/kg.
AP: atmospheric pressure in hPa or mbar.

The measurement topics explain the principle, available methods and a short example.

## Conductivity and salinity

WHAT DOES THE CTD MEASURE?

The CTD measures electrical conductivity: how readily the water conducts electricity. Dissolved salts contribute to this conductivity. The instrument calibrates the conductivity-cell signal and combines it with temperature and pressure to calculate salinity.

The SD208 itself calculates salinity S from measured C, T and P using PSS-78 (Practical Salinity Scale 1978). This is the instrument's salinity value in your file.

S means Practical Salinity. Scientific references also write it as SP, where P stands for Practical. S and SP describe the same quantity here; this guide uses S to match your instrument and data file. Practical Salinity is dimensionless. Absolute Salinity (SA) is a different quantity, expressed in g/kg.

In Convert, you can keep the instrument's S value or calculate salinity again from C, T and P using your selected method. Choosing a method in Convert applies to this calculation in SIT; it does not change the method used by the instrument.

METHOD CHOICES

SIT PSS-78 follows the established SAIV calculation and is useful for comparison with earlier data.

GSW PSS-78 uses the same salinity scale, with the Hill extension below S=2. This extends the calculation to very low salinities.

For TEOS-10, SIT also calculates Absolute Salinity. Reference composition uses standard seawater composition. The geographical choice uses position and atlas information to account for regional composition differences.

EXAMPLE

C=30.000 mS/cm, T=10.000 C and P=100.00 dbar give S=26.82415 with the SIT PSS-78 method.

S=35 corresponds to a Reference Salinity of 35.16504 g/kg. These numbers describe different salinity quantities.

Formula and units: https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html

SAIV recommends recording CTD (C/T/P) rather than STD (S/T/P). Conductivity is then available for later checking and recalculation with the chosen method. With STD, conductivity must be estimated back from the stored salinity; rounding means the exact original conductivity cannot be recovered.

## Temperature

HOW IT IS MEASURED

The CTD measures a temperature-dependent resistance and converts it to Celsius using the instrument's Steinhart-Hart calibration. SIT receives the calculated water temperature.

Use the calibration certificate supplied with your instrument to identify its temperature calibration and scale.

COMPARING TEMPERATURE RECORDS

Temperature calibrations can use a Kelvin-to-Celsius offset of 273.16 or 273.15. This is a difference of 0.01 C for identical resistance and coefficients. The offset belongs with the calibration coefficients. Keep the recorded temperature unless the instrument's calibration procedure specifies a correction.

TEMPERATURE SCALE AND DISPLAY

In Convert, select the temperature scale stated for your measurements. This lets SIT use the appropriate temperature in the selected calculations. Check the instrument documentation if you are unsure. The scale relation is T68=1.00024*T90: 10.000 C on ITS-90 corresponds to 10.0024 C on IPTS-68.

Fahrenheit is a display conversion: F=1.8*C+32. For example, 10 C becomes 50 F.

## Pressure and air pressure

The CTD converts its pressure-sensor signal using calibration and temperature compensation. The stored atmospheric reference establishes the zero for reported water pressure.

P is water pressure in dbar. AP is atmospheric pressure in hPa or mbar and is used in the SIT oxygen conversion.

1 dbar = 0.1 bar = 10000 Pa.
1 hPa = 1 mbar.

EXAMPLE

16.72 dbar = 1.672 bar = 167200 Pa. Depth in metres is calculated from pressure using the selected depth method.

Set the pressure reference according to the instrument procedure. For GSW calculations, sea pressure is absolute pressure minus 10.1325 dbar.

## Depth: modes and fjords

Pressure increases with the weight of the water above the sensor. Converting it to metres therefore depends on water density and gravity.

CHOICES IN CONVERT

Pressure only: retain the measured dbar.

SIT Fixed position: use density calculated from S, T and P at the measurement, together with gravity at the selected latitude. Depth=10000*P/(density*gravity), with density in kg/m3.

UNESCO 1983: use pressure and latitude with a standard seawater relationship. This is a straightforward choice for conventional pressure-to-depth conversion.

SIT-style profiling: add the depth of successive layers using EOS-80 density at each layer endpoint.

GSW reference ocean: use the TEOS-10 reference relationship between pressure and latitude.

TEOS-10 profiling: use the measured S/T/P profile and average the depth-per-pressure factors at each layer's endpoints.

FJORDS

A fresher surface layer has lower density than saltier deep water. The profile choices account for these layers instead of using salinity 35 throughout. Use one continuous cast, select its direction and include the surface layers.

EXAMPLE

S=32.539, T=7.773 C, P=16.72 dbar and latitude 45.50837 degrees give 16.626 m with SIT Fixed position and 16.583 m with UNESCO. The difference reflects how the methods represent the water column.

## Density and Sigma T

Water density depends on salinity, temperature and pressure. In Convert, choose the density method on the Derived seawater properties page.

Choose EOS-80 for comparison with SIT results calculated with EOS-80. Choose TEOS-10 when your project uses Absolute Salinity and TEOS-10 water properties. The SD200W S/T option lets you reproduce results that used that method.

In-situ density describes water at the measured pressure. Sigma T is the EOS-80 density at zero sea pressure, minus 1000. TEOS-10 also provides sigma0, a potential-density anomaly referenced to zero sea pressure.

EXAMPLE

S=32.539, T=7.773 C and P=16.72 dbar give an EOS-80 in-situ density of 1025.451 kg/m3 and Sigma T of 25.374 kg/m3. Use the full density, including the 1000, in the depth equation.

## Sound velocity

SIT calculates sound speed from the water properties. Temperature, salinity and pressure all contribute.

METHOD CHOICES

SIT: the established UNESCO/Chen-Millero-family calculation used for SAIV profiles.

TEOS-10: sound speed calculated consistently with Absolute Salinity and the other TEOS-10 water properties.

Mackenzie 1981: a compact equation using temperature, salinity and depth.

Del Grosso 1974: a pressure-based equation for seawater acoustics.

NPL/Leroy 2008: an equation using temperature, salinity, depth and latitude.

For acoustic projects, choose the method required by the survey or processing system. Convert checks the supported ranges of the alternative methods.

EXAMPLE

S=32.539, T=7.773 C and P=16.72 dbar give 1478.827 m/s with the SIT method.

Equation descriptions: https://resource.npl.co.uk/acoustics/techguides/soundseawater/

## Oxygen: saturation and units

Oxygen concentration is calculated from the reported percentage saturation and the amount of oxygen that water can hold under the selected conditions. Colder, fresher water holds more oxygen at air equilibrium.

Convert treats OX and OxR as percentage saturation and offers mg/L, mL/L, micromol/L and micromol/kg. Select each channel separately.

SIT uses water temperature, salinity and atmospheric pressure. GSW Garcia-Gordon uses a standard-atmosphere reference of 1013.25 hPa. Choose the convention used for the measurement and the comparison data.

EXAMPLE: SIT METHOD

At T=10 C, S=35 and AP=1013.25 hPa, 100% saturation corresponds to 9.02426 mg/L.

At 50%: 9.02426*50/100 = 4.51213 mg/L.

The SIT gas-volume conversion is mL/L = mg/L*22.391/31.998. The example gives approximately 3.1574 mL/L.

Micromol/kg expresses oxygen per mass of water; its conversion also uses water density. Retaining the percentage column makes comparisons between concentration methods easier.

## Oxygen: deep water and alternatives

For deep-water measurements, use the pressure correction and calibration specified for the oxygen sensor. This accounts for how the sensor responds to water pressure. Concentration conversion then uses temperature, salinity and the chosen reference conditions.

SIT's percentage-to-mg/L calculation uses atmospheric pressure. GSW Garcia-Gordon uses one standard atmosphere. Hydrostatic pressure at the sensor belongs to the sensor-pressure correction, not to the atmospheric-pressure field.

International deep-ocean processing also accounts for sensor response time and, where relevant, pressure-history effects. Reference water samples can be used to check the resulting concentrations.

Choose the oxygen convention consistently across a survey. For comparing SIT and GSW results, use the same input measurements and identify the atmospheric reference for each result.

GSW oxygen method: https://www.teos-10.org/pubs/gsw/html/gsw_O2sol.html

## Turbidity: FTU, NTU and FNU

Turbidity is measured optically from light scattered by particles in the water. The sensor calibration converts that response to a turbidity value. SIT retains the reported OT value in FTU.

FTU means Formazin Turbidity Unit. NTU and FNU are related reporting units tied to optical measurement methods. Instruments can agree on a calibration standard yet respond differently to natural particles, depending on light source and viewing geometry.

For comparison between instruments, use their stated optical method and calibration. A fixed multiplier cannot convert every natural-water FTU measurement to NTU or FNU.

EXAMPLE

A reported OT=1.08 is retained as 1.08 FTU.

## Fluorescence

The sensor illuminates the sample and measures the fluorescence emitted in response. Its calibration converts the signal to the reported concentration.

SIT retains OF in ug/L. For chlorophyll work, the relationship to concentration depends on the sensor calibration and the algae in the sample. Reference samples help relate the profile to local conditions.

EXAMPLE

A reported OF=5.67 is retained as 5.67 ug/L.

## PAR and light units

PAR describes light available for photosynthesis. The sensor calibration converts its signal to photon flux. In Convert, select the area unit used in the source data.

1 microeinstein is 1 micromole of photons.

From microeinstein/(m2*s) to micromol photons/(m2*s): keep the number.

From microeinstein/(cm2*s) to micromol photons/(m2*s): multiply by 10000, since one square metre contains 10000 square centimetres.

EXAMPLE

0.05 microeinstein/(cm2*s) becomes 500 micromol photons/(m2*s).

Use the sensor's stated unit. W/m2 measures optical energy; converting that to photon flux also requires the light's spectral information.

## OSU107 measurement chain

OSU107 measures analog sensor outputs, including configured oxygen and PAR channels, as calibrated voltages.

WHAT THIS MEANS FOR YOUR FILE

The logger measures each connected analog sensor's voltage and applies the calibration for that channel. The resulting oxygen, PAR or other measurement is stored in the logger file. In SIT, check the field name and unit before selecting a conversion.

When changing a sensor, use the calibration coefficients supplied for that sensor and its range. The logger's voltage calibration and the sensor's calibration work together to produce the recorded value.

EXAMPLE

For an illustrative sensor calibration of value=-10+0.05*mV, a corrected voltage of 1000 mV gives 40 sensor units. Use your own sensor's coefficients and units for real measurements.

The water-temperature column comes from the CTD. The logger's internal electronics temperature, when used for compensation, is separate. CTD measurements received digitally are stored as supplied by the CTD.

## TEOS-10 and other choices

PSS-78 converts C/T/P to Practical Salinity. EOS-80 calculates seawater properties using Practical Salinity. TEOS-10 adds Absolute Salinity and a common thermodynamic description of the water.

For familiar SAIV results and comparisons with earlier surveys, select the SIT methods. For work using Absolute Salinity, Conservative Temperature and TEOS-10 density or sound speed, select the corresponding GSW choices.

In Convert:

1. Select the salinity, depth and oxygen methods on their measurement pages.
2. Choose density and sound speed on Derived seawater properties.
3. State the recorded temperature scale and supply any required supporting values.
4. For Absolute Salinity, choose reference composition or the geographical atlas with position.
5. Convert and export the named result columns together with the original measurements.

Reference composition uses SA=S*35.16504/35. The atlas option includes regional composition information. Select the assumption appropriate to the water being studied.

## Further reading

For the full equations and scientific background:

PSS-78 salinity and input units:
https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html

EOS-80 and UNESCO seawater calculations:
https://www.teos-10.org/preteos10_software/unesco_44.html

TEOS-10 introduction and calculation documentation:
https://www.teos-10.org/

Use the calibration certificate and manual supplied with the instrument for its sensor coefficients, measuring ranges and accuracy specifications.
