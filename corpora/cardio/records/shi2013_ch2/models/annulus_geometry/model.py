# The text gives a diameter, a thickness and a density, then "a sectional area" and "a mass".
# Read as a circular disc of that diameter (area) and that area times thickness times density (mass).
import math


def run(inputs, settings):
    d_m = inputs["d"] * 1e-3
    h_m = inputs["h"] * 1e-3
    A = math.pi * d_m ** 2 / 4.0
    return {"A": A, "m": inputs["rho"] * A * h_m}


def symbolic():
    import sympy as sp
    d, h, rho = sp.symbols("d h rho", positive=True)
    A = sp.pi * (d * sp.Rational(1, 1000)) ** 2 / 4
    return {"A": A, "m": rho * A * h * sp.Rational(1, 1000)}
