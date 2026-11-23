# k_off^load = k_off exp(|F_c| / F_b) (p. 2): 1/s, pN, pN -> 1/s.
import math


def run(inputs, settings):
    return {"koff_load": inputs["koff"] * math.exp(abs(inputs["Fc"]) / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, Fc, Fb = sp.symbols("koff Fc Fb", positive=True)
    return {"koff_load": koff * sp.exp(Fc / Fb)}
