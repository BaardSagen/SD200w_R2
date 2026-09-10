# SIT: Conversions and formulas

English source for the offline Quick guide, SIT 1.4.8. Reviewed 10 September 2026. Start with System evaluation for practical guidance. The native SD200W routines are preserved; Convert offers explicitly selected alternatives. Full coefficients are included in the embedded reference-code topics generated from analysis/recovered_formulas.py.

## System evaluation

THE PRACTICAL CHOICE

For new measurements, SAIV recommends recording CTD (conductivity, temperature and pressure) and keeping those original values. Use the native SIT methods to reproduce historical results. Use GSW/TEOS-10 for new seawater-property calculations when the temperature scale, pressure reference and required salinity assumptions are known.

The largest improvement usually comes from correct calibration and preserving measurements. A newer formula cannot remove fouling, repair a wrong zero or restore digits lost before the file was saved.

WHAT DO THE NAMES MEAN?

PSS-78: calculates Practical Salinity from conductivity, temperature and pressure. This remains useful today, including within the modern workflow. GSW adds a low-salinity extension that the native SIT routine lacks.

EOS-80: calculates density and related seawater properties using Practical Salinity. Choose it for consistency with original SIT/SD200W and older datasets.

TEOS-10: calculates seawater properties consistently using Absolute Salinity. Its advantage is a common physical basis for density, temperature-related properties and sound speed. It does not make the conductivity sensor more accurate. Keep Practical Salinity as well; Absolute Salinity is a different quantity with different units.

They are different tools with different jobs, not three successive versions of one salinity equation.

OLD OR NEW TEMPERATURE CALIBRATION?

Four Steinhart-Hart coefficients can fit the calibrated temperature range more flexibly than three. This helps only if reliable calibration points demonstrate a better fit. Always use the coefficients and convention belonging to the instrument.

The old Kelvin constant is separate: 273.16 versus 273.15 produces a 0.01 C difference with identical coefficients. It is not a reason to add 0.01 C to every old file. ITS-90/IPTS-68 is another, separate scale conversion. TEOS-10 does not replace temperature calibration.

WHAT DO I LOSE IN STD MODE?

STD stores calculated salinity instead of the calibrated conductivity. Conductivity can be estimated back under an assumed equation, but rounded salinity cannot recover the exact original C. Recording CTD preserves more freedom to review and recalculate salinity later. Neither mode preserves every internal sensor signal.

OTHER PARAMETERS: WHAT MATTERS MOST?

Depth: use a documented pressure reference. A measured density profile can represent a stratified fjord better than a fixed salinity of 35; a simple mean salinity is still an approximation.

Density and sound speed: TEOS-10 offers consistency; native methods offer historical comparability. Use alternative acoustic equations only within their stated ranges.

Oxygen: correct sensor calibration, units, air-pressure convention and response at depth matter. A solubility equation alone cannot correct an unknown deep-water sensor response.

OSU107 OX/PAR: these analog channels have their own measurement chain. CTD accuracy does not transfer to them. The supplied documents do not quantify a complete, directly comparable channel accuracy; ADC bit count alone cannot establish it.

Turbidity, fluorescence and PAR: optics, calibration, range, fouling and units matter more than choosing a seawater equation. FTU/NTU/FNU cannot be universally converted by a fixed multiplier.

For the reasons, examples and evidence behind these recommendations, open System: measurement quality. The individual parameter topics contain the equations and detailed choices.

## System: measurement quality

START HERE: WHAT IMPROVES THE RESULT?

A well-calibrated instrument, correct units and preserved C/T/P are the foundation. Choosing a newer equation improves how measurements are interpreted; it cannot recover information already lost through rounding, fouling, an unsuitable sensor range or incorrect calibration. An old equation does not by itself make a measurement poor, and extra displayed decimals do not prove extra accuracy.

For comparison with historical SD200W results, use the native SIT methods and the original conventions. For new seawater-property calculations, use the named GSW/TEOS-10 choices with a documented temperature scale, pressure reference and salinity assumption. Keep the original measurements alongside derived columns. Convert choices do not change instrument firmware or the old Compute/calibration menus.

THE THREE NAMES HAVE DIFFERENT JOBS

