import math


def run(inputs, settings):
    n = settings.get("n", 1)
    S = math.pi * inputs["r"] ** 2
    # poise = g cm^-1 s^-1
    return {"R": 8 * math.pi * inputs["eta"] * n / S**2 * inputs["dz"]}


def symbolic():
    import sympy as sp
    eta, r, dz = sp.symbols("eta r dz", positive=True)
    return {"R": 8 * sp.pi * eta / (sp.pi * r**2) ** 2 * dz}
