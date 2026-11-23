import math


def run(inputs, settings):
    return {"koff_i": inputs["koff"] * math.exp(inputs["Fclutch"] / inputs["Fbond"])}


def symbolic():
    import sympy as sp
    koff, Fclutch, Fbond = sp.symbols("koff Fclutch Fbond", positive=True)
    return {"koff_i": koff * sp.exp(Fclutch / Fbond)}
