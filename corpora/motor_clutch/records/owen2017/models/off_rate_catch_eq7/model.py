# Supp. eqn. 7: koff = ks exp(F delta_s / kT) + kc exp(-F delta_c / kT).
import math


def run(inputs, settings):
    F, kT = inputs["F"], inputs["kT"]
    return {"koff": inputs["ks"] * math.exp(F * inputs["delta_s"] / kT)
            + inputs["kc"] * math.exp(-F * inputs["delta_c"] / kT)}


def symbolic():
    import sympy as sp
    ks, kc, F, ds, dc, kT = sp.symbols("ks kc F delta_s delta_c kT", positive=True)
    return {"koff": ks * sp.exp(F * ds / kT) + kc * sp.exp(-F * dc / kT)}
