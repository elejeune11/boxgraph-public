import math


def run(inputs, settings):
    return {"area": 4 * math.pi * inputs["r"] ** 2}


def symbolic():
    import sympy as sp
    r = sp.symbols("r", positive=True)
    return {"area": 4 * sp.pi * r**2}
