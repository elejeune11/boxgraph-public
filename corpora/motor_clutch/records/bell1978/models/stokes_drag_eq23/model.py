import math


def run(inputs, settings):
    return {"drag": 6 * math.pi * inputs["eta"] * inputs["r"] * 1e-4}  # um -> cm


def symbolic():
    import sympy as sp
    eta, r = sp.symbols("eta r", positive=True)
    return {"drag": 6 * sp.pi * eta * r * sp.Rational(1, 10**4)}
