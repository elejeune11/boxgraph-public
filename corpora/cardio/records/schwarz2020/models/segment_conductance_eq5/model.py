import math


def run(inputs, settings):
    return {"G": math.pi * inputs["d"] ** 4 / (128 * inputs["mu"] * inputs["l"])}


def symbolic():
    import sympy as sp
    d, mu, l = sp.symbols("d mu l", positive=True)
    return {"G": sp.pi * d ** 4 / (128 * mu * l)}
