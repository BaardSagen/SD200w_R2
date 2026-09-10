"""Apply the model release additions to the completed guide-only source once."""
from pathlib import Path
R=Path(__file__).resolve().parent.parent
p=R/'docs/SIT_CONVERSIONS_AND_FORMULAS.md'
s=p.read_text(encoding='utf-8')
replacements={
'SIT 1.4.6. Reviewed 10 September 2026. This guide documents calculations; it does not change them.':'SIT 1.4.7. Reviewed 10 September 2026. The native SD200W routines are preserved; Convert now offers explicitly selected alternatives.',
'SIT retains the original SD200W calculation methods: PSS-78 Practical Salinity, EOS-80 density, a UNESCO-family sound-speed polynomial and several pressure-to-depth methods. TEOS-10 is not used in these calculation paths. Modern alternatives below are comparisons and possible future work, not selectable features in this release.':'The original SD200W routines use PSS-78 Practical Salinity, EOS-80 density, a UNESCO-family sound-speed polynomial and several depth methods. Those native routines do not use TEOS-10. In SIT 1.4.7, the Convert wizard additionally offers GSW/TEOS-10 and named alternative methods. The choice applies to Convert outputs; it does not change the native calibration tools or the old Compute/recalculation menus.',
'3. The added logger Convert wizard handles FIELDS/Full data, offers additional columns and calls the original SIT salinity, sound-speed, density and gravity routines. Its oxygen equation reproduces the original normal equation, but its missing-input rules differ from the old wrapper.':'3. Convert handles FIELDS/Full logger data and CTD/STD text with a declared Date/Time and whole-second Interval. It offers both native routines and named new models. Legacy row times are reconstructed from the header and sequence order and labelled accordingly. Original File > Import dispatch remains separate.',
'Requesting C-to-S with an existing S field adds S_from_C; it does not replace S as the input to the other derived columns.':'Requesting C-to-S with an existing S field adds S_from_C. By default S still supplies dependent calculations; the checkbox "Use this calculated salinity" explicitly changes that priority.',
'Logger Convert passes the stored Celsius value directly to the native routine. No new scale correction has been inserted.':'The default "As recorded" choice passes stored Celsius directly, reproducing legacy SIT. Choosing ITS-90 sends T90*1.00024 to legacy PSS-78/EOS-80/sound equations. Choosing IPTS-68 sends T68/1.00024 to modern equations. Modern selections require an explicit scale; the file date alone does not establish it.',
'A possible modern path derives CT from SA, ITS-90 temperature and pressure; it must preserve the measured temperature and identify the new quantity.':'The TEOS-10 path adds separately named SA and CT columns from SP, ITS-90 temperature and pressure. Original T is retained by default.',
'This logger path does not implement the native Profiling mode.':'This remains depth option 1. The added SIT-style profile option reproduces the recovered normal endpoint integration rule with explicit cast traversal; it is not a replacement for every native profile mask/offset/fallback.',
'A possible upgrade uses TEOS-10 density/specific volume and documented numerical integration.':'Convert now offers TEOS-10 exact density with trapezoid integration of reciprocal density/gravity.',
'When complete CTD inputs exist, Density_anomaly_SIT_kg_m3 is calculated with the native pressure-dependent EOS-80 routine. Existing derived fields are retained rather than overwritten. S takes precedence over an independently requested S_from_C column. Real depth uses the full in-situ density, not merely its anomaly.':'With complete S/T/P or C/T/P, the water-properties step offers EOS-80 in-situ anomaly, EOS-80 Sigma T, the older SD200W S/T anomaly, or TEOS-10 exact density plus sigma0. The default is the original EOS-80 anomaly. Existing original SIT density/sound columns can be retained; duplicate newly requested output columns are rejected. Source-salinity priority is controlled on the C page. Depth uses the density defined by its own selected method, not whichever anomaly column is displayed.',
'A possible path is SP -> SA, T90 -> CT, then gsw_rho(SA,CT,P), or an appropriate exact-temperature routine.':'The implemented path is SP -> SA, then gsw_rho_t_exact(SA,T90,P); CT is also exported. sigma0 is gsw_rho_t_exact(SA,gsw_pt0_from_t(SA,T90,P),0)-1000.',
'Keeping both legacy and explicitly named TEOS-10 columns would allow comparison without erasing provenance.':'Run Convert separately from the original file for each method to compare named outputs; the export records the selected method.',
'It offers retaining the original and converting either field to mg/L, mL/L, or both.':'It offers retaining the original and adding mg/L, mL/L, micromol/L, micromol/kg, or all four concentration units, independently for each oxygen field.',
'The newer logger wizard does not offer the two micromole outputs.':'Convert 1.4.7 offers all these units. Its SIT mass-unit option uses EOS-80 in-situ density, with zero sea pressure explicitly assumed where P is missing.',
'TRADEOFFS / POSSIBLE FUTURE WORK':'TRADEOFFS / SELECTABLE ALTERNATIVE',
'A modern optional path could add named Garcia-Gordon/GSW outputs, explicit reference conditions, unit/density conventions and documented sensor corrections where raw information is available.':'The optional GSW Garcia-Gordon path uses O2sol_SP_pt(SP,pt0) at 1013.25 hPa, multiplied by reported percent/100. This is micromol/kg; mg/L = micromol/kg * 31.998 * rho_in_situ / 1e6. It uses exact TEOS-10 density and does not apply the file AP to this fixed-atmosphere model. For mL/L it retains the SIT gas-equivalent factor. Sensor-specific raw pressure/response correction remains separate and is not added by this choice.',
'Sources: [11], [12], [13], [14]. These describe alternatives; they are not implemented by this guide update.':'Sources: [11], [12], [13], [14]. The solubility alternative is implemented in Convert; the sensor-processing references explain further work requiring sensor-specific inputs.',
'SIT uses its original PSS-78/EOS-80 and associated legacy formulas. It does not currently offer a TEOS-10 switch. Choosing Fahrenheit or "Real depth" does not enable TEOS-10.':'Native SD200W/SIT menus keep their original formulas. Convert 1.4.7 offers per-parameter methods, with a Quick guide button on each Next page. Choosing Fahrenheit alone does not enable TEOS-10.',
'This is a proposed comparison workflow, not executable SIT code.':'This illustrates the GSW workflow. Convert uses exact-temperature Gibbs density/sound routines instead of the 75-term rho/sound_speed approximation shown here.',
'A sensible future design would offer separately named legacy and modern outputs with calculation metadata, rather than silently rewriting old datasets.':'Convert now writes method names, input temperature scale, salinity source, composition/position and reference assumptions into the exported metadata. Reopen the original input to compare another selection. Old native Compute tools can still recalculate their traditional quantities; use the named Convert columns and FIELDS export to identify the selected model.',
'The guide update preserves measurement/calibration/communications code.':'The guide/model update preserves native measurement/calibration/communications code; new calculations run in the Convert module.',
}
for old,new in replacements.items():
 if old not in s:raise SystemExit('Missing replacement: '+old[:100])
 s=s.replace(old,new)
