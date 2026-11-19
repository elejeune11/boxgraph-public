"""Eq. 1: d = 2 pi h [(1 - nu_s^2) Ef / (3 (1 - nu_f^2) Es)]^(1/3).

Ports: h in nm, Ef in GPa, Es in MPa, d in um. Ef/Es in GPa/MPa is multiplied by 1e3;
h in nm gives d in nm, divided by 1e3 for um.
"""

import math


def run(inputs, settings):
    ratio = (1 - inputs["nu_s"] ** 2) * inputs["Ef"] * 1e3 / (3 * (1 - inputs["nu_f"] ** 2) * inputs["Es"])
    return {"d": 2 * math.pi * inputs["h"] * ratio ** (1.0 / 3.0) / 1e3}


def symbolic():
    import sympy as sp

    h, Ef, nu_f, Es, nu_s = sp.symbols("h Ef nu_f Es nu_s", positive=True)
    ratio = (1 - nu_s**2) * Ef * 1000 / (3 * (1 - nu_f**2) * Es)
    return {"d": 2 * sp.pi * h * ratio ** sp.Rational(1, 3) / 1000}
