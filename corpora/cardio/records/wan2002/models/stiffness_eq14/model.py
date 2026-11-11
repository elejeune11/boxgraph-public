import math


def run(inputs, settings):
    return {"Eh_r0": inputs["k1"] * math.exp(inputs["k2"] * inputs["r0"]) + inputs["k3"]}


def symbolic():
    import sympy as sp
    k1, k3, r0 = sp.symbols("k1 k3 r0", positive=True)
    k2 = sp.Symbol("k2", real=True)
    return {"Eh_r0": k1 * sp.exp(k2 * r0) + k3}
