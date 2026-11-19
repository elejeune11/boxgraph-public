import math


def run(inputs, settings):
    return {"l0": 2.0 * math.pi * inputs["R"] / inputs["lam"]}


def symbolic():
    import sympy as sp
    R, lam = sp.symbols("R lam", positive=True)
    return {"l0": 2 * sp.pi * R / lam}
