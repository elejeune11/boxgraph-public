import math


def run(inputs, settings):
    return {"coef": 2.0 * math.sqrt(inputs["c"])}


def symbolic():
    import sympy as sp
    c = sp.symbols("c", positive=True)
    return {"coef": 2 * sp.sqrt(c)}
