import math


def run(inputs, settings):
    n, nu = inputs["n"], inputs["nu"]
    return {"delta": 1.0 / (1.0 + n), "N": -2.0 * (n + 2.0) * math.pi * nu}


def symbolic():
    import sympy as sp
    n, nu = sp.symbols("n nu", positive=True)
    return {"delta": 1 / (1 + n), "N": -2 * (n + 2) * sp.pi * nu}
