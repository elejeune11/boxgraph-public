# c0^2 = (4/3) Eh/(rho r0) at A = A0, with Eh/r0 = k1 exp(k2 r0) + k3 (Eq. 6). CGS units.
import math


def run(inputs, settings):
    eh_r0 = inputs["k1"] * math.exp(inputs["k2"] * inputs["r0"]) + inputs["k3"]
    return {"c0": math.sqrt(4.0 / 3.0 * eh_r0 / inputs["rho"])}


def symbolic():
    import sympy as sp
    rho, k1, k3, r0 = sp.symbols("rho k1 k3 r0", positive=True)
    k2 = sp.Symbol("k2", real=True)
    return {"c0": sp.sqrt(sp.Rational(4, 3) * (k1 * sp.exp(k2 * r0) + k3) / rho)}
