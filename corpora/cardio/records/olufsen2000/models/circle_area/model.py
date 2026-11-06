import math


def run(inputs, settings):
    return {"A": math.pi * inputs["R"] ** 2}


def symbolic():
    import sympy as sp
    R = sp.symbols("R", positive=True)
    return {"A": sp.pi * R ** 2}
