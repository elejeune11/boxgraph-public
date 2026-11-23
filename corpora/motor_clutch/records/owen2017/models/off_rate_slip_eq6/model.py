# Supp. eqn. 6: Bell slip bond, koff = ks exp(F delta_s / kT). pN * nm / (pN nm) is dimensionless.
import math


def run(inputs, settings):
    return {"koff": inputs["ks"] * math.exp(inputs["F"] * inputs["delta_s"] / inputs["kT"])}


def symbolic():
    import sympy as sp
    ks, F, ds, kT = sp.symbols("ks F delta_s kT", positive=True)
    return {"koff": ks * sp.exp(F * ds / kT)}
