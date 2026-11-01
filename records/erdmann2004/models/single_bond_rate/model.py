import math


def run(inputs, settings):
    return {"k": inputs["k0"] * math.exp(inputs["F"] / (inputs["i"] * inputs["Fb"]))}


def symbolic():
    import sympy as sp
    k0, F, i, Fb = sp.symbols("k0 F i Fb", positive=True)
    return {"k": k0 * sp.exp(F / (i * Fb))}
