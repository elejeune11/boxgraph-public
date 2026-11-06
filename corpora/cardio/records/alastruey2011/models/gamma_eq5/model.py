import math


def run(inputs, settings):
    return {"Gamma": 2.0 / 3.0 * math.sqrt(math.pi) * inputs["phi"] * inputs["h"]}


def symbolic():
    import sympy as sp
    phi, h = sp.symbols("phi h", positive=True)
    return {"Gamma": sp.Rational(2, 3) * sp.sqrt(sp.pi) * phi * h}
