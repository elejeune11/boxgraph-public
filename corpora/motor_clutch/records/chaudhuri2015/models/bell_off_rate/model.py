import math


def run(inputs, settings):
    return {"koff_star": inputs["koff"] * math.exp(inputs["Fclutch"] / inputs["Frup"])}


def symbolic():
    import sympy as sp
    koff, Fclutch, Frup = sp.symbols("koff Fclutch Frup", positive=True)
    return {"koff_star": koff * sp.exp(Fclutch / Frup)}
