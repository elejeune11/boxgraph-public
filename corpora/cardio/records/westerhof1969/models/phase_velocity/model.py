import math


def run(inputs, settings):
    return {"c": 1.0 / math.sqrt(inputs["Lp"] * inputs["Cp"])}


def symbolic():
    import sympy as sp
    Lp, Cp = sp.symbols("Lp Cp", positive=True)
    return {"c": 1 / sp.sqrt(Lp * Cp)}
