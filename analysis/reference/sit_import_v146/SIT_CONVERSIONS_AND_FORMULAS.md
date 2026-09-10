# SIT: Conversions and formulas

English source for the offline Quick guide, SIT 1.4.6. Reviewed 10 September 2026. This guide documents calculations; it does not change them. Full coefficients are included in the embedded reference-code topics generated from analysis/recovered_formulas.py.

## Conversions and formulas

SIT retains the original SD200W calculation methods: PSS-78 Practical Salinity, EOS-80 density, a UNESCO-family sound-speed polynomial and several pressure-to-depth methods. TEOS-10 is not used in these calculation paths. Modern alternatives below are comparisons and possible future work, not selectable features in this release.

THE NAMES IN PLAIN LANGUAGE

PSS-78 means Practical Salinity Scale 1978: the agreed recipe for converting conductivity, temperature and pressure to Practical Salinity. Conductivity tells us how readily water conducts electricity; the recipe accounts for the effects of temperature and pressure before reporting salinity.

EOS-80 means Equation of State of Seawater 1980: the older recipe connecting salinity, temperature and pressure to seawater density. SIT uses this family for density.

TEOS-10 means Thermodynamic Equation of Seawater 2010 (sometimes mistakenly called EOS-10). It is the newer international framework for calculating related seawater properties consistently, including density, heat-related properties and sound speed. It uses Absolute Salinity, which accounts for composition, rather than treating conductivity-based Practical Salinity as a mass concentration. PSS-78 is still used to obtain SP within the modern workflow; TEOS-10 does not make conductivity measurement obsolete.

Public introductions and formula documentation:
https://www.teos-10.org/
https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html
https://www.teos-10.org/preteos10_software/unesco_44.html

HOW TO READ THIS GUIDE

Each parameter describes its input, output, implemented calculation, limitations and alternatives. "Numerically checked" means reconstructed equations have been compared with original machine code. "Code traced" means the operations were followed but the complete data workflow has not necessarily been tested. "Not yet established" identifies a remaining gap rather than an assumed formula.

THREE DIFFERENT STAGES

1. Instrument firmware turns sensor signals into reported values using that instrument's calibration. A temperature or oxygen percentage may already be calculated before SIT receives it.
2. Original SIT handles CTD/STD datasets, calibration tools and display/export calculations. Its global settings and file metadata can affect results.
3. The added logger Convert wizard handles FIELDS/Full data, offers additional columns and calls the original SIT salinity, sound-speed, density and gravity routines. Its oxygen equation reproduces the original normal equation, but its missing-input rules differ from the old wrapper.

Do not apply resistance, voltage or phase calibration a second time to a reported temperature or oxygen percentage. Firmware documentation alone does not prove a Windows calculation.

REPRODUCING A RESULT

Retain the original file, instrument serial number, firmware/calibration details, units, temperature scale, pressure reference, position, calculation mode and manually supplied values. Compare unrounded results before the displayed decimals. Logger exports record conversion choices and supplied supporting values; original SD2 datasets also depend on their companion files and SIT settings.

The final reference-code topics contain all recovered core coefficients. The evidence and references topics identify code locations, tests and outside sources. Unresolved calibration and profile details are listed explicitly; this is not a claim that every mathematical operation in the entire Delphi executable has been reconstructed.

## Conductivity and salinity

INPUT / OUTPUT

C is conductivity in mS/cm, T is the temperature passed to the routine in degrees Celsius, and P is sea pressure in dbar. 1 S/m = 10 mS/cm; 1000 uS/cm = 1 mS/cm. Do not substitute conductivity normalized to 25 C for in-situ conductivity without knowing how it was normalized.

The output S is Practical Salinity (SP, dimensionless; often labelled PSU historically). It is not Absolute Salinity in g/kg.

IMPLEMENTED: PSS-78, NUMERICALLY CHECKED

R = C/42.914
rt = 0.6766097 + 0.0200564*T + 0.0001104259*T^2 - 6.9698e-7*T^3 + 1.0031e-9*T^4
Rp = 1 + P*(2.07e-5 - 6.37e-10*P + 3.989e-15*P^2) / (1 + 0.03426*T + 0.0004464*T^2 + (0.4215 - 0.003107*T)*R)
x = sqrt(abs(R/(rt*Rp)))
d = T-15
S = 0.008 - 0.1692*x + 25.3851*x^2 + 14.0941*x^3 - 7.0261*x^4 + 2.7081*x^5 + d/(1+0.0162*d)*(0.0005 - 0.0056*x - 0.0066*x^2 - 0.0375*x^3 + 0.0636*x^4 - 0.0144*x^5)

The original routine returns zero for C < 0.01, including negative C. The abs() is also present in the original code. These are implementation behaviours, not scientific validity checks. No Hill low-salinity correction was found in this routine.

CHECK VALUES

C=30, T=10, P=100 gives S=26.82414973.
C=42.914, T=10, P=0 gives S=39.99671809, not 35.
At T=20, P=0, C=0.00999 gives 0, whereas C=0.01000 gives about 0.0128275264.

The inverse S-to-C routine iteratively solves the salinity polynomial with temperature and pressure compensation (tolerance found: 1e-9). Three numerical S-to-C-to-S round trips passed. This is not a constant multiplier between S and C.

LOGGER CONVERT

