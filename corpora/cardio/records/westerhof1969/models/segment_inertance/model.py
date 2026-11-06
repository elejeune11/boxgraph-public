import math


def run(inputs, settings):
    n = settings.get("n", 1)
    S = math.pi * inputs["r"] ** 2
    lp = inputs["rho"] / S / (2 * n - 1)
    return {"L": lp * inputs["dz"], "Lp": lp}


def symbolic():
    import sympy as sp
    rho, r, dz = sp.symbols("rho r dz", positive=True)
    lp = rho / (sp.pi * r**2)
    return {"L": lp * dz, "Lp": lp}
