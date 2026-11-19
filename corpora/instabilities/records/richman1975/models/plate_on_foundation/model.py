"""Two bonded incompressible thin plates (strata 1 over 2) on an incompressible elastic half-space.

All moduli are in units of E1; lengths in mm. The plate modulus of an incompressible plate is
E/(1 - nu^2) = 4E/3. A half-space with nu = 1/2 resists a surface undulation of wavenumber k with
pressure (2/3) Ecore k w, whether its surface is free of shear or held by an inextensible plate.
Equibiaxial membrane force makes the critical load depend only on |k| = 2 pi / l.
"""

import math


def _critical(t1, t2, e2, ec):
    b1, b2 = 4.0 / 3.0, 4.0 / 3.0 * e2
    # z measured from the bottom of stratum 2: stratum 2 on [0, t2], stratum 1 on [t2, t2 + t1]
    zn = (b2 * t2 * t2 / 2 + b1 * t1 * (t2 + t1 / 2)) / (b2 * t2 + b1 * t1)
    d = b2 * ((t2 - zn) ** 3 - (0 - zn) ** 3) / 3 + b1 * ((t2 + t1 - zn) ** 3 - (t2 - zn) ** 3) / 3
    kf = 2.0 / 3.0 * ec  # foundation: p = kf * k * w
    k = (kf / (2 * d)) ** (1.0 / 3.0)  # dN/dk = 2 D k - kf / k^2 = 0
    n = d * k * k + kf / k
    return k, n


def run(inputs, settings):
    t1, t2 = inputs["t1"], inputs["t2"]
    k, n = _critical(t1, t2, inputs["E2_over_E1"], inputs["Ecore_over_E1"])
    l_over_t = 2 * math.pi / k / (t1 + t2)
    load = t1 + inputs["stress_ratio"] * t2
    sigma = n / load if load > 0 else float("nan")
    return {"l_over_t": l_over_t, "sigma1_crit_over_E1": sigma}