An existing S field supplies dependent calculations first. Otherwise S is derived from C/T/P where available, then an explicitly supplied missing-S value is used where allowed. Requesting C-to-S with an existing S field adds S_from_C; it does not replace S as the input to the other derived columns. C-to-S requires C/T/P in every row.

BENEFITS / ALTERNATIVES

Keeping PSS-78 reproduces historical SIT results and preserves the measured conductivity-based salinity used in oceanographic archives. The GSW toolbox also uses PSS-78 for SP, with ITS-90 input handling and a modified Hill formula below SP=2. Its documented ordinary PSS-78 range is 2 < SP < 42. The wizard input limits are not proof of accuracy outside the method's validity range.

For TEOS-10 thermodynamic calculations, first obtain SP, then derive SA with pressure and geographic position. Do not rename the existing S column to SA. For unusual freshwater chemistry, conductivity alone does not establish the seawater composition assumed by either method.

Sources: [1], [2], [3]. Original routine: 0x0050A5B8; inverse: 0x0050A6E0. See Temperature for the separate ITS-90/IPTS-68 issue.

WORKED EXAMPLE: CTD VERSUS STD

Suppose an STD record contains S=32.539, T=7.773 C and P=16.72 dbar. The S field is salinity, not a conductivity measurement. SIT's inverse gives C=33.71963249 mS/cm using the same legacy temperature convention. Feeding C=33.719632 back to PSS-78 with the same T/P gives S=32.53899947, which rounds to 32.539.

That round trip demonstrates consistency, not recovery of the original measured C. Rounding of the transmitted S and uncertainty about the instrument's own formula/temperature convention remain. A CTD record containing C/T/P preserves the direct input to later salinity calculations. In this example do not interpret 32.539 as mS/cm.

SAIV RECOMMENDATION

SAIV recommends recording in CTD mode (conductivity, temperature, pressure/depth channel) rather than STD mode (salinity, temperature, pressure/depth channel) whenever possible. Conductivity is the calibrated sensor measurement from which salinity is derived. Keeping C, T and P allows salinity to be checked and recalculated with a documented temperature scale, improved algorithms or future processing. Recording only S loses that original conductivity value and ties later reconstruction to the instrument's formula and rounding. Keep the instrument's calibration details as well: C is a calibrated measurement, not unprocessed raw counts. This is SAIV's data-recording recommendation, not a claim that every STD result is wrong.

## Temperature

INPUT / OUTPUT

SIT normally receives an already calculated T in Celsius. The resistance formula below belongs to the original temperature calibration/recalculation tools; it is not automatically applied to every received CTD text line.

IMPLEMENTED CALIBRATION: CODE TRACED

Let r=ln(R), using the natural logarithm of the resistance value in the units used to obtain the calibration coefficients.
Four coefficients: T = 1/(a + b*r + c*r^2 + d*r^3) - K0.
Three coefficients: T = 1/(a + b*r + d*r^3) - K0 (c=0).

This is the Steinhart-Hart family, with an additional squared-log term in the four-coefficient form. Four coefficients allow a more flexible calibration fit, but require sufficient reliable calibration points and do not by themselves guarantee better accuracy outside the calibrated range. Coefficients and resistance units must remain a matched set.

THE ONE-HUNDREDTH-DEGREE DIFFERENCE

The actual "Old Kelvin constant" handler selects:
Checked: K0=273.16.
Unchecked: K0=273.15.
For identical R and coefficients, the checked choice produces a temperature 0.01 C lower. The handler also recalculates the calibration fit; changing the option in a complete calibration session is therefore not simply an instruction to add 0.01 to every stored temperature.

The "4 coefficients" option and "Old Kelvin constant" are separate choices. The manufacturer's report that newer instruments adopted a changed convention after 2000 needs a firmware/serial-number or calibration record to establish the exact cutover. No such cutover is encoded in the identified handler. The guide does not infer it from the file date.

Modern Celsius/Kelvin conversion uses T_K = t_C + 273.15. The value 273.16 is associated historically with the water triple point, not the modern Celsius zero. Use the convention belonging to the instrument's calibration, rather than changing old coefficients in isolation.

TEMPERATURE SCALE IS ANOTHER ISSUE

The recovered PSS-78 coefficients use the historical IPTS-68 convention. The comparison relation is T68 = 1.00024*T90. This is a scale factor, not a constant 0.01 C correction.

With C=34.5487, T90=28.7856, P=10, the published GSW value is SP=20.009869599086951. The SIT core matches it when fed T90*1.00024; feeding T90 directly gives about 20.012741722649743. The complete legacy instrument/file temperature-scale history is not established. Logger Convert passes the stored Celsius value directly to the native routine. No new scale correction has been inserted.

FAHRENHEIT / TEOS-10

Logger Convert: T_degF = T*9/5+32. Example: 10 C = 50 F. Sensor calculations still use original Celsius values. The original Celsius field may be retained.

TEOS-10 also distinguishes in-situ temperature, potential temperature and Conservative Temperature. These are derived water properties and do not replace thermistor calibration. A possible modern path derives CT from SA, ITS-90 temperature and pressure; it must preserve the measured temperature and identify the new quantity.

Sources: [1], [4], [5]. Code: 0x0052A320, 0x0052A2EC, Kelvin handler 0x00545FF4.

WORKED EXAMPLES

