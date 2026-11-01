import math


def run(inputs, settings):
    # x = plog(gamma/e) with x = fc/N0, so gamma = e * x * exp(x)
    x = inputs["Fc"] / inputs["Fb"] / inputs["N0"]
    gamma = math.e * x * math.exp(x)
    return {"gamma": gamma, "kon": gamma * inputs["k0"]}


def symbolic():
    import sympy as sp
    Fc, Fb, N0, k0 = sp.symbols("Fc Fb N0 k0", positive=True)
    x = Fc / Fb / N0
    gamma = sp.E * x * sp.exp(x)
    return {"gamma": gamma, "kon": gamma * k0}
