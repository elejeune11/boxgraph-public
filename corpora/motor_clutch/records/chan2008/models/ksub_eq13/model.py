# Eq. 13: κsub = π E δ / (1 + υ). Pa * nm = 1e-9 N/m = 1e-6 pN/nm.
import math


def run(inputs, settings):
    return {"ksub": math.pi * inputs["E"] * inputs["L"] * 1e-6 / (1.0 + inputs["nu"])}


def symbolic():
    import sympy as sp
    E, L, nu = sp.symbols("E L nu", positive=True)
    return {"ksub": sp.pi * E * L * sp.Rational(1, 10**6) / (1 + nu)}
