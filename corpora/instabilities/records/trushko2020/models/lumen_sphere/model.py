import math


def run(inputs, settings):
    R = inputs["R"] * 1e-6
    return {"V": 4.0 / 3.0 * math.pi * R ** 3, "A": 4.0 * math.pi * R ** 2}


def symbolic():
    import sympy as sp
    R = sp.symbols("R", positive=True)
    r = R * sp.Rational(1, 10 ** 6)
    return {"V": sp.Rational(4, 3) * sp.pi * r ** 3, "A": 4 * sp.pi * r ** 2}