T=7.773 C becomes 7.773*9/5+32=45.9914 F. This changes display units only.
If a resistance formula produces 1/(a+b*r+c*r^2+d*r^3)=280.923 K, subtracting 273.15 gives 7.773 C; subtracting 273.16 with the same coefficients gives 7.763 C.
If a reported 7.773 C is known to be ITS-90, its historical-scale comparison value is 7.773*1.00024=7.77486552 C. Do not apply that scale conversion unless the source scale is established.

## Pressure and air pressure

INPUT / OUTPUT

P is pressure in dbar. AP in logger headers is atmospheric pressure in mbar/hPa. 1 hPa=1 mbar; 1 dbar=100 hPa=10000 Pa; 1 bar=10 dbar. Thus 600 bar=6000 dbar, but 600 mbar=6 dbar. A pressure of 6000 dbar is not a definition of exactly 6000 metres.

IMPLEMENTED USE

P enters the PSS-78 pressure compensation, in-situ density, sound speed and depth calculations. The logger wizard treats P as already supplied sea pressure. It does not subtract AP from each P value. Original SIT has additional pressure/reference and offset handling around depth calculations; retain the file settings when reproducing that path.

For oxygen conversion, logger AP is converted to mmHg as AP*760/1013.25, then used in the original saturation equation. This is atmospheric pressure, not hydrostatic pressure at sensor depth.

The complete pressure-sensor raw-signal calibration and every old pressure-offset path have not been reconstructed. Do not invent a universal polynomial for an instrument that already reports calibrated dbar. Use its calibration record to establish zero, gain, pressure type and any firmware correction.

MODERN COMPARISON

GSW defines sea pressure as absolute pressure minus 10.1325 dbar (one standard atmosphere). A sensor zeroed against local air pressure can have a different reference. Resolve the reference before comparing SIT, GSW and instrument output; do not subtract atmospheric pressure twice. Atmospheric variability, sensor zero drift and the pressure-to-depth model are separate effects.

Pressure itself remains a measured quantity. TEOS-10 changes derived seawater properties, not the definition of the sensor's calibration. See Depth for all four SIT display choices.

Sources: [1], [6]. Logger implementation: sit_import/conversions.inc.

WORKED EXAMPLE

P=16.72 dbar corresponds to 167200 Pa=1.672 bar of sea pressure. For the separate oxygen calculation, AP=925 hPa corresponds to 925*760/1013.25=693.80705650 mmHg. These are different pressures used for different purposes; neither the 925 nor the 693.807 value is a depth.

## Depth: modes and fjords

ORIGINAL SIT HAS FOUR CHOICES

1. Pressure dbar (no calc.): display pressure; this is not a calculated depth in metres.
2. Depth (Unesco 1983): a standard pressure/latitude approximation.
3. Depth = P/(Density x Gravity) Fixed position.
4. Depth = P/(Density x Gravity) Profiling: a separate profile calculation using the water column.

UNESCO FORMULA, CODE TRACED

Let phi be latitude in degrees, P sea pressure in dbar, x=sin(phi*pi/180)^2.
g = 9.780318*(1+(0.0052788+0.0000236*x)*x) + 0.000001092*P.
Depth_m = (((-1.82e-15*P+2.279e-10)*P-2.2512e-5)*P+9.72659)*P/g.

This branch takes P and latitude, not the measured S/T profile. It is a standard-ocean approximation; it should not be described as measuring the actual density of every fjord layer.

FIXED POSITION

Depth_m = 10000*P/(rho*g), where rho is density in kg/m^3.
Using density anomaly q=rho-1000, this is 10*P/((1+q/1000)*g).

Logger Convert's "Real depth" explicitly uses this equation with native EOS-80 in-situ density from S/T/P. It uses supplied GPS latitude, or 45.508368287 degrees when GPS is not selected. Longitude is retained in metadata but does not enter this gravity calculation. Missing T/S must be supplied; they are not silently replaced by 35. This logger path does not implement the native Profiling mode.

Original native depth uses its density wrapper and associated settings; do not assume every old file takes the same density branch as the newer logger wizard.

PROFILING / THE FJORD METHOD

The native code builds a pressure/depth table for each profile. For successive new maximum pressures in the selected traversal direction, the traced normal recurrence is:
k_i = 10000/(rho_i*g_i), in metres per dbar.
First positive knot: z_i = k_i*P_i.
Later knot: z_i = z_previous + k_i*(P_i-P_previous).

Thus each new layer uses that sample's density/gravity, rather than one arithmetic mean salinity or a universal S=35 for the entire water column. For measurements back within the accumulated pressure range, the code linearly interpolates between pressure/depth knots; below the first positive knot it scales from zero. The profile traversal can be reversed. The complete masking, profile-boundary, offset and fallback behaviour has not been validated end to end.

This code is consistent with the reason for SAIV's fjord option: a low-salinity surface layer and a saltier deep layer should contribute different amounts to pressure-to-depth conversion. An arithmetic mean of salinities is not identical to integrating reciprocal density: rho also depends on T and P, and sampling intervals can differ.

BENEFITS / LIMITATIONS

UNESCO is simple and needs only pressure/latitude. A representative density improves local interpretation; layer integration uses the actual profile structure where good S/T data exist. Fixed-position P/(rho_at_sensor*g) treats that density as representative of the overlying column, so it can diverge from integration, especially at large pressure or strong stratification. The name "Real depth" does not remove that approximation. Sparse sampling or a missing surface layer also limits a profile estimate.

MODERN ALTERNATIVE

