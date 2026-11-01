from math import comb


def run(inputs, settings):
    # Eq. 5 at tau -> infinity, i = 1: C(N0,1) gamma^1 * 1^(N0-1) / (1+gamma)^N0
    n0, g = int(round(inputs["N0"])), inputs["gamma"]
    return {"a": comb(n0, 1) * g / (1 + g) ** n0}


def symbolic():
    import sympy as sp
    N0, gamma = sp.symbols("N0 gamma", positive=True)
    return {"a": N0 * gamma / (1 + gamma) ** N0}
