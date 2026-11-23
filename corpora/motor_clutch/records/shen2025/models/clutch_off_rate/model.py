import math


def run(inputs, settings):
    return {"koff": inputs["koff0"] * math.exp(inputs["flc"] / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff0, flc, Fb = sp.symbols("koff0 flc Fb", positive=True)
    return {"koff": koff0 * sp.exp(flc / Fb)}
