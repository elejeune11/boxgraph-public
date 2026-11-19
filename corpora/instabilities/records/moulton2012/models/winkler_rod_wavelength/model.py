# Reconstructed: wavelength of the first buckling mode of an inextensible elastic rod (bending
# stiffness EI) on a linear Winkler foundation (stiffness ks per unit length), straight-rod limit:
# lambda = 2 pi (EI / ks)^(1/4). The paper minimises E_f + E_b (Eqs. 7, 8) numerically and states
# no wavelength. Nondimensional units, as in Appendix F.
import math


def run(inputs, settings):
    return {"lam": 2.0 * math.pi * (inputs["EI"] / inputs["ks"]) ** 0.25}


def symbolic():
    import sympy as sp
    EI, ks = sp.symbols("EI ks", positive=True)
    return {"lam": 2 * sp.pi * (EI / ks) ** sp.Rational(1, 4)}
