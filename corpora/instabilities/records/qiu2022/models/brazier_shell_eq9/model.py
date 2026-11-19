# Eq. 9, shell normalization: the curvature at the maximum of Eq. 8, kappa-bar_B = sqrt(8/3 + 8 p-bar/9)
import math


def run(inputs, settings):
    return {"kbarB": math.sqrt(8 / 3 + 8 * inputs["pbar"] / 9)}


def symbolic():
    import sympy as sp
    pbar = sp.symbols("pbar", positive=True)
    return {"kbarB": sp.sqrt(sp.Rational(8, 3) + sp.Rational(8, 9) * pbar)}
