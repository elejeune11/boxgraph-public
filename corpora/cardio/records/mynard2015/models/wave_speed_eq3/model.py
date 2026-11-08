# Eq. 3: c0^2 = 2/(3 rho) [k1 exp(k2 D0/2) + k3]; cgs units throughout (g, cm, s).
import math


def run(inputs, settings):
    rho, k1, k2, k3, D0 = (inputs[k] for k in ("rho", "k1", "k2", "k3", "D0"))
    c0_sq = 2.0 / (3.0 * rho) * (k1 * math.exp(k2 * D0 / 2.0) + k3)
    return {"c0": math.sqrt(c0_sq)}


def symbolic():
    import sympy as sp
    rho, k1, k3, D0 = sp.symbols("rho k1 k3 D0", positive=True)
    k2 = sp.Symbol("k2", real=True)
    return {"c0": sp.sqrt(2 / (3 * rho) * (k1 * sp.exp(k2 * D0 / 2) + k3))}
