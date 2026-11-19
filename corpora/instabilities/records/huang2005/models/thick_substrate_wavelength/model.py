"""Eq. 17 solved for lambda_eq: lambda_eq = 2 pi h (E_bar / (3 Es_bar))^(1/3).

Ports: h in nm, lam in um (divide by 1e3).
"""

import math


def run(inputs, settings):
    r = inputs["Ebar_over_Esbar"]
    return {"lam": 2 * math.pi * inputs["h"] * (r / 3) ** (1 / 3) / 1e3}


def symbolic():
    import sympy as sp

    h, r = sp.symbols("h Ebar_over_Esbar", positive=True)
    return {"lam": 2 * sp.pi * h * (r / 3) ** sp.Rational(1, 3) / 1000}
