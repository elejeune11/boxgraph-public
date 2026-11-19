import math


def run(inputs, settings):
    kf = inputs["kf"]
    return {"P": 2.0 * math.sqrt(kf), "lam": 2.0 * math.pi * kf ** -0.25}


def symbolic():
    import sympy as sp
    kf = sp.symbols("kf", positive=True)
    return {"P": 2 * sp.sqrt(kf), "lam": 2 * sp.pi * kf ** sp.Rational(-1, 4)}
