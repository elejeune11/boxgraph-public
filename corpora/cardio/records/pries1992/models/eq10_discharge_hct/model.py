# Eqs. 9 and 10 of the paper as printed: D in um, hematocrits dimensionless.
import math


def run(inputs, settings):
    HT, D = inputs["HctT"], inputs["D"]
    X = 1 + 1.7 * math.exp(-0.35 * D) - 0.6 * math.exp(-0.01 * D)
    a = X / (2 - 2 * X)
    return {"HctD": -a + (a**2 + HT / (1 - X)) ** 0.5}


def symbolic():
    import sympy as sp
    HT, D = sp.symbols("HctT D", positive=True)
    X = 1 + sp.Rational(17, 10) * sp.exp(-sp.Rational(7, 20) * D) - sp.Rational(3, 5) * sp.exp(-sp.Rational(1, 100) * D)
    a = X / (2 - 2 * X)
    return {"HctD": -a + sp.sqrt(a**2 + HT / (1 - X))}
