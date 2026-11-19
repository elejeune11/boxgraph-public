# Eq. 8, balloon normalization: M-hat = pi [kappa-hat - kappa-hat^3 / (8 (alpha^2 + p-hat/3))]
import math


def run(inputs, settings):
    k, p, a = inputs["khat"], inputs["phat"], inputs["alpha"]
    return {"Mhat": math.pi * (k - k**3 / (8 * (a**2 + p / 3)))}


def symbolic():
    import sympy as sp
    khat, phat, alpha = sp.symbols("khat phat alpha", positive=True)
    return {"Mhat": sp.pi * (khat - khat**3 / (8 * (alpha**2 + phat / 3)))}