Hydrostatic depth follows the integral of 10000/(rho*g) over sea pressure in dbar. A possible upgrade uses TEOS-10 density/specific volume and documented numerical integration. GSW z_from_p returns height (negative underwater); depth=-z. Its basic P/latitude call does not automatically consume the observed fjord profile. Dynamic-height and surface-geopotential inputs are needed to include the corresponding corrections. Simply changing the function name to TEOS-10 is not a fjord correction.

Sources: [6], [7]. Native code: 0x0050BCF8, 0x0050CB5C, 0x0050CEA4; profile table 0x0050D374, integration 0x0050D1E0, interpolation 0x0050D024, retrieval 0x0050CD34. New profile findings are code traced; see evidence topic.

WORKED EXAMPLE: TWO DEPTH METHODS

Use S=32.539, T=7.773 C, P=16.72 dbar and the logger default latitude 45.508368287 degrees. Native EOS-80 gives rho=1025.45100788 kg/m^3 and g=9.80666825824 m/s^2.
Fixed position: 167200/(1025.45100788*9.80666825824)=16.62646309 m.
UNESCO P/latitude equation: 16.58282795 m.
Pressure remains 16.72 dbar. The two depths differ by about 0.044 m because their water-column assumptions differ, not because dbar is another spelling of metres.

WORKED EXAMPLE: TWO LAYERS

As a deliberately simplified two-layer calculation, use S=23.738 and T=14.461 C at P=0.30 dbar, then the values above at P=16.72 dbar. At the same latitude, apply the layer recurrence with EOS-80 density at each endpoint. The total is 16.62881923 m. This illustrates the integration rule; two endpoints are not a full observed density profile, and this is not a complete native-file Profiling result.

## Density and Sigma T

IMPLEMENTED: EOS-80 AND AN OLDER ALTERNATIVE

The native core has a zero-pressure density polynomial, an in-situ pressure correction, and a separate older S/T-only equation. All three reconstructed normal formulas have been numerically compared with the original machine code.

Sigma T = rho(S,T,0)-1000.
In-situ density anomaly = rho(S,T,P)-1000.
Add 1000 to either anomaly to obtain the corresponding density in kg/m^3. They describe different reference pressures and must not be interchanged at depth. Sigma T is also not potential density anomaly sigma-theta.

With p=P/10 (bar internally):
rho = rho0/(1-p/K).
K = K0(S,T)+A(S,T)*p+B(S,T)*p^2.
The reference-code topic includes every coefficient of rho0 and K and the older alternative; retaining the exact coefficients is necessary for reproducing SIT.

LOGGER CONVERT

When complete CTD inputs exist, Density_anomaly_SIT_kg_m3 is calculated with the native pressure-dependent EOS-80 routine. Existing derived fields are retained rather than overwritten. S takes precedence over an independently requested S_from_C column. Real depth uses the full in-situ density, not merely its anomaly.

BENEFITS / ALTERNATIVES

EOS-80 keeps old datasets and SIT exports reproducible. Its pressure-dependent branch accounts for seawater compressibility, unlike using only surface density throughout a deep cast. It uses Practical Salinity and the legacy temperature convention, so input scales matter.

TEOS-10 uses Absolute Salinity and thermodynamically consistent relationships among density, heat and sound speed. A possible path is SP -> SA, T90 -> CT, then gsw_rho(SA,CT,P), or an appropriate exact-temperature routine. SA is not numerically identical to SP; CT is not the measured in-situ temperature. Position/composition assumptions and the validity range must be documented. Keeping both legacy and explicitly named TEOS-10 columns would allow comparison without erasing provenance.

The original core accepts some physically invalid inputs; for example its abs(S^3) branch can return a finite density for negative S. A finite number is not a quality flag. The logger wizard rejects negative salinity for its CTD calculations, but that does not establish complete validation in every legacy path.

Sources: [2], [3], [7], [8]. Code: 0x0050C18C, 0x0050C330, 0x0050BF08.

WORKED EXAMPLE

S=32.539, T=7.773 C, P=16.72 dbar gives Sigma T=25.37431736, but in-situ density anomaly=25.45100788 kg/m^3. Therefore full in-situ density is 1025.45100788 kg/m^3. Using 25.451 as the full density in the depth equation would be a major error.

## Sound velocity

IMPLEMENTED: NUMERICALLY CHECKED

SIT computes sound speed in m/s from S, T and sea pressure P. With p=P/10 in bar:
c = W(T,p) + A(T,p)*S + B(T,p)*sqrt(S^3) + D(p)*S^2.
D = 0.001727 - 7.9836e-6*p.
B = -0.01922 - 4.42e-5*T + (7.3637e-5+1.7945e-7*T)*p.

W and A are temperature/pressure polynomials. Every recovered coefficient is in the sound_velocity reference-code topic. This is a UNESCO/Chen-Millero-family coefficient pattern; use the supplied coefficients to identify the precise SIT variant rather than assuming that any modern function called "UNESCO" is bit-identical.

CHECK VALUE

T=10, S=35, P=0 gives 1489.82233602 m/s. This is a calculated sound speed, not an independent acoustic measurement.

It is used by Compute Sound velocity, STD/profile processing and recalculations. Logger Convert can append Sound_velocity_SIT_m_s through the same native core. Existing derived sound-speed columns are preserved. The result depends on salinity and pressure as well as temperature.

ALTERNATIVES AND TRADEOFFS

