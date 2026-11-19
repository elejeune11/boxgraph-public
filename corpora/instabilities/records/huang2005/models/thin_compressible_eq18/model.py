import math


def run(inputs, settings):
    r, Hh, nu = inputs["Ebar_over_Esbar"], inputs["H_over_h"], inputs["nu_s"]
    return {
        "lam_over_h": 2 * math.pi * (Hh * r * (1 - 2 * nu) / (12 * (1 - nu) ** 2)) ** 0.25,
        "Nc_over_hE": ((1 - nu) ** 2 / (3 * Hh * r * (1 - 2 * nu))) ** 0.5,
        "amp_coeff": math.sqrt(2 / 3),
    }


def symbolic():
    import sympy as sp
    r, Hh, nu = sp.symbols("Ebar_over_Esbar H_over_h nu_s", positive=True)
    return {
        "lam_over_h": 2 * sp.pi * (Hh * r * (1 - 2 * nu) / (12 * (1 - nu) ** 2)) ** sp.Rational(1, 4),
        "Nc_over_hE": sp.sqrt((1 - nu) ** 2 / (3 * Hh * r * (1 - 2 * nu))),
        "amp_coeff": sp.sqrt(sp.Rational(2, 3)),
    }
