# Eq. S26 as printed: P = P0 + (4/3)(Yh/r0)(1 - sqrt(S0/S)), Yh/r0 = k1 exp(k2 r0) + k3. CGS.
import math


def run(inputs, settings):
    yhr0 = inputs["k1"] * math.exp(inputs["k2"] * inputs["r0"]) + inputs["k3"]
    return {"P": inputs["P0"] + 4.0 / 3.0 * yhr0 * (1.0 - math.sqrt(inputs["S0"] / inputs["S"]))}


def symbolic():
    import sympy as sp
    k1, k3, r0, S0, S = sp.symbols("k1 k3 r0 S0 S", positive=True)
    k2, P0 = sp.symbols("k2 P0", real=True)
    yhr0 = k1 * sp.exp(k2 * r0) + k3
    return {"P": P0 + sp.Rational(4, 3) * yhr0 * (1 - sp.sqrt(S0 / S))}
