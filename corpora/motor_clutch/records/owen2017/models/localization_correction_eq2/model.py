# Supp. eqn. 2 as printed: s = sqrt(<d^2> - 4 sigma_xy^2 - 2 sigma_z^2).
import math


def run(inputs, settings):
    return {"s": math.sqrt(inputs["msd"] - 4.0 * inputs["sigma_xy"] ** 2 - 2.0 * inputs["sigma_z"] ** 2)}


def symbolic():
    import sympy as sp
    msd, sxy, sz = sp.symbols("msd sigma_xy sigma_z", positive=True)
    return {"s": sp.sqrt(msd - 4 * sxy**2 - 2 * sz**2)}
