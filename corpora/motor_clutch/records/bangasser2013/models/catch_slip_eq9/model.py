# Eq. 9: catch-slip off-rate as the sum of two exponentials; lifetime under constant force = 1/koff*.
import math


def run(inputs, settings):
    F = inputs["F"]
    k = inputs["koff"] * math.exp(F / inputs["Fb"]) + inputs["koffc"] * math.exp(-F / inputs["Fc"])
    return {"koff_star": k, "tau": 1.0 / k}


def symbolic():
    import sympy as sp
    F, koff, Fb, koffc, Fc = sp.symbols("F koff Fb koffc Fc", positive=True)
    k = koff * sp.exp(F / Fb) + koffc * sp.exp(-F / Fc)
    return {"koff_star": k, "tau": 1 / k}
