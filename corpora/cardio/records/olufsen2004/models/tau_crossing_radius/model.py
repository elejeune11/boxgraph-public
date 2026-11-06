import math


def run(inputs, settings):
    return {"R": math.sqrt(inputs["nu"] / (2 * math.pi * inputs["HR"] * inputs["lam"]))}


def symbolic():
    import sympy as sp
    nu, hr, lam = sp.symbols("nu HR lam", positive=True)
    return {"R": sp.sqrt(nu / (2 * sp.pi * hr * lam))}
