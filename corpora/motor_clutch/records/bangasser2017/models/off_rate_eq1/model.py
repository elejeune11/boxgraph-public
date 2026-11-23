# Eq. 1: Bell slip-bond off-rate of one clutch, koff,i = k*off exp(Fc,i/Fb). Units: 1/s, pN.
import math


def run(inputs, settings):
    return {"koff_i": inputs["koff"] * math.exp(inputs["Fc"] / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, Fc, Fb = sp.symbols("koff Fc Fb", positive=True)
    return {"koff_i": koff * sp.exp(Fc / Fb)}
