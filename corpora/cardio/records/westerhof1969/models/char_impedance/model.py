import math


def run(inputs, settings):
    return {"Z0": math.sqrt(inputs["Lp"] / inputs["Cp"])}


def symbolic():
    import sympy as sp
    Lp, Cp = sp.symbols("Lp Cp", positive=True)
    return {"Z0": sp.sqrt(Lp / Cp)}