Mackenzie is a shorter empirical equation using depth, T and S. It is convenient but has its own domain, and depth cannot simply be replaced by dbar. Del Grosso and the NPL/Leroy-Robinson-Goldsmith formulations are other documented acoustic alternatives. Their coefficients, pressure/depth conventions and validity ranges differ; none should silently replace the SIT formula.

GSW sound_speed uses SA, CT and P with a 75-term specific-volume formulation. This provides consistency with other TEOS-10 water properties, with the documented oceanographic range/funnel limitation. A dedicated acoustics project may also need to compare against direct sound-speed calibration and its required uncertainty, rather than choosing solely by publication year.

SIT's main advantage is continuity with historical profiles and reproducible existing exports. The previous ImGui reference document used Mackenzie; at T=10, S=35, surface pressure/depth it gave 1489.80340000 m/s. That historical comparison does not prove the current Studio release uses that old document's formula.

Sources: [9], [10]. Original code: 0x0050A8F0.

WORKED EXAMPLE

S=32.539, T=7.773 C and P=16.72 dbar give c=1478.82737409 m/s. The routine internally uses p=1.672 bar. Use P=16.72 in the reference-code function, which performs the division by ten itself.

## Oxygen: saturation and units

INPUT / OUTPUT

OX (SAIV205) and OxR (RINKO) are separate oxygen fields. Logger Convert assumes their reported values are percent saturation, not raw voltage or optical phase. It offers retaining the original and converting either field to mg/L, mL/L, or both. Do not apply a raw-sensor calibration again.

IMPLEMENTED SATURATION EQUATION

For S, T in Celsius and atmospheric pressure air_mmHg:
K = T+273.15
L = exp(-139.34411+157570.1/K-66423080/K^2+12438000000/K^3-862194900000/K^4)
Fs = exp(-S*(0.017674-10.754/K+2140.7/K^2))
theta = 0.000975-0.00001426*T+0.00000006436*T^2
v = exp(11.8571-3840.7/K-216961/K^2)
p_air = air_mmHg*0.00131578955679
Fp = (1-theta*p_air)*(p_air-v)/((1-v)*(1-theta))
O100_mg_L = L*Fs*Fp
O_mg_L = O100_mg_L*percent/100

If the denominator is zero, the original correction branch uses factor 1. These exact constants, rather than an inferred publication label, define the verified SIT model. Three normal-equation oxygen cases have been compared numerically with the native wrapper.

Logger AP is in hPa: air_mmHg = AP*760/1013.25. A supplied positive AP overrides header AP; otherwise header AP is used. T/S come from measured fields, S calculated from C/T/P where needed, or explicitly supplied missing values. Missing oxygen cells stay empty. Input checks are not a declaration of scientific validity over the entire accepted range.

UNIT CONVERSIONS FOUND IN ORIGINAL SIT

mg/L -> mL/L: multiply by 22.391/31.998.
mg/L -> umol/L: multiply by 1000/31.998.
mg/L -> umol/kg: multiply by 22.391*1000/(716.467218*(rho/1000)).

Here rho is the density used by the selected native path, in kg/m^3. The mass-specific unit is different from per-litre units; reproduce the density convention as well as the constants. The mL value is a gas-equivalent amount under the convention embodied in the constant, not a volume of bubbles at sensor depth. The newer logger wizard does not offer the two micromole outputs.

CHECK VALUES AT 100% SATURATION

T=10, S=35: 760 mmHg gives 9.02425975 mg/L; 700 mmHg gives 8.30363061 mg/L.
At T=20 and 760 mmHg: S=0 gives about 9.0924 mg/L, whereas S=34.5 gives about 7.4179 mg/L.

KNOWN LEGACY DIFFERENCE

Original wrapper 0x0050BC10 forces S=34.5 if the file's S/C channel flag is zero. This behaviour is numerically confirmed, but not every display/file has been shown to enter it. It can differ from an intended freshwater assumption. The added logger Convert path uses its explicit T/S rules and does not reproduce that hardcoded missing-channel fallback.

Modern oxygen models and deep-water limitations are described in the next topic. The pressure in Fp above is air pressure; it must never be replaced by sensor hydrostatic pressure.

Code: 0x0050C818, wrapper 0x0050BC10, unit handling near 0x0050C818; logger sit_import/conversions.inc. Local numerical evidence is listed under Verification and sources.

WORKED EXAMPLE: LOW OXYGEN

For S=32.539, T=7.773 C, AP=925 hPa and oxygen=3.47%, the equation gives O100=8.78599291332 mg/L. Then:
8.78599291332*3.47/100 = 0.30487395 mg/L.
0.30487395409*22.391/31.998 = 0.21333936 mL/L.
Using the unrounded result, the original unit factors give 9.52790656 umol/L. If the selected density is the EOS-80 in-situ value 1025.45100788 kg/m^3 at P=16.72 dbar, the native mass-unit expression gives 9.29143029 umol/kg.

3.47% is the input saturation percentage, not 3.47 mg/L. AP=925 hPa is an explicit example assumption; choose the correct atmospheric pressure for actual work. This example verifies a conversion only, not the validity of a sensor reading or its pressure compensation.

## Oxygen: deep water and alternatives

WHAT SIT DOES AT DEPTH

The recovered percent-to-mg/L equation uses temperature, salinity and atmospheric pressure. It has no direct hydrostatic-pressure argument. Pressure can affect S calculated from conductivity, and density affects native umol/kg conversion, but these indirect effects are not a sensor pressure-response correction.

