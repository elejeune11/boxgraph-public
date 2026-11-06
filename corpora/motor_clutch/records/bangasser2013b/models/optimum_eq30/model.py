# Eq. 30: kappa_s,opt = Fm nm kon / (vu ln(nc)) * ln(1/eps). Fm pN, vu nm/s, kon 1/s -> pN/nm.
import math


def run(inputs, settings):
    p = inputs
    return {"ks_opt": p["Fm"] * p["nm"] * p["kon"] / (p["vu"] * math.log(p["nc"])) * math.log(1 / p["eps"])}


def symbolic():
    import sympy as sp
    Fm, nm, kon, vu, nc, eps = sp.symbols("Fm nm kon vu nc eps", positive=True)
    return {"ks_opt": Fm * nm * kon / (vu * sp.log(nc)) * sp.log(1 / eps)}
