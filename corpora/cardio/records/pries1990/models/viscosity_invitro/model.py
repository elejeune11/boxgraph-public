# Eqs. 2 and 3 as printed; D in um.
import math


def eta_rel(D, HD):
    alpha = 4 / (1 + math.exp(-0.593 * (D - 6.74)))
    return 1 + (math.exp(HD * alpha) - 1) / (math.exp(0.45 * alpha) - 1) * (
        110 * math.exp(-1.424 * D) + 3 - 3.45 * math.exp(-0.035 * D))


def run(inputs, settings):
    return {"eta_rel": eta_rel(inputs["D"], inputs["HD"])}


def symbolic():
    import sympy as sp
    D, HD = sp.symbols("D HD", positive=True)
    F = sp.Float
    alpha = 4 / (1 + sp.exp(-F("0.593") * (D - F("6.74"))))
    return {"eta_rel": 1 + (sp.exp(HD * alpha) - 1) / (sp.exp(F("0.45") * alpha) - 1)
            * (110 * sp.exp(-F("1.424") * D) + 3 - F("3.45") * sp.exp(-F("0.035") * D))}
