# Eqs. 8 and 9 of the paper, solved for Hct_T: D in um, hematocrits dimensionless.
import math


def run(inputs, settings):
    H, D = inputs["HctD"], inputs["D"]
    X = 1 + 1.7 * math.exp(-0.35 * D) - 0.6 * math.exp(-0.01 * D)
    return {"HctT": H * (H + (1 - H) * X)}


def symbolic():
    import sympy as sp
    H, D = sp.symbols("HctD D", positive=True)
    X = 1 + sp.Rational(17, 10) * sp.exp(-sp.Rational(7, 20) * D) - sp.Rational(3, 5) * sp.exp(-sp.Rational(1, 100) * D)
    return {"HctT": H * (H + (1 - H) * X)}