PSS-78 converts conductivity, temperature and pressure into Practical Salinity (SP). It remains part of the modern workflow. It is useful for comparing CTD observations over time.

EOS-80 calculates seawater properties such as density from SP, temperature and pressure. Its main advantage here is compatibility with original SIT/SD200W and older datasets.

TEOS-10 calculates seawater properties in a consistent thermodynamic framework, using Absolute Salinity (SA). Its advantage is consistency between density, temperature-related properties and sound speed, including a treatment of seawater composition. SP and SA are different quantities, not two estimates in the same units. TEOS-10 is not a replacement thermistor calibration or a direct salinity sensor.

WHICH SALINITY METHOD SHOULD I USE?

Native PSS-78 is appropriate when reproducing original SIT processing. The GSW conductivity-to-SP choice includes the Hill extension below SP=2, avoiding the original routine's simple low-conductivity behaviour. This is useful for low-salinity water, but does not prove accuracy in unusual freshwater chemistry or outside the conductivity sensor's calibration.

For TEOS-10 properties, preserve SP and calculate SA separately. The reference-composition choice makes a declared composition assumption. The geographical atlas choice adds position-dependent information, but is not a local chemical measurement and cannot guarantee a better composition estimate in every fjord. At SP=35, reference-composition salinity is approximately 35.16504 g/kg; this difference is not a 0.16504 measurement error.

WHAT DOES THE CTD CALCULATE BEFORE SIT RECEIVES DATA?

The reviewed SD208 firmware report describes a separate conductivity module, followed by linearisation, optional coefficient-based internal-resistance compensation and a quadratic conductivity calibration. It then calculates SP using the PSS-78 polynomial. This is not a simple conductivity multiplier and is not TEOS-10. SIT receives the resulting calibrated values; it does not undo that measurement chain.

Firmware and native SIT use the same salinity polynomial family but are not exactly identical. Firmware uses C*0.023302418; SIT uses C/42.914. With T=15 and P=0, C=42.914 gives approximately SP=34.9999986 in the firmware reference and 34.9999999 in SIT. That tiny numerical difference is not a useful improvement in sensor accuracy. Low-conductivity guards also differ, and the firmware passes temperature directly without an explicit ITS-90/IPTS-68 conversion.

CTD mode preserves calibrated conductivity, temperature and pressure. STD mode retains calculated salinity instead of conductivity. Conductivity can be estimated back from S/T/P under an assumed equation, but the exact original conductivity and internal precision cannot be recovered from rounded output. Retaining C allows later calibration review and recalculation with an explicitly chosen salinity method. CTD output is still calibrated data, not untouched ADC counts.

The documented SD208 text format reports C/S/T to three decimals and pressure to two; SD204 C/S use two. If values are rounded to the nearest 0.001, the formatting contribution can be up to 0.0005 in that field's unit; at 0.01 it can be up to 0.005. Internal salinity uses values before text formatting, so a host recalculation can legitimately differ. These are conditional rounding examples, not total accuracy specifications. Increasing decimals later cannot restore discarded digits.

TEMPERATURE: OLD AND NEW STEINHART-HART

The three-coefficient resistance equation is simpler. The four-coefficient form adds a squared-log term and can fit a calibrated temperature range more flexibly. Its benefit must be demonstrated by calibration residuals and independent check points; an extra coefficient alone does not establish better accuracy. The reviewed SD208 firmware uses the four-coefficient form and subtracts 273.15.

The old Kelvin constant is a separate issue: subtracting 273.16 instead of 273.15 makes the result 0.01 C lower for identical coefficients. SIT can refit coefficients when that setting changes, so do not add 0.01 C to old files automatically. Use the convention and coefficients belonging to the instrument. The documents do not establish a reliable production-year or serial-number cutover.

ITS-90 versus IPTS-68 is a third, separate issue. The comparison relation T68=1.00024*T90 is a scale factor: at 10 C the difference is 0.0024 C, not 0.01 C. TEOS-10 does not repair an incorrect thermistor fit. See Temperature for the equations and examples.

PRESSURE AND DEPTH: WHERE THE CHOICE MATTERS

The reviewed CTD firmware calibrates pressure, compensates it using internal resistance and subtracts a stored atmospheric reference. It outputs nonnegative relative pressure in dbar, not a density-based depth. Clipping negative pressure to zero hides negative zero-offset information. Establish the reference before treating the result as the sea pressure required by a selected model.

