import math


def run(inputs, settings):
    return {"tau": (1 / inputs["HR"]) * inputs["nu"] / (2 * math.pi * inputs["R"] ** 2)}


def symbolic():
    import sympy as sp
    nu, hr, r = sp.symbols("nu HR R", positive=True)
    return {"tau": (1 / hr) * nu / (2 * sp.pi * r**2)}
