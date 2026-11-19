import math


def run(inputs, settings):
    F_sp = inputs["F_cs"] * 1e-6 * inputs["n_cells"] / math.pi     # N
    R = inputs["R"] * 1e-6
    return {"P": F_sp / (4.0 * math.pi * R ** 2)}


def symbolic():
    import sympy as sp
    F, n, R = sp.symbols("F_cs n_cells R", positive=True)
    return {"P": F * sp.Rational(1, 10 ** 6) * n / sp.pi / (4 * sp.pi * (R * sp.Rational(1, 10 ** 6)) ** 2)}