The UNESCO pressure/latitude method is simple and reproducible but represents reference seawater. SIT's Fixed position/EOS-80 method uses salinity, temperature and gravity and suits compatibility work. A profile-based method uses the water column's changing density; this is particularly useful where a freshwater layer overlies saltier water. A single fixed salinity of 35 cannot represent every fjord, while an arithmetic mean salinity is still only an approximation to integrating density through the profile.

GSW reference depth is convenient but does not automatically integrate your measured density profile. The TEOS-10 profile choice does that layer calculation with declared assumptions. Its benefit depends on valid, adequately sampled T/S/P through the column. Missing surface layers, reversals and gaps matter. See Depth: modes and fjords for the actual implemented choices.

Pressure accuracy still limits every depth calculation. For illustration, an accuracy of 0.01% of full scale means 0.1 dbar for a 1000 dbar range and 0.6 dbar for a 6000 dbar range. These examples explain a specification, not a verified specification for the connected instrument.

DENSITY AND SOUND SPEED

EOS-80/native sound calculations preserve historical comparability. TEOS-10 gives a consistent modern calculation from the same declared water properties. Mackenzie, Del Grosso and NPL provide named acoustic alternatives within their stated domains; none is universally best at every depth. Calculated sound speed is not an independent acoustic measurement. Do not confuse in-situ density with Sigma T or sigma0: their reference conditions differ. See the parameter pages before comparing numbers.

OXYGEN, INCLUDING DEEP WATER

The reviewed SAIV 205 firmware path converts a corrected ADC signal to voltage and then to percentage using a calibration reference. No explicit water T/S/P solubility calculation was identified in that path; compensation inside a particular sensor must be checked separately. Other oxygen sensors and option fields can use different units and calibration chains.

SIT's legacy percentage-to-concentration conversion retains its temperature, salinity and air-pressure convention. The GSW oxygen-solubility alternative uses a specified one-atmosphere reference. Results with different air-pressure assumptions are not a pure comparison of equation accuracy. Neither conversion corrects an unknown sensor response at depth. Deep-water work needs the sensor manufacturer's pressure response, calibration convention and response-time information. Do not substitute hydrostatic water pressure for atmospheric pressure in an air-saturation equation. See both Oxygen pages.

OSU107 OXYGEN/PAR: A DIFFERENT MEASUREMENT CHAIN

CTD values received digitally by OSU107 are not measured again by OSU107's analog converter. Its analog oxygen/PAR channels have their own sensor, input electronics, multiplexer, reference, calibration and timing. Consequently, CTD accuracy specifications must not be applied to these channels.

The handover documents identify ADS1263, reference checks and warmup/calibration procedures. The chip's nominal resolution is not the complete channel's accuracy. The reported lower accuracy of OSU107 analog OX/PAR has not been quantified by a comparable full-chain uncertainty specification in the supplied documents. A numerical ranking against CTD therefore remains unverified. Reference checks are useful diagnostics, not a complete sensor calibration.

Warmup, input range, sensor response and stored decimals can matter more than the last digits of a conversion formula. OSU107 channel decimals are configurable; a two-decimal setting alone says nothing about accuracy in mg/L or PAR until the channel's units and scaling are known. Retain channel configuration and calibration with the data. Never treat a missing/invalid measurement as zero.

TURBIDITY, FLUORESCENCE AND PAR

FTU, NTU and FNU describe optical measurement/calibration conventions. Renaming FTU to FNU or NTU does not change the optics or improve accuracy; there is no universal conversion valid for every particle mixture. Range selection prevents overload but does not correct fouling or particle-dependent response.

Fluorescence is a calibrated optical response; species, physiological state and quenching can change its relationship to chlorophyll concentration. PAR needs the correct sensor sensitivity and area unit. Changing cm2 to m2 is an exact unit conversion, while changing optical watts to photon flux requires spectral information. These limitations cannot be removed by selecting TEOS-10.

PRACTICAL RECOMMENDATION

Record C/T/P, preserve original fields and instrument/calibration details, and use named derived columns. Choose native methods for historical reproduction; choose GSW/TEOS-10 for new seawater-property work when its required inputs and assumptions are established. Check calibration, zero, fouling, range, warmup and sampling before attributing a difference to an equation. More computation is useful only when the measurements support it.

