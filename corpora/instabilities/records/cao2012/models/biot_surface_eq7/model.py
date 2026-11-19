import math


def run(inputs, settings):
    return {"eW": 1 - inputs["c"] / math.sqrt(inputs["lam3"])}


def symbolic():
    import sympy as sp
    c, lam3 = sp.symbols("c lam3", positive=True)
    return {"eW": 1 - c / sp.sqrt(lam3)}
