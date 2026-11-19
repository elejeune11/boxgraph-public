# Eq. 8 as printed.
import math


def run(inputs, settings):
    return {"lamC_over_H": 2.0 * math.pi * (inputs["mu_ratio"] / 3.0) ** (1.0 / 3.0)}


def symbolic():
    import sympy as sp
    mu_ratio = sp.symbols("mu_ratio", positive=True)
    return {"lamC_over_H": 2 * sp.pi * (mu_ratio / 3) ** sp.Rational(1, 3)}
