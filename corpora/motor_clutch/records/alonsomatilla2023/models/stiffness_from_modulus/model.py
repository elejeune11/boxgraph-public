# kappa_s = 2 pi d E / 9. nm * kPa = 1e-9 m * 1e3 N/m^2 = 1e-6 N/m = 1 pN/um.
import math


def run(inputs, settings):
    return {"ks": 2 * math.pi * inputs["d"] * inputs["E"] / 9}


def symbolic():
    import sympy as sp
    d, E = sp.symbols("d E", positive=True)
    return {"ks": 2 * sp.pi * d * E / 9}
