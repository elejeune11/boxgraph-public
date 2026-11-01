import math


def run(inputs, settings):
    return {"t": (1 / inputs["k0"]) * math.exp(-inputs["F"] * inputs["xb"] / inputs["kT"])}


def symbolic():
    import sympy as sp
    k0, F, xb, kT = sp.symbols("k0 F xb kT", positive=True)
    return {"t": (1 / k0) * sp.exp(-F * xb / kT)}