EVIDENCE AND FURTHER READING

This assessment combines recovered native SIT calculations, the source-reviewed SD208 report supplied in asmCTDdoc, and OSU107 firmware handovers. It is not a calibration certificate, a dump of the connected instrument's EEPROM, or an independent inspection here of the assembly sources referenced by that report. Exact deployed firmware, coefficients and complete OSU107 channel uncertainty remain instrument-specific.

Public background: https://www.teos-10.org/
Low-salinity algorithm: https://www.teos-10.org/pubs/gsw/html/gsw_SP_from_C.html
Older seawater algorithms: https://www.teos-10.org/preteos10_software/
ADC component information (not a system accuracy specification): https://www.ti.com/product/ADS1263

## Conversions and formulas

The original SD200W routines use PSS-78 Practical Salinity, EOS-80 density, a UNESCO-family sound-speed polynomial and several depth methods. Those native routines do not use TEOS-10. In SIT 1.4.7, the Convert wizard additionally offers GSW/TEOS-10 and named alternative methods. The choice applies to Convert outputs; it does not change the native calibration tools or the old Compute/recalculation menus.

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
3. Convert handles FIELDS/Full logger data and CTD/STD text with a declared Date/Time and whole-second Interval. It offers both native routines and named new models. Legacy row times are reconstructed from the header and sequence order and labelled accordingly. Original File > Import dispatch remains separate.

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

An existing S field supplies dependent calculations first. Otherwise S is derived from C/T/P where available, then an explicitly supplied missing-S value is used where allowed. Requesting C-to-S with an existing S field adds S_from_C. By default S still supplies dependent calculations; the checkbox "Use this calculated salinity" explicitly changes that priority. C-to-S requires C/T/P in every row.

SELECTABLE IN CONVERT

On C, keep conductivity, use original SIT PSS-78, use GSW PSS-78 with modified Hill below SP=2, or add both GSW SP and TEOS-10 SA. On an S-only input, retain SP and optionally add SA/CT. SA never replaces the meaning of S. The final page chooses Reference Composition (SA=SP*35.16504/35) or the geographic GSW atlas; the latter requires an actual supplied position. Reference Composition is an explicit approximation where no composition anomaly is supplied.

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

With C=34.5487, T90=28.7856, P=10, the published GSW value is SP=20.009869599086951. The SIT core matches it when fed T90*1.00024; feeding T90 directly gives about 20.012741722649743. The complete legacy instrument/file temperature-scale history is not established. The default "As recorded" choice passes stored Celsius directly, reproducing legacy SIT. Choosing ITS-90 sends T90*1.00024 to legacy PSS-78/EOS-80/sound equations. Choosing IPTS-68 sends T68/1.00024 to modern equations. Modern selections require an explicit scale; the file date alone does not establish it.

FAHRENHEIT / TEOS-10

Logger Convert: T_degF = T*9/5+32. Example: 10 C = 50 F. Sensor calculations still use original Celsius values. The original Celsius field may be retained.

TEOS-10 also distinguishes in-situ temperature, potential temperature and Conservative Temperature. These are derived water properties and do not replace thermistor calibration. The TEOS-10 path adds separately named SA and CT columns from SP, ITS-90 temperature and pressure. Original T is retained by default.

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

Logger Convert's "Real depth" explicitly uses this equation with native EOS-80 in-situ density from S/T/P. It uses supplied GPS latitude, or 45.508368287 degrees when GPS is not selected. Longitude is retained in metadata but does not enter this gravity calculation. Missing T/S must be supplied; they are not silently replaced by 35. This remains depth option 1. The added SIT-style profile option reproduces the recovered normal endpoint integration rule with explicit cast traversal; it is not a replacement for every native profile mask/offset/fallback.

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

Hydrostatic depth follows the integral of 10000/(rho*g) over sea pressure in dbar. Convert now offers TEOS-10 exact density with trapezoid integration of reciprocal density/gravity. GSW z_from_p returns height (negative underwater); depth=-z. Its basic P/latitude call does not automatically consume the observed fjord profile. Dynamic-height and surface-geopotential inputs are needed to include the corresponding corrections. Simply changing the function name to TEOS-10 is not a fjord correction.

