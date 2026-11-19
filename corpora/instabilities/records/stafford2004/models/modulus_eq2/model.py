"""Eq. 2: Ef / (1 - nu_f^2) = 3 Es / (1 - nu_s^2) (d / 2 pi h)^3, solved for Ef.

Ports: d in um, h in nm, Es in MPa, Ef in GPa. d/h in um/nm is multiplied by 1e3;
Es in MPa is divided by 1e3 for GPa.
"""

import math


def run(inputs, settings):
    x = inputs["d"] * 1e3 / (2 * math.pi * inputs["h"])
    Ef = (1 - inputs["nu_f"] ** 2) * 3 * inputs["Es"] / 1e3 / (1 - inputs["nu_s"] ** 2) * x**3
    return {"Ef": Ef}


def symbolic():
    import sympy as sp

    d, h, nu_f, Es, nu_s = sp.symbols("d h nu_f Es nu_s", positive=True)
    x = d * 1000 / (2 * sp.pi * h)
    return {"Ef": (1 - nu_f**2) * 3 * Es / 1000 / (1 - nu_s**2) * x**3}
