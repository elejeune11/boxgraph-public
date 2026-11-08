# mynard2014 Eq. 1 (after Olufsen), in CGS units, with the uniform scaling to a target wave speed at
# the proximal Cx that the paper describes in words. r0 = D0/2.
import math


def _c0_unscaled(k1, k2, k3, rho, D):
    return math.sqrt(2.0 / (3.0 * rho) * (k1 * math.exp(k2 * D / 2.0) + k3))


def run(inputs, settings):
    k1, k2, k3, rho = inputs["k1"], inputs["k2"], inputs["k3"], inputs["rho"]
    scale = inputs["c_ref"] / _c0_unscaled(k1, k2, k3, rho, inputs["D_ref"])
    return {"c0": scale * _c0_unscaled(k1, k2, k3, rho, inputs["D0"])}


def symbolic():
    import sympy as sp
    k1, k3, rho, D0, D_ref, c_ref = sp.symbols("k1 k3 rho D0 D_ref c_ref", positive=True)
    k2 = sp.symbols("k2", real=True)

    def g(D):
        return sp.sqrt(2 / (3 * rho) * (k1 * sp.exp(k2 * D / 2) + k3))

    return {"c0": c_ref * g(D0) / g(D_ref)}