Sources: [6], [7]. Native code: 0x0050BCF8, 0x0050CB5C, 0x0050CEA4; profile table 0x0050D374, integration 0x0050D1E0, interpolation 0x0050D024, retrieval 0x0050CD34. New profile findings are code traced; see evidence topic.

SELECTABLE IN CONVERT

Pressure only; SIT fixed position; UNESCO 1983 P/latitude; SIT-style EOS-80 endpoint profiling; GSW reference ocean (-z_from_p(P,latitude,0,0)); TEOS-10 trapezoid profiling.

Both profile options require at least two rows belonging to one continuous cast. Select forward/downcast or reverse/upcast traversal. New positive pressure maxima build knots; readings inside the accumulated range are linearly interpolated. The first positive knot extends to zero at its sample factor. Split repeated casts before conversion; a COUNT restart is rejected. The TEOS-10 factor is k_i=10000/(rho_exact_i*gsw_grav(latitude,P_i)), with z_i=z_previous+(P_i-P_previous)*(k_i+k_previous)/2 for later knots. This is hydrostatic numerical integration, not GSW dynamic-height processing. Missing surface water and coarse spacing remain limitations.

The EOS-80 depth modes do not become TEOS-10 when a TEOS-10 density column is selected. Select the depth method separately. The GSW reference-ocean option needs only P/latitude and does not use local S/T structure. GSW depth options are limited to 0..10000 dbar in Convert.

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

With complete S/T/P or C/T/P, the water-properties step offers EOS-80 in-situ anomaly, EOS-80 Sigma T, the older SD200W S/T anomaly, or TEOS-10 exact density plus sigma0. The default is the original EOS-80 anomaly. Existing original SIT density/sound columns can be retained; duplicate newly requested output columns are rejected. Source-salinity priority is controlled on the C page. Depth uses the density defined by its own selected method, not whichever anomaly column is displayed.

BENEFITS / ALTERNATIVES

EOS-80 keeps old datasets and SIT exports reproducible. Its pressure-dependent branch accounts for seawater compressibility, unlike using only surface density throughout a deep cast. It uses Practical Salinity and the legacy temperature convention, so input scales matter.

TEOS-10 uses Absolute Salinity and thermodynamically consistent relationships among density, heat and sound speed. The implemented path is SP -> SA, then gsw_rho_t_exact(SA,T90,P); CT is also exported. sigma0 is gsw_rho_t_exact(SA,gsw_pt0_from_t(SA,T90,P),0)-1000. SA is not numerically identical to SP; CT is not the measured in-situ temperature. Position/composition assumptions and the validity range must be documented. Run Convert separately from the original file for each method to compare named outputs; the export records the selected method.

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

SELECTABLE IN CONVERT

Original SIT, TEOS-10 exact Gibbs, Mackenzie 1981, Del Grosso 1974, or NPL/Leroy 2008. TEOS-10 uses gsw_sound_speed_t_exact(SA,T90,P); it is not the 75-term gsw_sound_speed fit. The classical acoustic alternatives are empirical equations, not TEOS-10 modes. Mackenzie and Del Grosso receive T68; NPL receives T90 and absolute latitude in this implementation. Mackenzie/NPL use the selected depth result, or internally derived UNESCO depth if pressure is retained. The acoustic-reference topic includes the complete implemented coefficients.

Converter bounds: Mackenzie S=25..40, T68=2..30 C, z=0..8000 m; Del Grosso S=30..40, T68=0..30 C, P=0..9806.65 dbar; NPL S=0..42, T90=-2..40 C, z=0..11000 m. Out-of-range rows stop conversion with a measurement number. These are operational guards, not a certificate of uncertainty across the whole range.

Sources: [9], [10]. Original code: 0x0050A8F0.

WORKED EXAMPLE

S=32.539, T=7.773 C and P=16.72 dbar give c=1478.82737409 m/s. The routine internally uses p=1.672 bar. Use P=16.72 in the reference-code function, which performs the division by ten itself.

## Oxygen: saturation and units

INPUT / OUTPUT

