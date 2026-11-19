"""Eq. 19 solved for lambda_eq: lambda_eq = 2 pi h sqrt(H/h) (E_bar / (18 Es_bar))^(1/6).

Ports: h and lam in mm.
"""

import math


def run(inputs, settings):
    r, Hh = inputs["Ebar_over_Esbar"], inputs["H_over_h"]
    return {"lam": 2 * math.pi * inputs["h"] * math.sqrt(Hh) * (r / 18) ** (1 / 6)}


def symbolic():
    import sympy as sp

    h, Hh, r = sp.symbols("h H_over_h Ebar_over_Esbar", positive=True)
    return {"lam": 2 * sp.pi * h * sp.sqrt(Hh) * (r / 18) ** sp.Rational(1, 6)}
