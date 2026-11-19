"""Eq. 2 on each measured (h, d) point of Fig. 2b, returned at the thicknesses of the plotted moduli.

Ef_at is used only for its x values (the thicknesses at which the paper plots a modulus): each is paired with
the wavelength point nearest in thickness (within max_dh), and Eq. 2 is evaluated at that point's own
thickness and wavelength. Units as in modulus_eq2: d in um, h in nm, Es in MPa, Ef in GPa.
"""

import math


def _eq2(d, h, nu_f, Es, nu_s):
    x = d * 1e3 / (2 * math.pi * h)
    return (1 - nu_f**2) * 3 * Es / 1e3 / (1 - nu_s**2) * x**3


def run(inputs, settings):
    dh, dd = inputs["d"]["x"], inputs["d"]["y"]
    out = []
    for h in inputs["Ef_at"]["x"]:
        j = min(range(len(dh)), key=lambda k: abs(dh[k] - h))
        if abs(dh[j] - h) > settings["max_dh"]:
            out.append(None)
        else:
            out.append(_eq2(dd[j], dh[j], inputs["nu_f"], inputs["Es"], inputs["nu_s"]))
    return {"Ef": {"x": list(inputs["Ef_at"]["x"]), "y": out}}