OX (SAIV205) and OxR (RINKO) are separate oxygen fields. Logger Convert assumes their reported values are percent saturation, not raw voltage or optical phase. It offers retaining the original and adding mg/L, mL/L, micromol/L, micromol/kg, or all four concentration units, independently for each oxygen field. Do not apply a raw-sensor calibration again.

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

Logger AP is in hPa: air_mmHg = AP*760/1013.25. A supplied positive AP overrides header AP; otherwise header AP is used. T/S come from measured fields, S calculated from C/T/P where needed, or explicitly supplied missing values. Missing oxygen cells stay empty. The added model path accepts oxygen percentages 0..300 and preserves missing oxygen cells. Input checks are not a declaration of scientific validity over the entire accepted range.

UNIT CONVERSIONS FOUND IN ORIGINAL SIT

mg/L -> mL/L: multiply by 22.391/31.998.
mg/L -> umol/L: multiply by 1000/31.998.
mg/L -> umol/kg: multiply by 22.391*1000/(716.467218*(rho/1000)).

Here rho is the density used by the selected native path, in kg/m^3. The mass-specific unit is different from per-litre units; reproduce the density convention as well as the constants. The mL value is a gas-equivalent amount under the convention embodied in the constant, not a volume of bubbles at sensor depth. Convert 1.4.7 offers all these units. Its SIT mass-unit option uses EOS-80 in-situ density, with zero sea pressure explicitly assumed where P is missing.

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

TRADEOFFS / SELECTABLE ALTERNATIVE

The current SIT equation keeps historical concentrations reproducible and explicitly uses measured air pressure. The optional GSW Garcia-Gordon path uses O2sol_SP_pt(SP,pt0) at 1013.25 hPa, multiplied by reported percent/100. This is micromol/kg; mg/L = micromol/kg * 31.998 * rho_in_situ / 1e6. It uses exact TEOS-10 density and does not apply the file AP to this fixed-atmosphere model. For mL/L it retains the SIT gas-equivalent factor. Sensor-specific raw pressure/response correction remains separate and is not added by this choice. Deep-water acceptance should compare against appropriate reference samples such as Winkler determinations and retain pressure/time history. Neither TEOS-10 nor any generic factor can recover missing calibration or undo an unknown firmware correction reliably.

Sources: [11], [12], [13], [14]. The solubility alternative is implemented in Convert; the sensor-processing references explain further work requiring sensor-specific inputs.

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

Native SD200W/SIT menus keep their original formulas. Convert 1.4.7 offers per-parameter methods, with a Quick guide button on each Next page. Choosing Fahrenheit alone does not enable TEOS-10.

WHAT A MODERN TEOS-10 PATH WOULD LOOK LIKE

SP = gsw_SP_from_C(C_mS_cm, T90_C, P_dbar)
SA = gsw_SA_from_SP(SP, P, longitude, latitude)
CT = gsw_CT_from_t(SA, T90, P)
rho = gsw_rho(SA, CT, P)
sound_speed = gsw_sound_speed(SA, CT, P)

This illustrates the GSW workflow. Convert uses exact-temperature Gibbs density/sound routines instead of the 75-term rho/sound_speed approximation shown here. Practical Salinity should still be retained as the conductivity-based observation. Absolute Salinity introduces composition information; Conservative Temperature supports heat-related calculations. Ocean atlases and standard-composition assumptions do not automatically characterize unusual local freshwater chemistry.

CHOICE BY PURPOSE

Historical SIT compatibility: retain the existing formulas and input conventions.
Oceanographic thermodynamic consistency: TEOS-10/GSW is the international framework to evaluate; preserve SP, SA, in-situ T and CT as distinct quantities.
Very low salinity: examine the modified Hill treatment and actual water composition, not just the C cutoff.
Pressure-to-depth in a stratified fjord: use a documented water-column density integration or dynamic-height correction, with sufficient profile coverage.
Acoustic work: compare SIT with appropriate GSW, Del Grosso, Mackenzie or NPL formulations within their domains and required uncertainty.
Oxygen: assess the solubility model and sensor-specific compensation separately; GSW oxygen is not an automatic deep-sensor correction.
Turbidity/fluorescence/PAR: use sensor calibration and optical/unit conventions; a seawater equation of state does not replace them.

BENEFITS AND COSTS

