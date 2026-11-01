# roff = roff0 exp(Fc/Fb).  Ports: roff0 1/s, Fc pN, Fb pN -> roff 1/s.
import math


def run(inputs, settings):
    return {"roff": inputs["roff0"] * math.exp(inputs["Fc"] / inputs["Fb"])}


def symbolic():
    import sympy as sp
    roff0, Fc, Fb = sp.symbols("roff0 Fc Fb", positive=True)
    return {"roff": roff0 * sp.exp(Fc / Fb)}
