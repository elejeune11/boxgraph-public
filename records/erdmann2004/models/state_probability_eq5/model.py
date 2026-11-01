import math


def run(inputs, settings):
    n0, i = int(round(inputs["N0"])), int(round(inputs["i"]))
    g, e = inputs["gamma"], math.exp(-(1 + inputs["gamma"]) * inputs["tau"])
    return {"p": math.comb(n0, i) * (g + e) ** i * (1 - e) ** (n0 - i) / (1 + g) ** n0}


def symbolic():
    import sympy as sp
    N0, i, gamma, tau = sp.symbols("N0 i gamma tau", positive=True)
    e = sp.exp(-(1 + gamma) * tau)
    return {"p": sp.binomial(N0, i) * (gamma + e) ** i * (1 - e) ** (N0 - i) / (1 + gamma) ** N0}
