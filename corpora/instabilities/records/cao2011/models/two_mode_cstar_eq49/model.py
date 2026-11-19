import math


def run(inputs, settings):
    return {"cstar": math.sqrt(3.0 * math.sqrt(3.0) * inputs["b112"] * inputs["c"] / 4.0)}


def symbolic():
    import sympy as sp
    b112, c = sp.symbols("b112 c", positive=True)
    return {"cstar": sp.sqrt(3 * sp.sqrt(3) * b112 * c / 4)}
