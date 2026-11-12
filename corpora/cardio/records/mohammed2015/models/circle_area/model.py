import math


def run(inputs, settings):
    d = inputs["d"]
    return {"A": math.pi * d * d / 4.0}


def symbolic():
    import sympy as sp
    d = sp.symbols("d", positive=True)
    return {"A": sp.pi * d**2 / 4}
