import math


def run(inputs, settings):
    return {"v": 2 * math.pi * inputs["nu"] * inputs["A"]}


def symbolic():
    import sympy as sp
    nu, A = sp.symbols("nu A", positive=True)
    return {"v": 2 * sp.pi * nu * A}
