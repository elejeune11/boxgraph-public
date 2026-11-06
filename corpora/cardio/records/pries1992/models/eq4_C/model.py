# Eq. 4 of the paper: D in um, output dimensionless.
import math


def run(inputs, settings):
    D = inputs["D"]
    s = 1.0 / (1.0 + 1e-11 * D**12)
    return {"C": (0.8 + math.exp(-0.075 * D)) * (-1.0 + s) + s}


def symbolic():
    import sympy as sp
    D = sp.symbols("D", positive=True)
    s = 1 / (1 + sp.Rational(1, 10**11) * D**12)
    return {"C": (sp.Rational(4, 5) + sp.exp(-sp.Rational(3, 40) * D)) * (-1 + s) + s}
