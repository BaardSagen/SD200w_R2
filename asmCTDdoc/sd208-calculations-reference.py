"""Numerical reference for the reviewed SD208 legacy firmware equations.

This is not an 8051 emulator or a serial driver. Inputs are internal values,
before serial formatting. Use the actual instrument's calibration coefficients.
Run with Python 3 to print reproducible calculation examples.
"""

import math


def conductivity_from_raw(n, a3, b3, c3):
    """Processed raw conductivity N -> calibrated conductivity [mS/cm]."""
    return a3 + b3 * n + c3 * n * n


def conductivity_from_module(m, rb, rb_reference, coefficients):
    """Internal module reply -> (processed raw N, conductivity [mS/cm]).

    rb and rb_reference are resistance values, not temperatures in deg C.
    coefficients must contain BA, CA, CB, Z1..Z3, LA..LC, H1..H3,
    HA..HC and A3..C3. The >100 gate follows the assembly's comparison
    branches. Nonfinite inputs are rejected here, not emulated as firmware.
    """
    if not all(math.isfinite(v) for v in (m, rb, rb_reference)):
        raise ValueError("Nonfinite input")
    if m <= 100:
        return 0.0, 0.0
    k = coefficients
    resistance = math.exp(k["CA"] + k["CB"] * math.log(m))
    n0 = k["BA"] * 10_000_000.0 / resistance
    if rb > rb_reference:
        amplitude = k["H1"] + k["H2"] * n0 + k["H3"] * n0**2
        thermal = k["HA"] + k["HB"] * rb + k["HC"] * rb**2
    else:
        amplitude = k["Z1"] + k["Z2"] * n0 + k["Z3"] * n0**2
        thermal = k["LA"] + k["LB"] * rb + k["LC"] * rb**2
    n = n0 + amplitude * thermal
    return n, conductivity_from_raw(n, k["A3"], k["B3"], k["C3"])


def polynomial(x, coefficients):
    """Coefficients in ascending powers; evaluation order need not match MCU."""
    return sum(coefficient * x**power
               for power, coefficient in enumerate(coefficients))


def salinity(c_ms_cm, t, p_dbar):
    """Firmware PSS-78 calculation; uses t directly, no ITS-90 conversion.

    No Hill low-salinity extension. No clipping of negative calculated S.
    The firmware special-cases nonpositive conductivity to zero salinity.
    """
    if c_ms_cm <= 0:
        return 0.0
    r = c_ms_cm * 0.023302418  # Actual stored constant, not exactly 1/42.914.
    rt35 = polynomial(t, (0.6766097, 0.0200564, 0.0001104259,
                          -6.9698e-7, 1.0031e-9))
    ax = 0.4215 - 0.003107 * t
    bx = 1 + 0.03426 * t + 0.0004464 * t**2
    cx = p_dbar * (2.07e-5 - 6.37e-10 * p_dbar + 3.989e-15 * p_dbar**2)
    x = math.sqrt(r / (rt35 * (1 + cx / (bx + ax * r))))
    base = polynomial(x, (0.008, -0.1692, 25.3851, 14.0941, -7.0261, 2.7081))
    correction = polynomial(x, (0.0005, -0.0056, -0.0066,
                                -0.0375, 0.0636, -0.0144))
    return base + (t - 15) / (1 + 0.0162 * (t - 15)) * correction


# fp_l1..fp_l42 from SD48MAT1.ASM, expressed as their intended decimal values.
# The ASM's literal doubles can differ by ~1 ULP from these decimal literals.
L = (
    1402.388, 5.03711, -5.80852e-2, 3.3420e-4, -1.47800e-6, 3.1464e-9,
    0.153563, 6.8982e-4, -8.1788e-6, 1.3621e-7, -6.1185e-10,
    3.1260e-5, -1.7107e-6, 2.5974e-8, -2.5335e-10, 1.0405e-12,
    -9.7729e-9, 3.8504e-10, -2.3643e-12,
    1.389, -1.262e-2, 7.164e-5, 2.006e-6, -3.21e-8,
    9.4742e-5, -1.2580e-5, -6.4885e-8, 1.0507e-8, -2.0122e-10,
    -3.9064e-7, 9.1041e-9, -1.6002e-10, 7.988e-12,
    1.100e-10, 6.649e-12, -3.389e-13,
    -1.922e-2, -4.42e-5, 7.3637e-5, 1.7945e-7, 1.727e-3, -7.9836e-6,
)


def sound_velocity(s, t, p_dbar):
    """Firmware's Chen/Millero-form calculation [m/s], with legacy constants."""
    p = p_dbar * 0.1
    x = (polynomial(t, L[0:6]) + polynomial(t, L[6:11]) * p
         + polynomial(t, L[11:16]) * p**2 + polynomial(t, L[16:19]) * p**3)
    y = (polynomial(t, L[19:24]) + polynomial(t, L[24:29]) * p
         + polynomial(t, L[29:33]) * p**2 + polynomial(t, L[33:36]) * p**3)
    z = L[36] + L[37] * t + (L[38] + L[39] * t) * p
    w = L[40] + L[41] * p
    return x + y * s + z * math.sqrt(s * s * s) + w * s * s


if __name__ == "__main__":
    print("Firmware equation examples; not measurements from an instrument")
    for n in (100000, 300000, 400000, 600000):
        c = conductivity_from_raw(n, 4.4712882942e-5,
                                  9.8257908671e-5, 9.9933004820e-13)
        print(f"N={n}, N/10000={n/10000:.1f}, C={c:.10f} mS/cm")
    for c, t, p in ((42.914, 15, 0), (40, 10, 1000), (0, 15, 0)):
        s = salinity(c, t, p)
        v = sound_velocity(s, t, p)
        print(f"C={c}, T={t}, P={p}: S={s:.10f}, sound={v:.10f} m/s")