The logger conversion does not add a raw RINKO or SAIV205 pressure-response, response-time or hysteresis correction. Instrument firmware may already have compensated the reported percentage; the exact behaviour must be established from the sensor model, calibration and firmware. The original Rinko calibration menu has been identified, but its complete calibration/pressure chain has not been reconstructed. Therefore this guide cannot certify that every old native oxygen path either includes or omits all deep-water corrections.

THREE DISTINCT QUESTIONS

1. Solubility: what concentration corresponds to equilibrium with air under the stated reference conditions?
2. Sensor response: how do hydrostatic pressure, temperature, time response and sensor history affect the measured electrical/optical signal?
3. Units: is oxygen reported per litre or per kilogram, and which density/reference convention is used?

A more modern solubility equation answers question 1; it does not automatically solve question 2. Water at depth is not necessarily in equilibrium with an air bubble at the full surrounding hydrostatic pressure.

INTERNATIONAL METHODS

Garcia and Gordon (1992, corrected 1993), fitted to Benson and Krause data, is used by GSW O2sol. GSW returns umol/kg for equilibrium with air at 101325 Pa, including saturated water vapour. It is an auxiliary best-practice algorithm in GSW, explicitly not an IOC-approved component of the TEOS-10 thermodynamic formulation. Its standard-atmosphere reference is not a drop-in replacement for SIT's user/header barometric correction.

GSW O2sol accepts SA, CT, P and position, but the reference equilibrium remains at zero sea pressure. O2sol_SP_pt accepts Practical Salinity and potential temperature. Choose the temperature/reference convention deliberately when comparing to SIT's in-situ T input.

Deep-ocean sensor processing is model-specific. Published SBE43 work distinguishes static membrane-pressure compensation, time response and pressure-history hysteresis, with bottle samples used for assessment. Modern optode processing likewise has sensor-specific pressure and response corrections; use the applicable Argo/manufacturer procedure. SBE43 coefficients must not be copied into SAIV205 or RINKO processing.

TRADEOFFS / POSSIBLE FUTURE WORK

The current SIT equation keeps historical concentrations reproducible and explicitly uses measured air pressure. A modern optional path could add named Garcia-Gordon/GSW outputs, explicit reference conditions, unit/density conventions and documented sensor corrections where raw information is available. Deep-water acceptance should compare against appropriate reference samples such as Winkler determinations and retain pressure/time history. Neither TEOS-10 nor any generic factor can recover missing calibration or undo an unknown firmware correction reliably.

Sources: [11], [12], [13], [14]. These describe alternatives; they are not implemented by this guide update.

## Turbidity: FTU, NTU and FNU

IMPLEMENTED IN SIT

OT is the turbidity channel, labelled FTU in original SIT. The checked legacy ASCII import preserved all 43 OT values into the native OP2 data without rescaling. Logger import/Convert also retains OT values and records FTU; it does not calculate an NTU or FNU replacement.

FTU means Formazin Turbidity Unit. The other labels commonly encountered are NTU (Nephelometric Turbidity Unit) and FNU (Formazin Nephelometric Unit).

WHY THE LABEL MATTERS

Turbidity depends on the optical method, including illumination wavelength and observation geometry. USGS distinguishes NTU for the EPA 180.1 method from FNU for ISO 7027-type infrared nephelometry. Its reporting guidance notes that FTU does not identify a particular measurement technology.

Matching a formazin calibration value does not establish that instruments with different optical methods will agree on natural fjord water. There is no universal scalar conversion FTU -> NTU -> FNU for arbitrary samples, nor a general conversion to suspended sediment in mg/L. A sensor-specific method declaration and, for sediment concentration, a site/sample calibration are needed.

BENEFITS / POSSIBLE IMPROVEMENT

Retaining the received FTU value preserves legacy measurements. A clearer future export could record the sensor model, optical method, calibration standard and method-appropriate unit. Confirm these before relabelling OT as FNU. A unit-name change alone is not a measurement correction.

The complete raw-sensor turbidity calibration is not reconstructed in the Windows program. Firmware coefficient notes are not sufficient evidence of a PC-side equation.

Source: [15]. Local import evidence: sd200DOc/PROSJEKTSTATUS.md and LES_MEG_Import_122.md; current converter: sit_import/conversions.inc.

WORKED EXAMPLE

A reported OT=1.08 is retained as 1.08 FTU by the checked SIT paths. Do not turn it into "1.08 FNU" merely by changing the label; method equivalence must first be established for the sensor.

## Fluorescence

IMPLEMENTED IN SIT

OF is the fluorescence channel, labelled ug/L in original SIT. The checked 43-row legacy import retained OF numerically in OP2. Logger conversion likewise retains OF without rescaling. No new conversion from raw voltage, counts or fluorescence intensity is applied by that wizard.

INTERPRETATION

The displayed concentration depends on the calibration used by the instrument. Do not infer from the label alone that all sensors, standards and natural samples have identical fluorescence-to-concentration response. Preserve the sensor model, calibration and reported unit along with the values.

The Windows raw-sensor calibration chain has not been completely reconstructed. The local firmware coefficient overview marks several relationships as assumptions, so those expressions are not presented here as verified SIT calculations.

POSSIBLE IMPROVEMENT

