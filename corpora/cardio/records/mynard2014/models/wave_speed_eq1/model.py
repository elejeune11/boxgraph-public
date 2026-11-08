# Eq. 1: c0^2 = 2/(3 rho) [k1 exp(k2 r0) + k3], CGS units (the paper's units system, p. 5).
import math


def run(inputs, settings):
    s = inputs["k1"] * math.exp(inputs["k2"] * inputs["r0"]) + inputs["k3"]
    return {"c0": math.sqrt(2.0 / (3.0 * inputs["rho"]) * s)}


def symbolic():
    import sympy as sp
    rho, k1, k3, r0 = sp.symbols("rho k1 k3 r0", positive=True)
    k2 = sp.Symbol("k2", real=True)
    return {"c0": sp.sqrt(2 / (3 * rho) * (k1 * sp.exp(k2 * r0) + k3))}
