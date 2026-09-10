# Coefficients (coef_tbl1) ? meaning and mapping

This document explains the ASCII coefficient table `coef_tbl1` embedded in `SD49INIT.ASM` and how it maps to binary coefficient storage (cobin_*) used by the math routines.

For the source-verified conductivity, temperature, pressure, salinity and
sound-speed equations, see [SD208 calculations and drift compensation](sd208-beregninger-og-drift.md).
That review supersedes the tentative coefficient roles below: CA/CB define
the conductivity resistance model; LA/LB/LC are conductivity drift terms,
alongside Z1/Z2/Z3 and H1/H2/H3/HA/HB/HC. They are not optional-sensor
calibration coefficients in this calculation path. X1-X4 are used by ox_mvolt for the SAIV205 oxygen input, despite the pressure-sensor comment in the initial coefficient table.

## Overview

- The table is a comma?separated list of key=value tokens, where the key is 2 characters (sometimes 1 letter + index) and value is a signed floating?point in scientific notation.
- On cold start, `ram_init` copies these ASCII bytes into XDATA and the conversion routine (`coeff_conv` in SD49CONV.ASM) parses them to binary floating?point into `cobin_*` locations.
- EEPROM persistence: `eeset_coeff` writes selected blocks to EEPROM; `eepre_coeff` restores.

## Groups and likely usage

- Temperature (A1, B1, C1, D1)
  - Likely 3rd/4th order polynomial for temperature sensor conversion.
- Pressure (A2..G2, plus X1..X4 from Keller)
  - High?order polynomial and sensor?specific transfer (X1..X4) for pressure sensor curve and compensation.
- Conductivity (A3..C3, BA) and temperature coefficients (Z1..Z3, CB)
  - Conductivity scaling and temperature dependence.
- Turbidity ranges L/M/H/V (AT/BT/CT/DT repeated per range)
  - Four calibrated ranges; each has 4 coefficients.
- Fluorescence ranges L/M/H/V (AF/BF/CF/DF)
  - Similar 4?coefficient sets per range.
- Oxygen mV offset/scale (V) and optional sensor scalars (LA/LB/LC/CA)
  - `V` is a reference; LA/LB/LC/CA likely optional sensor calibration.
- Polynomial drift compensation (K..Q with 0,1,2,3 suffixes)
  - Used in pressure `mat_comp` with Horner form; K0..Q0 are constants; K1..Q3 are terms.
- Oxygen calibration multi?point (AO..HO, BO/FO=1.0 default scales)
  - Defaults indicate identity scaling until user calibration.

## Mapping to binary variables (indicative)

- SD49CONV.ASM converts tokens to these binary symbols: `cobin_*`, `factor_*`, `rb_kald`, etc.
- Example flows:
  - `co_a1`..`co_d1` ? temperature curve constants.
  - `co_a2`..`co_g2` + `co_x1`..`co_x4` ? pressure/transfer.
  - `co_a3`..`co_c3` + `co_ba` ? conductivity scaling.
  - `ctl_*`, `ctm_*`, `cth_*`, `ctv_*` ? turbidity ranges.
  - `cfl_*`, `cfm_*`, `cfh_*`, `cfv_*` ? fluorescence ranges.
  - `co_K*`..`co_Q*`, `co_K0`..`co_Q0` ? pressure drift compensation.
  - `co_z*`, `co_cb` ? conductivity temperature coefficients.
  - `co_la/lb/lc/ca` ? optional sensor calibration.
  - `co_AO`..`co_HO`, `co_BO/FO` ? oxygen calibration.

## What?s missing / to confirm

- Formal definitions and units for each key.
- Which ADC channel and engineering unit each coefficient applies to.
- The exact equation forms (we have partial inference from SD48MAT.ASM).

## Proposed next steps

- Extract and tabulate `co_*` ? `cobin_*` destinations from SD49CONV.ASM.
- From SD48MAT.ASM, list equations and identify which coefficients are used in each formula.
- Produce a per?sensor table: ADC channel ? equation ? coefficients ? units.