where='BENEFITS / ALTERNATIVES\n\nKeeping PSS-78'
s=s.replace(where,'SELECTABLE IN CONVERT\n\nOn C, keep conductivity, use original SIT PSS-78, use GSW PSS-78 with modified Hill below SP=2, or add both GSW SP and TEOS-10 SA. On an S-only input, retain SP and optionally add SA/CT. SA never replaces the meaning of S. The final page chooses Reference Composition (SA=SP*35.16504/35) or the geographic GSW atlas; the latter requires an actual supplied position. Reference Composition is an explicit approximation where no composition anomaly is supplied.\n\n'+where)
where='WORKED EXAMPLE: TWO DEPTH METHODS'
s=s.replace(where,'''SELECTABLE IN CONVERT

Pressure only; SIT fixed position; UNESCO 1983 P/latitude; SIT-style EOS-80 endpoint profiling; GSW reference ocean (-z_from_p(P,latitude,0,0)); TEOS-10 trapezoid profiling.

Both profile options require at least two rows belonging to one continuous cast. Select forward/downcast or reverse/upcast traversal. New positive pressure maxima build knots; readings inside the accumulated range are linearly interpolated. The first positive knot extends to zero at its sample factor. Split repeated casts before conversion; a COUNT restart is rejected. The TEOS-10 factor is k_i=10000/(rho_exact_i*gsw_grav(latitude,P_i)), with z_i=z_previous+(P_i-P_previous)*(k_i+k_previous)/2 for later knots. This is hydrostatic numerical integration, not GSW dynamic-height processing. Missing surface water and coarse spacing remain limitations.

The EOS-80 depth modes do not become TEOS-10 when a TEOS-10 density column is selected. Select the depth method separately. The GSW reference-ocean option needs only P/latitude and does not use local S/T structure.

'''+where)
where='Sources: [9], [10]. Original code: 0x0050A8F0.'
s=s.replace(where,'''SELECTABLE IN CONVERT

Original SIT, TEOS-10 exact Gibbs, Mackenzie 1981, Del Grosso 1974, or NPL/Leroy 2008. TEOS-10 uses gsw_sound_speed_t_exact(SA,T90,P); it is not the 75-term gsw_sound_speed fit. The classical acoustic alternatives are empirical equations, not TEOS-10 modes. Mackenzie and Del Grosso receive T68; NPL receives T90 and absolute latitude in this implementation. Mackenzie/NPL use the selected depth result, or internally derived UNESCO depth if pressure is retained. The acoustic-reference topic includes the complete implemented coefficients.

Converter bounds: Mackenzie S=25..40, T68=2..30 C, z=0..8000 m; Del Grosso S=30..40, T68=0..30 C, P=0..9806.65 dbar; NPL S=0..42, T90=-2..40 C, z=0..11000 m. Out-of-range rows stop conversion with a measurement number. These are operational guards, not a certificate of uncertainty across the whole range.

'''+where)
s=s.replace('## Verification and sources','''CONVERT WORKFLOW

1. Select the source in Convert CSV/TXT. Each parameter has its own Next page and Quick guide button.
2. Choose salinity, temperature display/scale, pressure/depth and oxygen methods. Keep original fields checked unless an intentional export omits them.
3. Review sound speed and density on Derived seawater properties.
4. Supply missing supporting T/SP/AP, state the temperature scale, and review reference composition or geographic atlas plus position. The input P must already be sea pressure.
5. Convert, inspect the named columns, then Export all fields. The input file is not overwritten. Saved choices include model selections; supporting values and GPS are reviewed again for a new file.

Modern GSW water-property conversion is guarded to SP=0..42, T90=-2..40 C, sea pressure=0..10000 dbar. The exact Gibbs implementation avoids the 75-term approximation's funnel extrapolation, but bounds alone do not establish that an unusual water chemistry follows the seawater model. Missing P for oxygen is treated as zero sea pressure and recorded; provide measured P when pressure-dependent density or potential temperature is needed.

## Verification and sources''')
p.write_text(s,encoding='utf-8')
generator=(R/'analysis/generate_formula_guide146.py').read_text().replace('146','147')
generator=generator.replace("out=['// Generated", "science=(R/'sit_import/science.h').read_text()\nstart=science.index('inline double mackenzie')\nend=science.rfind('\\n}\\n#endif')\ntopics.append(('Reference: acoustic alternatives', 'Complete C++ functions used by Convert. S=SP; temperature and pressure/depth conventions appear in each function.\\n\\n'+science[start:end]))\ntopics.append(('GSW licence', (R/'sit_import/vendor/gsw/LICENSE').read_text(encoding='utf-8')))\nout=['// Generated")
(R/'analysis/generate_formula_guide147.py').write_text(generator)
