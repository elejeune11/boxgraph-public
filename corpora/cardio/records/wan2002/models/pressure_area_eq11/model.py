import math


def run(inputs, settings):
    r0 = inputs["r0"]
    eh_r0 = inputs["k1"] * math.exp(inputs["k2"] * r0) + inputs["k3"]
    S0 = math.pi * r0 * r0
    return {"p": inputs["p0"] + 4.0 / 3.0 * eh_r0 * (1.0 - math.sqrt(S0 / inputs["S"]))}


def symbolic():
    import sympy as sp
    k1, k3, r0, S = sp.symbols("k1 k3 r0 S", positive=True)
    k2, p0 = sp.symbols("k2 p0", real=True)
    return {"p": p0 + sp.Rational(4, 3) * (k1 * sp.exp(k2 * r0) + k3) * (1 - sp.sqrt(sp.pi * r0 ** 2 / S))}