Document sensor-specific calibration provenance and distinguish a reported calibrated concentration from raw fluorescence. Any new calibration conversion would need the applicable sensor equation and supporting measurements. TEOS-10 is a seawater thermodynamics framework, not a replacement for this optical calibration.

Local evidence: sd200DOc/FORMELKARTLEGGING.md, sd200DOc/PROSJEKTSTATUS.md and sit_import/conversions.inc.

WORKED EXAMPLE

A reported OF=5.67 is retained as 5.67 ug/L. The import multiplies it by neither 1000 nor a seawater-density factor. The concentration interpretation still belongs to the original optical calibration.

## PAR and light units

IMPLEMENTED IN LOGGER CONVERT

Par is Photosynthetically Active Radiation. The wizard asks for the source area unit when converting a photon-flux value:
uEinstein/(m^2*s) -> umol photons/(m^2*s): multiply by 1.
uEinstein/(cm^2*s) -> umol photons/(m^2*s): multiply by 10000.

One microeinstein denotes one micromole of photons. The area factor follows from 1 m^2=10000 cm^2. The output column is Par_umol_m2_s; the source column may be retained. Example: 0.5 uEinstein/(cm^2*s) becomes 5000 umol photons/(m^2*s).

The value range alone cannot tell which area unit the instrument used. The program does not infer it from a typical 1-5000 reading. Empty PAR cells remain empty during conversion.

WHAT THIS DOES NOT CALCULATE

This is unit conversion of an already reported photon flux, not a raw PAR-sensor calibration. Radiant power in W/m^2 cannot be converted to photon flux by the area multiplier alone; photon energy depends on wavelength and a broadband result requires spectral information or an explicitly justified approximation. PAR is not the same quantity as photometric illuminance in lux.

BENEFIT / POSSIBLE IMPROVEMENT

The current explicit area choice prevents a factor-of-10000 ambiguity. A future importer could use reliable source-unit metadata while retaining the original unit and provenance. TEOS-10 has no role in this unit conversion.

Implementation: sit_import/conversions.inc; LES_MEG_Fahrenheit_PAR_135.md. The multipliers are exact unit identities, not empirically fitted seawater formulas.

## Other calculations and limits

CONDUCTIVITY CALIBRATION

The original calibration selector contains these four expressions:
y = a+b*x+c*x^2+d*x^3
y = a+b*x+c*x^2
y = 1/(a+b*x^2.5+c/x)
y = a+b*x

They include polynomial, SAIV 1/x and linear options. These fit instrument calibration input to conductivity; they are separate from PSS-78. The complete meaning/scaling of x and mapping to instrument coefficients/commands have not been established. Do not substitute ordinary conductivity for x without the calibration definition.

FITTING AND DRIFT

Least-squares fitting controls (LSQFIT/ssq) and temperature-drift tables are present. All fit weights, stopping rules and drift transformations are not yet reconstructed. Additional coefficients can improve a fit only if the calibration data support them. No generic drift polynomial has been asserted as the actual program formula.

PROFILE TABLES AND EXPORTS

SIT includes standard depths, standard-depth sections, standard temperatures and averaging across passes. These are data-processing operations as well as presentation. Their full interval selection, weighting, interpolation, empty-bin and masking rules still require separate reconstruction. The depth-table interpolation described in the Depth topic must not be assumed to be the interpolation used by every export.

OTHER NATIVE PATHS

Temperature/pressure offsets trigger derived-value recalculation in identified paths. There is a historical correction command for wrongly interpreted salinity/conductivity in old files, and a dedicated Rinko calibration menu. Their complete conditions and formulas are not yet established. Generic mathematical-library strings alone are not evidence that a function is an active measurement calculation.

LOGGER DERIVED FIELDS

The wizard preserves original-field choices and explicitly named derived columns. It rejects a duplicate requested conversion column instead of silently overwriting it; existing sound-speed/density columns can be retained. Missing supporting T/S must be supplied for depth/oxygen when unavailable. Merge aligns timestamps within its selected tolerance; it does not average sensor values or correct unsynchronised clocks.

SCOPE OF THIS GUIDE

The recovered core formulas are reproducible with the included reference code. The remaining items above are listed so they are not lost or replaced by plausible but unverified equations. Original Delphi source is unavailable; firmware, raw calibration and complete native workflows require their own evidence.

## TEOS-10 and other choices

WHAT IS USED NOW

SIT uses its original PSS-78/EOS-80 and associated legacy formulas. It does not currently offer a TEOS-10 switch. Choosing Fahrenheit or "Real depth" does not enable TEOS-10.

WHAT A MODERN TEOS-10 PATH WOULD LOOK LIKE

SP = gsw_SP_from_C(C_mS_cm, T90_C, P_dbar)
SA = gsw_SA_from_SP(SP, P, longitude, latitude)
CT = gsw_CT_from_t(SA, T90, P)
rho = gsw_rho(SA, CT, P)
sound_speed = gsw_sound_speed(SA, CT, P)

This is a proposed comparison workflow, not executable SIT code. Practical Salinity should still be retained as the conductivity-based observation. Absolute Salinity introduces composition information; Conservative Temperature supports heat-related calculations. Ocean atlases and standard-composition assumptions do not automatically characterize unusual local freshwater chemistry.

CHOICE BY PURPOSE

