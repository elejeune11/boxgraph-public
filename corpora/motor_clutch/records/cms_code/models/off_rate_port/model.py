# Port of cms2Dv1_0.m line 181 (our code): koff*exp(norm(Fc)/Fb). The norm of a scalar force is abs().
import math


def run(inputs, settings):
    return {"koff_i": inputs["koff"] * math.exp(abs(inputs["Fc"]) / inputs["Fb"])}


def symbolic():
    import sympy as sp
    koff, Fc, Fb = sp.symbols("koff Fc Fb", positive=True)
    return {"koff_i": koff * sp.exp(Fc / Fb)}
