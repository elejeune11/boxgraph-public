import math


def run(inputs, settings):
    # Sign convention of Table S1: Fclutch and Fb are both negative, so their ratio is positive.
    return {"koff_star": inputs["koff"] * math.exp(inputs["Fclutch"] / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, Fclutch, Fb = sp.symbols("koff Fclutch Fb", positive=True)
    return {"koff_star": koff * sp.exp(Fclutch / Fb)}