The legacy path provides continuity with existing measurements, calibrations and exports. A modern path can provide clearer conventions, published reference implementations and internally consistent water properties. It also needs explicit temperature scales, salinity type, position/reference assumptions and validation; results may change. Convert now writes method names, input temperature scale, salinity source, composition/position and reference assumptions into the exported metadata. Reopen the original input to compare another selection. Old native Compute tools can still recalculate their traditional quantities; use the named Convert columns and FIELDS export to identify the selected model.

THE EARLIER IMGUI COMPARISON

The archived reference document differed from SIT: its salinity expression omitted SIT's rt/Rp compensation; its oxygen conversion omitted barometric correction; it used Mackenzie sound speed; and it did not represent all density modes. For C=30, T=10, P=100 it gave S=23.55343140 versus SIT's 26.82414973. Those differences were not evidence that TEOS-10 was implemented there. The working document was subsequently corrected to SIT; the archived comparison describes that earlier document, not a blanket claim about today's Studio executable.

Sources: [1]-[3], [5]-[14]; local historical comparison: sd200DOc/KONVERTERING_SAMMENLIGNING.md.

CONVERT WORKFLOW

1. Select the source in Convert CSV/TXT. Each parameter has its own Next page and Quick guide button.
2. Choose salinity, temperature display/scale, pressure/depth and oxygen methods. Keep original fields checked unless an intentional export omits them.
3. Review sound speed and density on Derived seawater properties.
4. Supply missing supporting T/SP/AP, state the temperature scale, and review reference composition or geographic atlas plus position. The input P must already be sea pressure.
5. Convert, inspect the named columns, then Export all fields. The input file is not overwritten. Saved choices include model selections; supporting values and GPS are reviewed again for a new file.

Modern GSW water-property conversion is guarded to SP=0..42, T90=-2..40 C, sea pressure=0..10000 dbar. The exact Gibbs implementation avoids the 75-term approximation's funnel extrapolation, but bounds alone do not establish that an unusual water chemistry follows the seawater model. Missing P for oxygen is treated as zero sea pressure and recorded; provide measured P when pressure-dependent density or potential temperature is needed.

WORKED EXAMPLE: SELECTED MODERN METHODS

Keep SP=32.539 as the salinity input. State T=7.773 C as ITS-90, P=16.72 dbar, Reference Composition and default latitude 45.508368287 degrees. Select TEOS-10 density/sound, GSW reference-ocean depth and GSW oxygen. Then:
SA=32.539*35.16504/35=32.6924353303 g/kg.
CT=7.8002598247 C; rho_exact=1025.4523106389 kg/m^3.
sigma0=25.3758362050 kg/m^3; sound_exact=1478.7704342732 m/s.
Depth=-z_from_p(16.72,45.508368287,0,0)=16.5828510084 m.
At 3.47%: oxygen=10.1876592416 micromol/kg = 0.3342817848 mg/L.
This oxygen example uses the GSW standard-atmosphere reference, not the 925 hPa SIT example. Their difference combines different reference conditions and solubility models; it must not be presented as a pure accuracy improvement. C-derived SP can also differ if ITS-90 is applied where the legacy example passed temperature unchanged. Keep the input convention fixed when comparing methods.

Exact-temperature reference documentation:
https://www.teos-10.org/pubs/gsw/html/gsw_rho_t_exact.html
https://www.teos-10.org/pubs/gsw/html/gsw_sound_speed_t_exact.html
https://www.teos-10.org/pubs/gsw/html/gsw_pt0_from_t.html

Library: bundled GSW-C V3.06 source, preserved without changes from the project's vendor copy. Source-file hashes are in sit_import/vendor/gsw/SIT_SOURCE_MANIFEST.json; full redistribution terms are included in the offline GSW licence topic. The acoustic-reference topic is the actual C++ wrapper source, including the original 1974 Del Grosso coefficients (not the ITS-90 coefficient refit). For an independently maintained coefficient implementation see https://github.com/pyoceans/python-oceans/blob/main/oceans/sw_extras/sw_extras.py .

## Verification and sources

LOCAL EVIDENCE

The legacy core was reconstructed from the executable, not original Delphi source. The guide/model update preserves native measurement/calibration/communications code; new calculations run in the Convert module. Addresses in these topics assume image base 0x00400000; relocated instances require the corresponding relative address.

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
