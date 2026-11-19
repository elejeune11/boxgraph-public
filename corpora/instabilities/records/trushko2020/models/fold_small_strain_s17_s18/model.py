import math

# Eqs. S17-S18 as printed; delta is taken in units of R (the derivation and the numerics set
# R = 1) and alpha in radians, converted to degrees for the port.


def run(inputs, settings):
    d = inputs["Delta"] / inputs["n"]
    return {"delta_over_R": 4.0 * 2.5 ** (1.0 / 3.0) * d ** (2.0 / 3.0),
            "alpha": math.degrees(0.4 ** (1.0 / 3.0) * d ** (1.0 / 3.0))}


def symbolic():
    import sympy as sp
    D, n = sp.symbols("Delta n", positive=True)
    return {"delta_over_R": 4 * sp.Rational(5, 2) ** sp.Rational(1, 3) * (D / n) ** sp.Rational(2, 3),
            "alpha": 180 / sp.pi * sp.Rational(2, 5) ** sp.Rational(1, 3) * (D / n) ** sp.Rational(1, 3)}
