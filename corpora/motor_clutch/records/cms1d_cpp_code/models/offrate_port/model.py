# Port of Cell1DPublish.cpp lines 575-578 and 614-618: Fc = clutch_k_ dx; rate = koff exp(|Fc| / Fb).
import math


def run(inputs, settings):
    return {"koff_i": inputs["koff"] * math.exp(abs(inputs["F"]) / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, F, Fb = sp.symbols("koff F Fb", positive=True)
    return {"koff_i": koff * sp.exp(F / Fb)}
