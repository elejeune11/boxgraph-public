# Eq. 16 (p. 15): A0 = Ad (1 - sqrt(Ad) Pd / beta)^2, with beta = (4/3) sqrt(pi) E h (Eq. 3). SI units.
import math


def run(inputs, settings):
    beta = 4.0 / 3.0 * math.sqrt(math.pi) * inputs["E"] * inputs["h"]
    Ad = inputs["Ad"]
    return {"A0": Ad * (1.0 - math.sqrt(Ad) * inputs["Pd"] / beta) ** 2}


def symbolic():
    import sympy as sp
    Ad, Pd, E, h = sp.symbols("Ad Pd E h", positive=True)
    beta = sp.Rational(4, 3) * sp.sqrt(sp.pi) * E * h
    return {"A0": Ad * (1 - sp.sqrt(Ad) * Pd / beta) ** 2}