Historical SIT compatibility: retain the existing formulas and input conventions.
Oceanographic thermodynamic consistency: TEOS-10/GSW is the international framework to evaluate; preserve SP, SA, in-situ T and CT as distinct quantities.
Very low salinity: examine the modified Hill treatment and actual water composition, not just the C cutoff.
Pressure-to-depth in a stratified fjord: use a documented water-column density integration or dynamic-height correction, with sufficient profile coverage.
Acoustic work: compare SIT with appropriate GSW, Del Grosso, Mackenzie or NPL formulations within their domains and required uncertainty.
Oxygen: assess the solubility model and sensor-specific compensation separately; GSW oxygen is not an automatic deep-sensor correction.
Turbidity/fluorescence/PAR: use sensor calibration and optical/unit conventions; a seawater equation of state does not replace them.

BENEFITS AND COSTS

The legacy path provides continuity with existing measurements, calibrations and exports. A modern path can provide clearer conventions, published reference implementations and internally consistent water properties. It also needs explicit temperature scales, salinity type, position/reference assumptions and validation; results may change. A sensible future design would offer separately named legacy and modern outputs with calculation metadata, rather than silently rewriting old datasets.

THE EARLIER IMGUI COMPARISON

The archived reference document differed from SIT: its salinity expression omitted SIT's rt/Rp compensation; its oxygen conversion omitted barometric correction; it used Mackenzie sound speed; and it did not represent all density modes. For C=30, T=10, P=100 it gave S=23.55343140 versus SIT's 26.82414973. Those differences were not evidence that TEOS-10 was implemented there. The working document was subsequently corrected to SIT; the archived comparison describes that earlier document, not a blanket claim about today's Studio executable.

Sources: [1]-[3], [5]-[14]; local historical comparison: sd200DOc/KONVERTERING_SAMMENLIGNING.md.

## Verification and sources

LOCAL EVIDENCE

The legacy core was reconstructed from the executable, not original Delphi source. The guide update preserves measurement/calibration/communications code. Addresses in these topics assume image base 0x00400000; relocated instances require the corresponding relative address.

Recovered normal equations: analysis/recovered_formulas.py.
Original numeric comparison: analysis/formula_numeric_validation.json (24 cases).
External salinity examples, oxygen fallback and inverse checks: analysis/formula_audit_tests.json.
Earlier ImGui-document comparison: analysis/conversion_document_comparison.json.
Detailed existing mapping: sd200DOc/FORMELKARTLEGGING.md and FORMELKONTROLL.md.
New Kelvin/profile evidence and release checks: analysis/formula_guide146_validation.json.

The original numeric cases cover selected combinations, including pressure to 4000 dbar; they do not certify every instrument, the entire model domain or every export. Code identity proves a calculation was preserved, not that all original science and input handling were correct.

COPYABLE REFERENCE CODE

The following topics include complete recovered core coefficient sets in Python syntax. Concatenate them in order, retaining indentation, and run under Python 3. No extra package is required for that reference calculation. They reproduce equations, not the entire instrument/file/GUI workflow. Calibration coefficients, metadata and mode decisions still have to be supplied correctly. Numerical checking against native code is separate from physical validation against calibrated reference measurements.

EXTERNAL SOURCES (checked 10 September 2026)

[1] GSW SP_from_C: PSS-78, modified Hill, units and ITS-90 input.
https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html

[2] GSW SA_from_SP: Absolute Salinity and geographic inputs.
https://www.teos-10.org/pubs/gsw/html/gsw_SA_from_SP.html

[3] TEOS-10 manual and framework, including retention of Practical Salinity observations.
https://www.teos-10.org/pubs/gsw/pdf/TEOS-10_Manual.pdf
https://www.teos-10.org/

[4] BIPM SI Brochure and Kelvin history: Celsius offset and triple point.
https://www.bipm.org/documents/d/guest/si-brochure-9-2_01
https://www.bipm.org/en/history-si/kelvin

[5] GSW CT_from_t: Conservative Temperature.
https://www.teos-10.org/pubs/gsw/html/gsw_CT_from_t.html

[6] GSW z_from_p: height sign and optional dynamic-height inputs.
https://www.teos-10.org/pubs/gsw/html/gsw_z_from_p.html

[7] UNESCO 1983 algorithms (legacy background).
https://www.teos-10.org/preteos10_software/unesco_44.html

[8] GSW rho: in-situ density.
https://www.teos-10.org/pubs/gsw/html/gsw_rho.html

[9] GSW sound_speed: SA/CT/P and validity funnel.
https://www.teos-10.org/pubs/gsw/html/gsw_sound_speed.html

[10] UK National Physical Laboratory: sound-speed equations and conventions.
https://resource.npl.co.uk/acoustics/techguides/soundseawater/

[11] GSW O2sol: reference equilibrium and Garcia-Gordon coefficients.
https://www.teos-10.org/pubs/gsw/html/gsw_O2sol.html

[12] GSW O2sol_SP_pt: Practical Salinity/potential temperature interface.
https://www.teos-10.org/pubs/gsw/html/gsw_O2sol_SP_pt.html

[13] Edwards et al. (2010): Calibration, Response, and Hysteresis in Deep-Sea Dissolved Oxygen Measurements.
https://journals.ametsoc.org/view/journals/atot/27/5/2009jtecho693_1.xml

[14] Argo Data Management documentation: current oxygen processing cookbook.
https://www.argodatamgt.org/Documentation

[15] USGS Technical Memorandum 2004.03: turbidity method/unit distinctions.
https://water.usgs.gov/admin/memo/QW/qw04.03.html
