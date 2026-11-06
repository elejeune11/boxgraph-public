import math


def run(inputs, settings):
    return {"koff_i": inputs["koff"] * math.exp(inputs["Fc"] / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, Fc, Fb = sp.symbols("koff Fc Fb", positive=True)
    return {"koff_i": koff * sp.exp(Fc / Fb)}
