import math


def run(inputs, settings):
    # ln N0 + Gamma = T k0; the 1/(2 N0) term is below float resolution for the N0 this gives.
    # Returned as log10 N0, since N0 itself overflows a float.
    return {"N0": (inputs["T"] * inputs["k0"] - inputs["Gamma"]) / math.log(10)}


def symbolic():
    import sympy as sp
    T, k0, Gamma = sp.symbols("T k0 Gamma", positive=True)
    return {"N0": (T * k0 - Gamma) / sp.log(10)}
