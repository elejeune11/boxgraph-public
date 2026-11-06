import math


def run(inputs, settings):
    r = inputs["d"] / 10.0 / 2.0  # cm
    return {"K": 8.0 * inputs["mu"] / (math.pi * r**4)}


def symbolic():
    import sympy as sp
    d, mu = sp.symbols("d mu", positive=True)
    r = d / 20
    return {"K": 8 * mu / (sp.pi * r**4)}
