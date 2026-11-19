import math


def run(inputs, settings):
    r, Hh = inputs["Ebar_over_Esbar"], inputs["H_over_h"]
    return {
        "lam_over_h": 2 * math.pi * math.sqrt(Hh) * (r / 18) ** (1 / 6),
        "Nc_over_hE": (1 / (4 * Hh)) * (9 / (4 * r)) ** (1 / 3),
        "amp_coeff": math.sqrt(0.5),
    }


def symbolic():
    import sympy as sp
    r, Hh = sp.symbols("Ebar_over_Esbar H_over_h", positive=True)
    return {
        "lam_over_h": 2 * sp.pi * sp.sqrt(Hh) * (r / 18) ** sp.Rational(1, 6),
        "Nc_over_hE": (1 / (4 * Hh)) * (sp.Rational(9, 4) / r) ** sp.Rational(1, 3),
        "amp_coeff": sp.sqrt(sp.Rational(1, 2)),
    }
