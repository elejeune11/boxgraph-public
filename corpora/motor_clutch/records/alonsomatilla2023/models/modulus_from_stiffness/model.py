# E_s = 9 kappa_s / (2 pi d_s): the inverse of legend E. pN/um / nm -> kPa (factor 1).
import math


def run(inputs, settings):
    return {"E": 9 * inputs["ks"] / (2 * math.pi * inputs["d"])}


def symbolic():
    import sympy as sp
    d, ks = sp.symbols("d ks", positive=True)
    return {"E": 9 * ks / (2 * sp.pi * d)}
