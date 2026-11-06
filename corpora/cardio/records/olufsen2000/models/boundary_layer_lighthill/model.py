import math


def run(inputs, settings):
    return {"delta": math.sqrt(inputs["nu"] * inputs["T"] / (2 * math.pi))}


def symbolic():
    import sympy as sp
    nu, T = sp.symbols("nu T", positive=True)
    return {"delta": sp.sqrt(nu * T / (2 * sp.pi))}
