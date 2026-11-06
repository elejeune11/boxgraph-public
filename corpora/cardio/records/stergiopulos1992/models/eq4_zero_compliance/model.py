"""Pressure at which the quadratic wall law (Eq. 4) with the coefficients from Eq. 9 stops being compliant.

Eq. 4: A = A0 [1 + C0'(p - p0) + C1'(p - p0)^2], with C0' = K/p0 and C1' = -K/(2 p0^2) (p. 3).
dA/dp = A0 [C0' + 2 C1'(p - p0)] = A0 (K/p0^2)(2 p0 - p), which is zero at p = 2 p0 and negative above.
"""


def run(inputs, settings):
    return {"p_star": 2.0 * inputs["p0"]}


def symbolic():
    import sympy as sp

    p0 = sp.symbols("p0", positive=True)
    return {"p_star": 2 * p0}
