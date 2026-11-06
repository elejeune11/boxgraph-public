# Eq. 8 as printed, its left-hand side Hct_T/Hct_D as the output: D in um, hematocrit dimensionless.
import math


def run(inputs, settings):
    H, D = inputs["HctD"], inputs["D"]
    return {"HctT_HctD": H + (1 - H) * (1 + 1.7 * math.exp(-0.35 * D) - 0.6 * math.exp(-0.01 * D))}


def symbolic():
    import sympy as sp
    H, D = sp.symbols("HctD D", positive=True)
    X = 1 + sp.Rational(17, 10) * sp.exp(-sp.Rational(7, 20) * D) - sp.Rational(3, 5) * sp.exp(-sp.Rational(1, 100) * D)
    return {"HctT_HctD": H + (1 - H) * X}
