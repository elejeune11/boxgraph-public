import math


def run(inputs, settings):
    x = 100 * (math.sqrt(inputs["k"]) - 1)
    return {"dZ": x, "dc": x}


def symbolic():
    import sympy as sp
    k = sp.symbols("k", positive=True)
    x = 100 * (sp.sqrt(k) - 1)
    return {"dZ": x, "dc": x}
