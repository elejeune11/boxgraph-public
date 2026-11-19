import math


def run(inputs, settings):
    r = inputs["Ebar_over_Esbar"]
    return {
        "lam_over_h": 2 * math.pi * (r / 3) ** (1 / 3),
        "Nc_over_hE": 0.25 * (3 / r) ** (2 / 3),
        "amp_coeff": 1.0,
    }


def symbolic():
    import sympy as sp
    r = sp.symbols("Ebar_over_Esbar", positive=True)
    return {
        "lam_over_h": 2 * sp.pi * (r / 3) ** sp.Rational(1, 3),
        "Nc_over_hE": sp.Rational(1, 4) * (3 / r) ** sp.Rational(2, 3),
        "amp_coeff": sp.Integer(1),
    }
