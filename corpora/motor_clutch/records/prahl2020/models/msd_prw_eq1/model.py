import math


def run(inputs, settings):
    n, S, P, t = inputs["n"], inputs["S"], inputs["P"], inputs["t"]
    return {"msd": n * S ** 2 * P ** 2 * (math.exp(-t / P) + t / P - 1.0)}


def symbolic():
    import sympy as sp
    n, S, P, t = sp.symbols("n S P t", positive=True)
    return {"msd": n * S ** 2 * P ** 2 * (sp.exp(-t / P) + t / P - 1)}
